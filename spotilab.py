from datetime import datetime
from typing import Literal, Tuple
import numpy as np
import pandas as pd
from spotidf import (
    SpotifyClient,
)


def _genre_in_list(track_genres: list[str] | None, test_genres: list[str]):
    if track_genres is None or len(track_genres) == 0:
        if "NONE" in test_genres:
            return True
        return False
    for test_genre in test_genres:
        if test_genre in track_genres:
            return True
    return False


def _genres(
    track_genres: list[str] | None, artist_genres: list[str] | None, album_genres: list[str] | None
) -> list[str]:
    genres = set[str]()
    if track_genres is not None and isinstance(track_genres, np.ndarray):
        genres.update(track_genres)
    if artist_genres is not None and isinstance(artist_genres, np.ndarray):
        genres.update(artist_genres)
    if album_genres is not None and isinstance(album_genres, np.ndarray):
        genres.update(album_genres)
    return list(genres)


def _fix_name_for_dupes(_track) -> str:
    """Adjust the name of the track so that it's easier to check for dupes"""
    name = _track["name"]
    if (
        " mix" in name.lower()
        or " instrumental" in name.lower()
        or " acoustic" in name.lower()
        or " remix" in name.lower()
        or " version" in name.lower()
        or "- pt." in name.lower()
        or "part " in name.lower()
        or " live" in name.lower()
        or " reprise" in name.lower()
        or " continued" in name.lower()
        or " <>" in name.lower()
        or " suite" in name.lower()
        or " bbc" in name.lower()
        or "rmx" in name.lower()
    ):
        return name
    return name.split(" - ")[0]


