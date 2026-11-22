import json
import logging
import os
import threading
import time
import webbrowser
from datetime import datetime
from itertools import groupby
from queue import Empty, Queue
from typing import Any, List, TypedDict
from urllib.parse import urlparse

import pandas as pd
from flask import Flask, request
from werkzeug.serving import make_server
from spotipy import Spotify
from spotipy.cache_handler import CacheFileHandler
from spotipy.oauth2 import SpotifyOAuth, SpotifyPKCE

# This is not a secret - don't worry
SPOTILAB_REDIRECT_URI = "http://127.0.0.1:8000/hub/oauth_callback"
CONFIG_ROOT = (
    f"{os.environ.get('HOME',os.environ.get('HOMEPATH','.'))}{os.sep}.spotilab"
)


class TrackUriPositions(TypedDict):
    uri: str
    positions: List[int]


client_id = os.environ.get("SPOTIPY_CLIENT_ID", "")
redirect_uri = os.environ.get("SPOTIPY_REDIRECT_URI", SPOTILAB_REDIRECT_URI)
scope = [
    "user-read-private",
    "user-read-email",
    "playlist-modify-public",
    "playlist-modify-private",
    "user-library-read",
    "user-library-read",
    "user-library-modify",
    "playlist-read-private",
    "playlist-read-collaborative",
]


class SpotifyOAuthCallbackServer(threading.Thread):
    """Run a minimal Flask server to capture Spotify's OAuth callback."""

    def __init__(self, host: str, port: int, path: str, result_queue: Queue):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.path = path
        self._result_queue = result_queue
        self._ready_event = threading.Event()

        self.app = Flask(__name__)

        @self.app.route(self.path, methods=["GET"])
        def callback():  # type: ignore[valid-type]
            error = request.args.get("error")
            if error:
                self._result_queue.put({"error": error})
            else:
                self._result_queue.put(
                    {
                        "code": request.args.get("code"),
                        "state": request.args.get("state"),
                    }
                )
            return (
                "<html><body><h1>Authorization complete</h1>"
                "<p>You can close this window and return to the application.</p>"
                "</body></html>"
            )

        self._server = make_server(self.host, self.port, self.app)
        self._ctx = self.app.app_context()
        self._ctx.push()

    def run(self) -> None:
        self._ready_event.set()
        self._server.serve_forever()

    def wait_until_ready(self, timeout: float = 5.0) -> None:
        self._ready_event.wait(timeout)

    def shutdown(self) -> None:
        self._server.shutdown()
        self._ctx.pop()


