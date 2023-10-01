from datetime import datetime
from typing import Literal, Tuple
import pandas as pd
from spotidf import (
    SpotifyClient,
)


class Spotilab:
    def __init__(self):
        self._client = SpotifyClient()

    def fetch_library(self):
        self._lib = self._client.fetch_library_dataframe()
        return self._lib

    def _exclude_playlists(self, df: pd.DataFrame, exclude_playlists: list[str]):
        uris = set(
            [
                uri
                for playlist_name in exclude_playlists
                for uri in self._client.fetch_playlist_track_uris(playlist_name)
            ]
        )
        mask = df["original_uri"].isin(uris)
        df = df.loc[~mask]
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
        exclude_playlists=[],
    ):
        new_tracks_df = self._lib if new_tracks_df is None else new_tracks_df
        excluding = [*exclude_playlists]
        if exclude_holiday:
            excluding.append("Holiday Songs")
        if exclude_noise or added_after is not None:
            excluding.append("Noise")
        new_tracks_df = self._exclude_playlists(new_tracks_df, excluding)

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
        if artists is not None:
            new_tracks_df = new_tracks_df.loc[
                (new_tracks_df["artist"].isin(artists)) | (new_tracks_df["artist_1"].isin(artists))
            ]
        if albums is not None:
            new_tracks_df = new_tracks_df.loc[(new_tracks_df["album"].isin(albums))]
        if tracks is not None:
            new_tracks_df = pd.concat([new_tracks_df,self._lib[(self._lib["name"].isin(tracks))]])

        if sort_key is not None:
            new_tracks_df = new_tracks_df.sort_values(by=[sort_key, "added_at"], ascending=sort_ascending)
        if limit is not None:
            new_tracks_df = new_tracks_df.head(limit)
        if artists_like is not None:
            artists_df = self._lib[(self._lib["artist"].isin(artists_like))]
            artists_ids = artists_df["artist_id"].to_list()
            artists_like_res = [self._client.fetch_artists_like(id).get("artists", []) for id in artists_ids]
            artists_like_names = [r["name"] for sublist in artists_like_res for r in sublist]
            # return the 5 most popular tracks for each artist in the names list from the dataframe in _lib
            subart =  [self._lib[(self._lib["artist"]==name) | (self._lib["artist_1"]==name)] for name in artists_like_names]
            top5 = [suba.sort_values('popularity', ascending=False).head(5) for suba in subart]
            # new_tracks_df = self._lib[(self._lib["artist"].isin(artists_like_names)) | (self._lib["artist_1"].isin(artists_like_names))]
            new_tracks_df = pd.concat([new_tracks_df] + top5) 
        print(f"Updating {playlist_name} with {len(new_tracks_df)} tracks, excluding {','.join(excluding)}")
        return self._client.update_playlist(self._lib, playlist_name, new_tracks_df)

    def fetch_track_uris(self, playlist_name: str):
        return self._client.fetch_playlist_track_uris(playlist_name)

    def get_library_duplicates(self) -> pd.DataFrame:
        """Get a DataFrame of duplicate tracks in the user's library"""
        # check the library dataframe for duplicates based on the song title and artist name
        duplicates = self._lib[self._lib.duplicated(subset=["name", "artist"], keep=False)]
        print(duplicates.head(30))
        return duplicates
