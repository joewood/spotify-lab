from datetime import datetime
from itertools import groupby
import json
import multiprocessing
import time
from typing import Any, List
from spotipy import SpotifyPKCE, Spotify, prompt_for_user_token, SpotifyClientCredentials
import os
import pandas as pd

# This is not a secret - don't worry
SPOTILAB_REDIRECT_URI = "http://localhost:8000/hub/oauth_callback"
CONFIG_ROOT = f"{os.environ.get('HOME',os.environ.get('HOMEPATH','.'))}{os.sep}.spotilab"

import os
from flask import Flask, request
from spotipy import Spotify
from spotipy.oauth2 import SpotifyPKCE


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


def authorize_spotify(authorization_queue: multiprocessing.Queue, auth_manager: SpotifyPKCE) -> None:
    print(f"client_id {client_id} red: {redirect_uri}")

    def callback():
        auth_code = request.args.get("code")
        authorization_queue.put(auth_code)
        return "Done", 200

    app = Flask(__name__)
    app.add_url_rule("/hub/oauth_callback", "callback", callback)
    app.run(port=8000)


# Define the path to the credentials file

# Check if the credentials file exists


class SpotifyClient:
    def __init__(self) -> None:
        self._token = self.get_auth_token()
        self._spotify = Spotify(auth=self._token)
        self._playlists_cache = self.fetch_playlists()
        os.makedirs(CONFIG_ROOT, exist_ok=True)

    def get_auth_token(self) -> str | None:
        spotify_pkce = SpotifyPKCE(
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope,
        )
        os.makedirs(CONFIG_ROOT, exist_ok=True)
        creds_file = f"{CONFIG_ROOT}{os.sep}.spotilab.ini"
        if os.path.exists(creds_file):
            # Open the credentials file for reading
            with open(creds_file, "r") as f:
                # Read the cached credentials from the file
                code = f.read()
            return spotify_pkce.get_access_token(code)

        authorization_queue = multiprocessing.Queue()
        authorization_process = multiprocessing.Process(
            target=authorize_spotify, args=(authorization_queue, spotify_pkce)
        )
        authorization_process.start()

        auth_url = spotify_pkce.get_authorize_url()
        print(f"Please visit this URL to authorize the application: {auth_url}")
        code = authorization_queue.get(block=True)
        spotify_pkce.get_access_token(code)
        authorization_process.terminate()
        with open(creds_file, "w") as f:
            f.write(code)
        return spotify_pkce.get_access_token(code)

    def _get_library_tracks(self, cache_only=False):
        # Set up the SpotifyOAuth object
        library = f"{CONFIG_ROOT}{os.sep}mytracks.parquet"
        # Get the user's library tracks
        df: pd.DataFrame = pd.DataFrame(
            columns=[
                "id",
                "name",
                "artist",
                "album",
                "popularity",
                "album_id",
                "added_at",
                "original_id",
                "original_uri",
            ]
        )
        stop_tracks: List[str] | None = None
        if os.path.exists(library):
            df = pd.read_parquet(library)
            if cache_only:
                return df
            stop_tracks = set(df["id"].tolist())
        results = self._spotify.current_user_saved_tracks(limit=50, market="US")
        if results is not None:
            print(f"Loading Library. Spotify reports library size of: {results['total']}")
        stopped = False
        while results is not None and not stopped:
            page: List[dict[str, Any]] = []
            for item in results["items"]:
                track = item["track"]
                original_id = track.get("linked_from_id", track["id"])
                original_uri = track.get("linked_from_uri", track["uri"])
                if stop_tracks is not None and track["id"] in stop_tracks:
                    stopped = True
                    break
                row = {
                    "id": track["id"],
                    "uri": track["uri"],
                    "name": track["name"],
                    "artist": track["artists"][0]["name"],
                    "artist_id": track["artists"][0]["id"],
                    "artist_1": track["artists"][1]["name"] if len(track["artists"]) > 1 else None,
                    "artist_id_1": track["artists"][1]["id"] if len(track["artists"]) > 1 else None,
                    "album": track["album"]["name"],
                    "album_id": track["album"]["id"],
                    "added_at": item["added_at"],
                    "popularity": track["popularity"],
                    "original_id": original_id,
                    "original_uri": original_uri,
                }
                page.append(row)
            df = pd.concat([df, pd.DataFrame(page)])
            if results["next"] is None:
                break
            results = self._spotify.next(results)

        all_track_ids = df["id"].to_list()
        all_del = set()
        for chunks in [all_track_ids[i : i + 50] for i in range(0, len(all_track_ids), 50)]:
            tracks_contains_response = self._spotify.current_user_saved_tracks_contains(chunks)
            to_del = [
                chunks[index]
                for index, track_contained in enumerate(tracks_contains_response)
                if track_contained == False
            ]
            for o in to_del:
                all_del.add(o)
        if len(all_del) > 0:
            mask = df["id"].isin(all_del)
            print(f"Deleting {len(all_del)} tracks from library: {len(df)}")
            df = df.loc[~mask]

        print(f"Size of library before Duplicate Check {len(df)}")
        duplicates = df.groupby("original_uri").filter(lambda x: len(x) > 1)
        if len(duplicates) > 0:
            urii = duplicates["original_uri"].to_list()
            print(f"Found {len(duplicates)} duplicates")
            for chunks in [urii[i : i + 50] for i in range(0, len(urii), 50)]:
                print(f"\t\tChunk ")
                self._spotify.current_user_saved_tracks_delete(tracks=chunks)
                self._spotify.current_user_saved_tracks_add(tracks=chunks)

        df = df.drop_duplicates()
        df.to_parquet(library)
        return df

    def _get_albums(self, album_id_set: set[str], cache_only=False):
        cache_file_path = f"{CONFIG_ROOT}{os.sep}myalbums.parquet"
        df: pd.DataFrame = pd.DataFrame(columns=["id", "release_date", "album_type"])
        if os.path.exists(cache_file_path):
            df = pd.read_parquet(cache_file_path)
            if cache_only:
                return df
        for id in df["id"].to_list():
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
                    "%Y"
                    if (item["release_date_precision"] == "year")
                    else "%Y-%m"
                    if (item["release_date_precision"] == "month")
                    else "%Y-%m-%d",
                )
                row = {
                    "id": item["id"],
                    "release_date": pd.to_datetime(release_date).floor("D"),
                    "album_type": item["album_type"],
                    "album_genres": item["genres"]
                }
                page.append(row)  
            new_albums_df = pd.DataFrame(page)
            df["release_date"] = df["release_date"].apply(lambda x : pd.to_datetime(x).floor("D"))
            print("added:", new_albums_df.dtypes)
            print("added:", df.dtypes)
            df = pd.concat([df, new_albums_df], ignore_index=True)
        df.to_parquet(cache_file_path)
        return df

    def _get_features(self, ids: set[str], cache_only: bool):
        """Get the audio features for the tracks in the user's library, fetching what is missing."""
        # Set up the SpotifyOAuth object
        os.makedirs(CONFIG_ROOT, exist_ok=True)
        features_cache_path = f"{CONFIG_ROOT}{os.sep}features.parquet"
        df: pd.DataFrame = pd.DataFrame()
        if os.path.exists(features_cache_path):
            df = pd.read_parquet(features_cache_path)
            if cache_only:
                return df
            # df.drop("release_date", axis=1, inplace=True)
        if not df.empty:
            for id in df["id"].to_list():
                if id in ids:
                    ids.remove(id)
        track_ids = list(ids)
        if (len(track_ids)) == 0:
            return df
        print(f"Reading {len(track_ids)} features from Spotify")
        # Get the user's library tracks
        for chunks in [track_ids[i : i + 100] for i in range(0, len(track_ids), 100)]:
            results = self._spotify.audio_features(chunks)
            features_list: List[dict[str, Any]] = []
            if results is None:
                continue
            for item in results:
                feature = {
                    "id": item["id"],
                    "loudness": item["loudness"],
                    "tempo": item["tempo"],
                    "danceability": item["danceability"],
                    "energy": item["energy"],
                    "valence": item["valence"],
                    "acousticness": item["acousticness"],
                    "instrumentalness": item["instrumentalness"],
                    "liveness": item["liveness"],
                    "speechiness": item["speechiness"],
                    "time_signature": item["time_signature"],
                    "minor": item["mode"] == 1,
                    "key": item["key"],
                    "valence": item["valence"],
                    "duration_ms": item["duration_ms"],
                }
                features_list.append(feature)
            print(f"\tRead {len(df)}")
            df = pd.concat([df, pd.DataFrame(features_list)])
        df.to_parquet(features_cache_path)
        return df

    def _get_artists(self, ids: set[str], cache_only: bool):
        """Get the audio artists for the tracks in the user's library, fetching what is missing."""
        # Set up the SpotifyOAuth object
        os.makedirs(CONFIG_ROOT, exist_ok=True)
        if None in ids:
            ids.remove(None)
        artists_cache_path = f"{CONFIG_ROOT}{os.sep}artists.parquet"
        df: pd.DataFrame = pd.DataFrame()
        if os.path.exists(artists_cache_path):
            df = pd.read_parquet(artists_cache_path)
            if cache_only:
                return df
            # df.drop("release_date", axis=1, inplace=True)
        if not df.empty:
            for id in df["id"].to_list():
                if id in ids:
                    ids.remove(id)
        artist_ids = list(ids)
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
                    "id": item["id"],
                    "genres": item["genres"],
                    "popularity": item["popularity"],
                    "followers": item["followers"]["total"],
                    "uri": item["uri"],
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
        album_ids_set = set(df["album_id"].to_list())
        albums = self._get_albums(album_ids_set, cache_only)
        df = pd.merge(df, albums, left_on="album_id", right_on="id", how="left")
        # Read the Features
        features = self._get_features(set(df["original_id"].to_list()), cache_only)
        df = pd.merge(df, features, left_on="original_id", right_on="id", how="left")
        # create a single set from columns artist_id and artist_id_1 in dataframe df
        artists_set = set(df["artist_id_1"].to_list())
        artists_set.update(df["artist_id"].to_list())

        artists = self._get_artists(artists_set, cache_only)
        df = pd.merge(df, artists, left_on="artist_id", right_on="id", how="left", suffixes=("", "_artist"))
        df = pd.merge(df, artists, left_on="artist_id_1", right_on="id", how="left", suffixes=("", "_artist1"))

        return df

    def _add_tracks(self, playlist_id: str, uris: List[str]):
        for chunks in [uris[i : i + 100] for i in range(0, len(uris), 100)]:
            self._spotify.playlist_add_items(playlist_id, chunks, position=0)

    def _delete_tracks(self, playlist_id: str, uris: List[str]):
        for chunks in [uris[i : i + 100] for i in range(0, len(uris), 100)]:
            bodylist = [{"uri": x} for x in chunks]
            self._spotify.playlist_remove_all_occurrences_of_items(playlist_id, chunks)

    def _create_playlist(self, name: str, description: str):
        print(f"Creating playlist {name}")
        user_id = self._spotify.me()["id"]
        self._spotify.user_playlist_create(user=user_id, name=name, description=description, public=True)
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

    def _fetch_playlist_tracks(self, playlist_name: str, dirty_cache=False) -> pd.DataFrame | None:
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
            if not dirty_cache and len(df) > 0 and df["snapshot_id"].iloc[0] == snapshot_id:
                return df
        print(f"\tFetching tracks for {playlist_name}")
        results = self._spotify.playlist_tracks(playlist["id"])
        tracks = results["items"]
        while results is not None and results["next"]:
            results = self._spotify.next(results)
            tracks.extend(results["items"])

        data: List[dict[str, Any]] = []
        for item in tracks:
            track = item["track"]
            original_id = track.get("linked_from_id", track["id"])
            original_uri = track.get("linked_from_uri", track["uri"])
            data.append(
                {
                    "snapshot_id": snapshot_id,
                    "track_id": track["id"],
                    "name": track["name"],
                    "track_uri": track["uri"],
                    "original_id": original_id,
                    "original_uri": original_uri,
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
        return next((playlist for playlist in _playlists if playlist["name"] == playlist_name), None)

    def fetch_playlist_track_uris(self, playlist_name: str) -> set[str]:
        tracks_df = self._fetch_playlist_tracks(playlist_name, False)
        return set([] if tracks_df.empty else tracks_df["original_uri"].values.tolist())

    def update_playlist(
        self,
        lib: pd.DataFrame,
        playlist_name: str,
        new_tracks_df: pd.DataFrame,
        description: str = None,
        dedupe: bool = True,
        update_cache: bool = False
    ) -> pd.DataFrame:
        target_tracks = set(new_tracks_df["original_uri"].values.tolist())
        target_tracks_t = set(lib[(lib["original_uri"].isin(target_tracks))]["id"].values.tolist())
        try:
            playlist = self._fetch_named_playlist(playlist_name)
            if playlist is None:
                playlist = self._create_playlist(
                    name=playlist_name, description=description or f"Generated {playlist_name}"
                )
            existing_tracks_df = self._fetch_playlist_tracks(playlist_name)

            existing_tracks = set([])
            if existing_tracks_df is not None and not existing_tracks_df.empty:
                existing_tracks = existing_tracks_df["original_uri"].values.tolist()
            # Go through the exclude playlist list, fetch the original URIs and filter out the tracks
            updated_playlist = False
            uris_to_del = [uri for uri in existing_tracks if uri not in target_tracks]
            if len(uris_to_del) > 0:
                df_to_del = lib[(lib["original_uri"].isin(uris_to_del))]
                names_to_del = df_to_del["name"].values.tolist()[:4]
                del_tracks = ",".join(names_to_del)
                print(f"\t{playlist_name}: deleting {len(uris_to_del)} Tracks: {del_tracks}")
                self._delete_tracks(playlist["id"], uris_to_del)
                updated_playlist = True
            uris_to_add = [uri for uri in target_tracks if uri not in existing_tracks]
            if len(uris_to_add) > 0:
                df_to_add = lib[(lib["original_uri"].isin(uris_to_add))]
                names_to_add = df_to_add["name"].values.tolist()[:4]
                adding_tracks = ",".join(names_to_add)
                print(f"\t{playlist_name}: adding {len(uris_to_add)} Tracks: {adding_tracks}")
                self._add_tracks(playlist["id"], uris_to_add)
                updated_playlist = True
            if (dedupe or update_cache) and updated_playlist :
                self._delete_duplicates(playlist_name)
            # if updated_playlist:
            #     self._fetch_playlist_tracks(playlist_name, dirty_cache=True)
            return new_tracks_df
        except:
            print(f"Error Processing Update to Playlist: {playlist_name}")
            raise

    def _delete_duplicates(self, playlist_id: str):
        existing = self._fetch_playlist_tracks(playlist_id, dirty_cache=True)
        if existing.empty:
            return existing
        # group the DataFrame by 'original_uri' and filter the groups with more than one row
        duplicates = existing.groupby("original_uri").filter(lambda x: len(x) > 1)

        # get a list of 'track_uri' values from the filtered DataFrame
        track_uris = duplicates["track_uri"].tolist()
        if len(track_uris) > 0:
            print(f"\tDeleting {len(track_uris)} With Duplicates")
            self._delete_tracks(playlist_id, track_uris)
            return existing
        else:
            return existing