class SpotifyClient:
    def __init__(self) -> None:
        self.logger = logging.getLogger("spotidf.spotify_client")
        os.makedirs(CONFIG_ROOT, exist_ok=True)

        if not client_id:
            raise RuntimeError("SPOTIPY_CLIENT_ID must be set in the environment")

        self.cache_path = f"{CONFIG_ROOT}{os.sep}.spotilab_token.json"
        cache_handler = CacheFileHandler(cache_path=self.cache_path)

        self.auth_manager = SpotifyPKCE(
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=" ".join(scope),
            cache_handler=cache_handler,
            open_browser=False,
        )

        self._ensure_token_available()

        self._spotify = Spotify(auth_manager=self.auth_manager)
        self._playlists_cache = self.fetch_playlists()

    def _normalize_track_id_for_lookup(self, track_identifier: str) -> str:
        """Return a bare Spotify track ID for saved-track lookup calls."""
        if track_identifier.startswith("spotify:track:"):
            return track_identifier.split(":")[-1]

        if track_identifier.startswith("http://") or track_identifier.startswith(
            "https://"
        ):
            parsed = urlparse(track_identifier)
            if parsed.path.startswith("/track/"):
                return parsed.path.split("/")[-1]

        return track_identifier

    def _normalize_artist_id_for_lookup(self, artist_identifier: Any) -> str | None:
        """Return a bare Spotify artist ID, or None if identifier is invalid."""
        if not isinstance(artist_identifier, str):
            return None

        artist_identifier = artist_identifier.strip()
        if not artist_identifier:
            return None

        if artist_identifier.startswith("spotify:artist:"):
            return artist_identifier.split(":")[-1]

        if artist_identifier.startswith("http://") or artist_identifier.startswith(
            "https://"
        ):
            parsed = urlparse(artist_identifier)
            if parsed.path.startswith("/artist/"):
                return parsed.path.split("/")[-1]

        return artist_identifier

    def _ensure_token_available(self) -> dict[str, Any]:
        token_info = self.auth_manager.cache_handler.get_cached_token()
        token_info = self.auth_manager.validate_token(token_info)

        if token_info is None:
            token_info = self._run_authorization_flow(self.auth_manager)

        if token_info is None:
            raise RuntimeError("Unable to obtain Spotify authorization token")

        return token_info

    def _run_authorization_flow(
        self, auth_manager: SpotifyPKCE, timeout: int = 180
    ) -> dict[str, Any]:
        parsed_uri = urlparse(redirect_uri)
        host = parsed_uri.hostname or "127.0.0.1"
        port = parsed_uri.port or 8000
        path = parsed_uri.path or "/callback"

        result_queue: Queue = Queue()
        callback_server = SpotifyOAuthCallbackServer(host, port, path, result_queue)
        callback_server.start()
        callback_server.wait_until_ready()

        auth_url = auth_manager.get_authorize_url()
        print("Starting Spotify authorization flow...")
        print(f"If your browser doesn't open automatically, visit:\n{auth_url}\n")

        if not self._open_authorization_url(auth_url):
            self.logger.warning("Unable to open browser automatically")
            if self._is_ssh_or_headless_session():
                print(
                    "Detected SSH/headless session. Open the URL above in a desktop browser. "
                    "If needed, forward callback port 8000 with: ssh -L 8000:127.0.0.1:8000 <host>"
                )

        try:
            result = result_queue.get(timeout=timeout)
        except Empty as exc:
            raise TimeoutError("Spotify authorization timed out") from exc
        finally:
            callback_server.shutdown()

        error = result.get("error")
        if error:
            raise RuntimeError(f"Spotify authorization failed: {error}")

        code = result.get("code")
        if not code:
            raise RuntimeError(
                "Spotify authorization failed: missing authorization code"
            )

        auth_manager.get_access_token(code, check_cache=False)
        token_info = auth_manager.cache_handler.get_cached_token()
        if not token_info:
            raise RuntimeError(
                "Spotify authorization failed to return token information"
            )

        return token_info

    def _open_authorization_url(self, auth_url: str) -> bool:
        """Open Spotify auth URL in a real desktop browser where possible."""
        if self._is_ssh_or_headless_session():
            return False

        if os.name == "nt":
            try:
                os.startfile(auth_url)  # type: ignore[attr-defined]
                return True
            except OSError:
                pass

            try:
                webbrowser.get("windows-default").open(auth_url, new=2)
                return True
            except webbrowser.Error:
                pass

        try:
            return bool(webbrowser.open(auth_url, new=2, autoraise=True))
        except webbrowser.Error:
            return False

    def _is_ssh_or_headless_session(self) -> bool:
        if os.environ.get("SSH_CONNECTION") or os.environ.get("SSH_TTY"):
            return True

        if os.name != "nt" and not (
            os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
        ):
            return True

        return False

    def _get_library_tracks(self, cache_only=False):
        # Set up the SpotifyOAuth object
        library = f"{CONFIG_ROOT}{os.sep}mytracks.parquet"
        # Get the user's library tracks
        library_df: pd.DataFrame = pd.DataFrame(
            columns=[
                "track_id",
                "track_uri",
                "name",
                "artist",
                "artist_id",
                "artist_1",
                "artist_id_1",
                "album",
                "album_id",
                "added_at",
                "popularity",
                "original_id",
                "original_uri",
            ]
        )
        stop_tracks: List[str] | None = None
        if os.path.exists(library):
            library_df = pd.read_parquet(library)
            if cache_only:
                return library_df
            stop_tracks = list(set(library_df["track_id"].tolist()))
        results = self._spotify.current_user_saved_tracks(limit=50, market="US")
        if results is not None:
            print(
                f"Loading Library. Spotify reports library size of: {results['total']}"
            )
        stopped = False
        while results is not None and not stopped:
            page: List[dict[str, Any]] = []
            for item in results["items"]:
                track = item["track"]
                if stop_tracks is not None and track["id"] in stop_tracks:
                    stopped = True
                    break
                row = {
                    "track_id": track["id"],
                    "track_uri": track["uri"],
                    "name": track["name"],
                    "artist": track["artists"][0]["name"],
                    "artist_id": track["artists"][0]["id"],
                    "artist_1": (
                        track["artists"][1]["name"]
                        if len(track["artists"]) > 1
                        else None
                    ),
                    "artist_id_1": (
                        track["artists"][1]["id"] if len(track["artists"]) > 1 else None
                    ),
                    "album": track["album"]["name"],
                    "album_id": track["album"]["id"],
                    "added_at": item["added_at"],
                    "popularity": track["popularity"],
                    "original_id": track.get("linked_from", {}).get("id", None),
                    "original_uri": track.get("linked_from", {}).get("uri", None),
                    "duration_ms": track.get("duration_ms", 0),
                }
                page.append(row)
            library_df = pd.concat([library_df, pd.DataFrame(page)])
            if results["next"] is None:
                break
            results = self._spotify.next(results)

        to_delete = set()
        all_track_ids = library_df["track_id"].to_list()  # list(all_track_ids_set)
        all_track_set = set(library_df["track_id"].to_list())  # list(all_track_ids_set)
        # Keep a conservative page size and normalize URI values to track IDs.
        # This avoids 400 errors from Spotify when cached values include full URIs.
        for track_id_page in [
            all_track_ids[i : i + 20] for i in range(0, len(all_track_ids), 20)
        ]:
            lookup_ids = [
                self._normalize_track_id_for_lookup(track_id)
                for track_id in track_id_page
            ]
            tracks_contains_response = self._spotify.current_user_saved_tracks_contains(
                lookup_ids
            )
            to_delete.update(
                [
                    track_id_page[index]
                    for index, track_contained in enumerate(tracks_contains_response)
                    if track_contained == False
                ]
            )
        # # print the name, artist of the first 100 tracks to be deleted
        print(
            f"Wanting to Delete {len(to_delete)} tracks from library: {len(library_df)}"
        )
        if len(to_delete) > 0:
            mask = library_df["track_id"].isin(to_delete)
            print(f"Deleting {len(to_delete)} tracks from library: {len(library_df)}")
            library_df = library_df.loc[~mask]

        print(
            f"Loaded {len(all_track_ids)}/{len(all_track_set)} (tracks/unique IDs) from library"
        )
        library_df = library_df.drop_duplicates(keep="first")

        library_df.to_parquet(library)
        return library_df

    def _get_albums(self, album_id_set: set[str], cache_only=False):
        cache_file_path = f"{CONFIG_ROOT}{os.sep}myalbums.parquet"
        df: pd.DataFrame = pd.DataFrame(
            columns=["album_id", "release_date", "album_type"]
        )
        if os.path.exists(cache_file_path):
            df = pd.read_parquet(cache_file_path)
            if cache_only:
                return df
        for id in df["album_id"].to_list():
            if id in album_id_set:
                album_id_set.remove(id)
        album_ids = list(album_id_set)
        if (len(album_ids)) == 0:
            return df
        print(f"Reading {len(album_ids)} albums from Spotify")
        # Get the user's library tracks
        for chunks in [album_ids[i : i + 20] for i in range(0, len(album_ids), 20)]:
            results = self._spotify.albums(chunks, market="US")
            page: List[dict[str, Any]] = []
            if results is None:
                continue
            for item in results["albums"]:
                release_date = datetime.strptime(
                    str(item["release_date"]),
                    (
                        "%Y"
                        if (item["release_date_precision"] == "year")
                        else (
                            "%Y-%m"
                            if (item["release_date_precision"] == "month")
                            else "%Y-%m-%d"
                        )
                    ),
                )
                row = {
                    "album_id": item["id"],
                    "release_date": pd.to_datetime(release_date).floor("D"),
                    "album_type": item["album_type"],
                    "album_genres": item["genres"],
                }
                page.append(row)
            if len(page) > 0:
                new_albums_df = pd.DataFrame(page)
                df["release_date"] = df["release_date"].apply(
                    lambda x: pd.to_datetime(x).floor("D")
                )
                df = pd.concat([df, new_albums_df], ignore_index=True)
        df.to_parquet(cache_file_path)
        return df

    # def _get_features(self, ids: set[str], cache_only: bool):
    #     """Get the audio features for the tracks in the user's library, fetching what is missing."""
    #     # Set up the SpotifyOAuth object
    #     os.makedirs(CONFIG_ROOT, exist_ok=True)
    #     features_cache_path = f"{CONFIG_ROOT}{os.sep}features.parquet"
    #     df: pd.DataFrame = pd.DataFrame()
    #     if os.path.exists(features_cache_path):
    #         df = pd.read_parquet(features_cache_path)
    #         if cache_only:
    #             return df
    #         # df.drop("release_date", axis=1, inplace=True)
    #     if not df.empty:
    #         for id in df["track_id"].to_list():
    #             if id in ids:
    #                 ids.remove(id)
    #     track_ids = list(ids)
    #     if (len(track_ids)) == 0:
    #         return df
    #     print(f"Reading {len(track_ids)} features from Spotify")
    #     # Get the user's library tracks
    #     for chunks in [track_ids[i : i + 100] for i in range(0, len(track_ids), 100)]:
    #         results = self._spotify.audio_features(chunks)
    #         features_list: List[dict[str, Any]] = []
    #         if results is None:
    #             continue
    #         for item in results:
    #             if item is None:
    #                 continue
    #             feature = {
    #                 "track_id": item["id"],
    #                 "loudness": item["loudness"],
    #                 "tempo": item["tempo"],
    #                 "danceability": item["danceability"],
    #                 "energy": item["energy"],
    #                 "valence": item["valence"],
    #                 "acousticness": item["acousticness"],
    #                 "instrumentalness": item["instrumentalness"],
    #                 "liveness": item["liveness"],
    #                 "speechiness": item["speechiness"],
    #                 "time_signature": item["time_signature"],
    #                 "minor": item["mode"] == 1,
    #                 "key": item["key"],
    #                 "valence": item["valence"],
    #                 "duration_ms": item["duration_ms"],
    #             }
    #             features_list.append(feature)
    #         print(f"\tRead {len(df)}")
    #         df = pd.concat([df, pd.DataFrame(features_list)])
    #     df.to_parquet(features_cache_path)
    #     return df

    def _get_artists(self, ids: set[str], cache_only: bool):
        """Get the audio artists for the tracks in the user's library, fetching what is missing."""
        # Set up the SpotifyOAuth object
        os.makedirs(CONFIG_ROOT, exist_ok=True)
        clean_ids = {
            artist_id
            for artist_id in (
                self._normalize_artist_id_for_lookup(artist_identifier)
                for artist_identifier in ids
            )
            if artist_id is not None
        }
        artists_cache_path = f"{CONFIG_ROOT}{os.sep}artists.parquet"
        df: pd.DataFrame = pd.DataFrame()
        if os.path.exists(artists_cache_path):
            df = pd.read_parquet(artists_cache_path)
            if cache_only:
                return df
            # df.drop("release_date", axis=1, inplace=True)
        if not df.empty:
            for artist_identifier in df["artist_id"].to_list():
                cached_artist_id = self._normalize_artist_id_for_lookup(
                    artist_identifier
                )
                if cached_artist_id in clean_ids:
                    clean_ids.remove(cached_artist_id)
        artist_ids = list(clean_ids)
        if (len(artist_ids)) == 0:
            return df
        print(f"Reading {len(artist_ids)} artists from Spotify")
        # Get the user's library tracks
        for chunks in [artist_ids[i : i + 50] for i in range(0, len(artist_ids), 50)]:
            results = self._spotify.artists(chunks)
            artist_list: List[dict[str, Any]] = []
            if results is None:
                continue
            for item in results["artists"]:
                artist = {
                    "artist_id": item["id"],
                    "genres": item["genres"],
                    "popularity": item["popularity"],
                    "followers": item["followers"]["total"],
                    "artist_uri": item["uri"],
                }
                artist_list.append(artist)
            print(f"\tRead {len(df)}")
            df = pd.concat([df, pd.DataFrame(artist_list)])
        df.to_parquet(artists_cache_path)
        return df

    def fetch_artists_like(self, artist_uri: str):
        res = self._spotify.artist_related_artists(artist_uri)
        return res

    def fetch_library_dataframe(self, cache_only: bool):
        df = self._get_library_tracks(cache_only)
        # print length of df
        album_ids_set = set(df["album_id"].to_list())
        albums = self._get_albums(album_ids_set, cache_only)
        df = pd.merge(df, albums, left_on="album_id", right_on="album_id", how="left")
        # Read the Features
        # features = self._get_features(set(df["track_id"].to_list()), cache_only)
        # df = pd.merge(df, features, left_on="track_id", right_on="track_id", how="left")
        # create a single set from columns artist_id and artist_id_1 in dataframe df
        artists_set = set(df["artist_id_1"].to_list())
        artists_set.update(df["artist_id"].to_list())
        artists = self._get_artists(artists_set, cache_only)
        df = pd.merge(
            df,
            artists,
            left_on="artist_id",
            right_on="artist_id",
            how="left",
            suffixes=("", "_artist"),
        )
        df = pd.merge(
            df,
            artists,
            left_on="artist_id_1",
            right_on="artist_id",
            how="left",
            suffixes=("", "_artist1"),
        )
        return df

    def _add_tracks(self, playlist_id: str, uris: List[str]):
        clean_uris = [uri for uri in uris if isinstance(uri, str) and uri]
        for chunks in [clean_uris[i : i + 100] for i in range(0, len(clean_uris), 100)]:
            self._spotify.playlist_add_items(playlist_id, chunks, position=0)

    def _delete_tracks(self, playlist_id: str, uris: List[str]):
        clean_uris = [uri for uri in uris if isinstance(uri, str) and uri]
        for chunks in [clean_uris[i : i + 100] for i in range(0, len(clean_uris), 100)]:
            x = self._spotify.playlist_remove_all_occurrences_of_items(
                playlist_id, chunks
            )

    def _delete_duplicates_uris(self, playlist_id: str, uri: str, original_uri: str):
        clean_uri = uri if isinstance(uri, str) and uri else None
        clean_original_uri = (
            original_uri if isinstance(original_uri, str) and original_uri else None
        )

        if clean_uri is None:
            self.logger.warning(
                "Skipping duplicate delete for playlist %s due to invalid URI: %r",
                playlist_id,
                uri,
            )
            return

        uris = [clean_uri]
        if clean_original_uri is not None and clean_original_uri != clean_uri:
            uris.append(clean_original_uri)

        x = self._spotify.playlist_remove_all_occurrences_of_items(playlist_id, uris)
        x = self._spotify.playlist_add_items(playlist_id, [clean_uri], position=0)

    def _create_playlist(self, name: str, description: str):
        print(f"Creating playlist {name}")
        user_id = self._spotify.me()["id"]
        self._spotify.user_playlist_create(
            user=user_id, name=name, description=description, public=True
        )
        return self._fetch_named_playlist(name, force_update=True)

    def fetch_playlists(self) -> List[dict[str, Any]]:
        """
        Fetches the user's playlists from Spotify and returns a list of dictionaries containing information about each playlist.

        Args:
            access_token (str): The user's Spotify access token.

        Returns:
            List[dict[str, Any]]: A list of dictionaries containing information about each playlist, including the playlist's
            name, ID, and other metadata.
        """
        results = self._spotify.current_user_playlists()
        items = results["items"]
        while results is not None and results["next"]:
            results = self._spotify.next(results)
            items.extend(results["items"])
        return items

    def _fetch_playlist_tracks(
        self, playlist_name: str, dirty_cache=False
    ) -> pd.DataFrame | None:
        playlist = self._fetch_named_playlist(playlist_name, force_update=dirty_cache)
        if playlist is None:
            print(f"Couldn't find playlist {playlist_name}")
            return None
        snapshot_id = playlist["snapshot_id"]
        if playlist["tracks"]["total"] == 0:
            return pd.DataFrame()
        os.makedirs(CONFIG_ROOT, exist_ok=True)
        playlist_cache_path = f"{CONFIG_ROOT}{os.sep}{playlist_name}.parquet"
        df: pd.DataFrame = pd.DataFrame()
        if os.path.exists(playlist_cache_path):
            df = pd.read_parquet(playlist_cache_path)
            if (
                not dirty_cache
                and len(df) > 0
                and df["snapshot_id"].iloc[0] == snapshot_id
            ):
                return df
        print(f"\tFetching tracks for {playlist_name}")
        results = self._spotify.playlist_tracks(playlist["id"], market="US")
        tracks = results["items"]
        while results is not None and results["next"]:
            results = self._spotify.next(results)
            tracks.extend(results["items"])

        data: List[dict[str, Any]] = []
        for item in tracks:
            track = item["track"]
            data.append(
                {
                    "snapshot_id": snapshot_id,
                    "track_id": track["id"],
                    "name": track["name"],
                    "track_uri": track["uri"],
                    "original_id": track.get("linked_from", {}).get("id", None),
                    "original_uri": track.get("linked_from", {}).get("uri", None),
                    "added_at": item["added_at"],
                }
            )
        df = pd.DataFrame(data)
        print("\tUpdating Playlist cache")
        df.to_parquet(playlist_cache_path)
        return df

    def _fetch_named_playlist(self, playlist_name: str, force_update=False):
        if force_update:
            self._playlists_cache = self.fetch_playlists()
        _playlists = self._playlists_cache
        if _playlists is None:
            raise ValueError("No playlists found")
        return next(
            (playlist for playlist in _playlists if playlist["name"] == playlist_name),
            None,
        )

    def fetch_playlist_track_uris(
        self, playlist_name: str, dirty_cache=False
    ) -> set[str]:
        tracks_df = self._fetch_playlist_tracks(playlist_name, dirty_cache)
        return set([] if tracks_df.empty else tracks_df["track_uri"].values.tolist())

    def update_playlist(
        self,
        lib: pd.DataFrame,
        playlist_name: str,
        new_tracks_df: pd.DataFrame,
        description: str = None,
        dedupe: bool = True,
        update_cache: bool = False,
    ) -> pd.DataFrame:
        target_tracks = set(new_tracks_df["track_uri"].values.tolist())
        linked_target_tracks = set(new_tracks_df["original_uri"].values.tolist())
        print(f"Updating {playlist_name} with {len(target_tracks)}")
        try:
            playlist = self._fetch_named_playlist(playlist_name)
            if playlist is None:
                playlist = self._create_playlist(
                    name=playlist_name,
                    description=description or f"Generated {playlist_name}",
                )
            existing_tracks_df = self._fetch_playlist_tracks(playlist_name)
            existing_tracks_original = (
                set(existing_tracks_df["original_uri"].values.tolist())
                if existing_tracks_df is not None and len(existing_tracks_df) > 0
                else set([])
            )
            existing_tracks = set([])
            if existing_tracks_df is not None and not existing_tracks_df.empty:
                existing_tracks = existing_tracks_df["track_uri"].values.tolist()
            # Go through the exclude playlist list, fetch the original URIs and filter out the tracks
            updated_playlist = False
            # only delete the track if it isn't in the target_tracks or the linked_target_tracks
            uris_to_del = [uri for uri in existing_tracks if uri not in target_tracks]
            uris_to_del = [
                uri for uri in uris_to_del if uri not in linked_target_tracks
            ]
            if len(uris_to_del) > 0:
                df_to_del = lib[(lib["track_uri"].isin(uris_to_del))]
                names_to_del = df_to_del["name"].values.tolist()[:4]
                del_tracks = ",".join(names_to_del)
                print(
                    f"\t{playlist_name}: deleting {len(uris_to_del)} Tracks: {del_tracks}"
                )
                self._delete_tracks(playlist["id"], uris_to_del)
                updated_playlist = True
            # add any track URI from target_tracks if it isn't in the existing_tracks or the existing_tracks_original
            uris_to_add = [uri for uri in target_tracks if uri not in existing_tracks]
            uris_to_add = [
                uri for uri in uris_to_add if uri not in existing_tracks_original
            ]

            if len(uris_to_add) > 0:
                df_to_add = lib[(lib["track_uri"].isin(uris_to_add))]
                names_to_add = df_to_add["name"].values.tolist()[:4]
                adding_tracks = ",".join(names_to_add)
                print(
                    f"\t{playlist_name}: adding {len(uris_to_add)} Tracks: {adding_tracks}"
                )
                self._add_tracks(playlist["id"], uris_to_add)
                updated_playlist = True
            print(
                f"\tDedupe: {dedupe} Update Cache: {update_cache} Updated Playlist: {updated_playlist}"
            )
            if (dedupe or update_cache) and updated_playlist:
                self._delete_duplicates(playlist_name, playlist["id"])
            if updated_playlist and update_cache:
                self._fetch_playlist_tracks(playlist_name, dirty_cache=True)
            return new_tracks_df
        except:
            print(f"Error Processing Update to Playlist: {playlist_name}")
            raise

    def _delete_duplicates(self, playlist_name: str, playlist_id: str):
        print(f"Checking for Duplicates in {playlist_name}/{playlist_id}")

        existing = self._fetch_playlist_tracks(playlist_name, dirty_cache=True)
        if existing.empty:
            return existing

        # Get a boolean mask for all rows that are duplicates (excluding the first occurrence)
        mask = existing.duplicated(subset="track_uri", keep="last")

        # Apply the mask to the DataFrame to get only the duplicate rows
        duplicates = existing[mask]

        # # get a list of 'track_uri' values from the filtered DataFrame
        track_uris = duplicates[["track_uri", "original_uri"]].values.tolist()

        # Convert list of lists to list of tuples, add to set to remove duplicates, then convert back to list of lists
        track_uris = [list(i) for i in set(tuple(i) for i in track_uris)]
        if len(track_uris) > 0:
            for i in track_uris:
                self._delete_duplicates_uris(playlist_id, i[0], i[1])
            return existing
        else:
            return existing