class Spotilab:
    def __init__(self):
        self._client = SpotifyClient()

    def fetch_library(self, cache_only=False) -> pd.DataFrame:
        self._lib = self._client.fetch_library_dataframe(cache_only)
        return self._lib

    def _exclude_playlists(self, df: pd.DataFrame, exclude_playlists: list[str], dirty_cache=False):
        if exclude_playlists is None or len(exclude_playlists) == 0:
            return df
        uris = set(
            [
                uri
                for playlist_name in exclude_playlists
                for uri in self._client.fetch_playlist_track_uris(playlist_name, dirty_cache)
            ]
        )
        mask = df["track_uri"].isin(uris)
        df = df.loc[~mask]
        return df

    def _include_playlists(self, df: pd.DataFrame, include_playlists: list[str]):
        tracks = set[str]()
        if include_playlists is None or len(include_playlists) == 0:
            return df
        uris = set(
            [
                uri
                for playlist_name in include_playlists
                for uri in self._client.fetch_playlist_track_uris(playlist_name)
            ]
        )
        mask = df["track_uri"].isin(uris)
        df = df.loc[mask]
        return df

    def update_playlist(
        self,
        playlist_name: str,
        new_tracks_df: pd.DataFrame | None = None,
        exclude_holiday=True,
        exclude_noise=False,
        added_after=None,
        released_between: Tuple[datetime | None, datetime | None] | None = None,
        sort_key: Literal[
            "energy",
            "popularity",
            "danceability",
            "valence",
            "acousticness",
            "instrumentalness",
            "liveness",
            "speechiness",
            "loudness",
            "tempo",
            None,
        ] = None,
        sort_ascending=False,
        limit: int | None = None,
        artists: list[str] | None = None,
        artists_like: list[str] | None = None,
        albums: list[str] | None = None,
        tracks: list[str] | None = None,
        include_genres: list[str] | None = None,
        include_playlists: list[str] | None = None,
        exclude_genres: list[str] | None = None,
        update_cache: bool = False,
        exclude_playlists=[],
    ):
        new_tracks_df = self._lib if new_tracks_df is None else new_tracks_df

        excluding = [*(exclude_playlists or [])]

        if include_playlists is not None and len(include_playlists) > 0:
            new_tracks_df = self._include_playlists(new_tracks_df, include_playlists)
        if exclude_holiday:
            excluding.append("Holiday Songs")
        if exclude_noise or added_after is not None:
            excluding.append("Noise")
        new_tracks_df = self._exclude_playlists(new_tracks_df, excluding, update_cache)

        new_tracks_df.loc[:, "genres"] = new_tracks_df.apply(
            lambda row: _genres(row["genres"], row["album_genres"], row["genres_artist1"]), axis=1
        )
        if include_genres is not None and len(include_genres) > 0:
            mask = new_tracks_df["genres"].apply(lambda genres: _genre_in_list(genres, include_genres))
            new_tracks_df = new_tracks_df[mask]
        if exclude_genres is not None and len(exclude_genres) > 0:
            mask = new_tracks_df["genres"].apply(lambda genres: _genre_in_list(genres, exclude_genres))
            new_tracks_df = new_tracks_df[~mask]

        if released_between is not None:
            new_tracks_df = (
                new_tracks_df.loc[(new_tracks_df["release_date"] >= released_between[0])]
                if released_between[0] is not None
                else new_tracks_df
            )
            new_tracks_df = (
                new_tracks_df.loc[(new_tracks_df["release_date"] < released_between[1])]
                if released_between[1] is not None
                else new_tracks_df
            )
        if added_after is not None:
            new_tracks_df = new_tracks_df.loc[
                (new_tracks_df["added_at"] >= added_after.isoformat())
                & (new_tracks_df["added_at"] > datetime(year=2023, month=6, day=8, hour=3, minute=30).isoformat())
            ]

        if artists is not None and len(artists) > 0:
            # filter the new_tracks_df dataframe to only include rows where the artist or artist_1 column is in the artists list
            new_tracks_df = new_tracks_df[
                new_tracks_df["artist"].isin(artists) | new_tracks_df["artist_1"].isin(artists)
            ]
        print(f" Excludng  {len(new_tracks_df)}: ", excluding)

        if albums is not None and len(albums) > 0:
            new_tracks_df = pd.concat([new_tracks_df, self._lib[(self._lib["album"].isin(albums))]])

        if tracks is not None and len(tracks) > 0:
            new_tracks_df = pd.concat([new_tracks_df, self._lib[(self._lib["name"].isin(tracks))]])

        if sort_key is not None:
            new_tracks_df = new_tracks_df.sort_values(by=[sort_key, "added_at"], ascending=sort_ascending)
        if limit is not None:
            new_tracks_df = new_tracks_df.head(limit)
        if artists_like is not None and len(artists_like) > 0:
            print(f"Artists like: {artists_like} with length of new_tracks_df: {len(new_tracks_df)} ")
            artists_df = self._lib[(self._lib["artist"].isin(artists_like))]
            artists_ids = artists_df["artist_id"].to_list()
            artists_like_res = [self._client.fetch_artists_like(id).get("artists", []) for id in artists_ids]
            artists_like_names = [r["name"] for sublist in artists_like_res for r in sublist]
            # return the 2 most popular tracks for each artist in the names list from the dataframe in _lib
            subart = [
                self._lib[(self._lib["artist"] == name) | (self._lib["artist_1"] == name)]
                for name in artists_like_names
            ]
            top5 = [suba.sort_values("popularity", ascending=False).head(2) for suba in subart]
            # new_tracks_df = self._lib[(self._lib["artist"].isin(artists_like_names)) | (self._lib["artist_1"].isin(artists_like_names))]
            new_tracks_df = pd.concat([new_tracks_df] + top5)
        return self._client.update_playlist(self._lib, playlist_name, new_tracks_df, update_cache)

    def fetch_track_uris(self, playlist_name: str, dirty_cache=False):
        return self._client.fetch_playlist_track_uris(playlist_name, dirty_cache)

    def get_library_duplicates(self) -> pd.DataFrame:
        """Get a DataFrame of duplicate tracks in the user's library"""
        # check the library dataframe for duplicates based on the song title and artist name
        duplicates = self._lib[self._lib.duplicated(subset=["name", "artist"], keep=False)]
        print(duplicates.head(30))
        return duplicates
