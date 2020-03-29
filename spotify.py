import requests
import json
import logging
import pandas as pd
from pandas.io.json import json_normalize
from typing import List, Set, Dict, Tuple, Optional
from itertools import groupby
import math
import numpy as np
from pandas import DataFrame, read_pickle, merge
from pandas import DataFrame as df
from datetime import datetime, timedelta, date
import os
import sys


def urlParams(**kwargs):
    d = map(lambda f: "{k}={v}".format(k=f[0], v=f[1]), kwargs.items())
    return "&".join(list(d))


class Spotify:
    auth = None
    userId: str = None
    imageUrl: str = None
    user = None
    market: str = None
    logger: None

    def __init__(self, auth, logger=logging.getLogger()):
        self.auth = auth
        self.logger = logger
        self.user = self.fetch("/v1/me")
        self.userId = self.user["id"]
        self.imageUrl = self.user["images"][0]["url"]
        self.market = self.user["country"]
        logger.debug("Initialized Spotify: {0} @ {1}".format(self.userId, self.market))
        self.fetch("/v1/me/tracks", limit=1, market=self.market)

    def fetch(self, path: str, url: str = None, **kwargs) -> json:
        args = urlParams(**kwargs)
        callPath = url or "https://api.spotify.com{path}{args}".format(
            path=path, args=("?" + args) if (len(args) > 0) else ""
        )
        response = requests.get(
            callPath, headers={"Authorization": "Bearer " + self.auth.access_token}
        )
        if not response.ok:
            self.logger.error(
                "error {0}: {1}".format(response.status_code, response.text)
            )
            response.raise_for_status()
        return response.json()

    def post(self, path, body, url: str = None) -> json:
        callPath = url if (url != None) else ("https://api.spotify.com" + path)
        response = requests.post(
            callPath,
            headers={"Authorization": "Bearer " + self.auth.access_token},
            data=json.dumps(body),
        )
        if not response.ok:
            self.logger.error(
                "error {0}: {1}".format(response.status_code, response.text)
            )
            response.raise_for_status()
        return response.json()

    def delete(self, path: str, body, url=None):
        callPath = url if (url != None) else ("https://api.spotify.com" + path)
        response = requests.delete(
            callPath,
            headers={"Authorization": "Bearer " + self.auth.access_token},
            data=json.dumps(body),
        )
        if not response.ok:
            self.logger.error(
                "error {0}: {1}".format(response.status_code, response.text)
            )
            response.raise_for_status()
        return response.json()

    def fetchAll(self, path: str, stopTrackId: List[str] = None, **kwargs):
        items = []
        more: json = None
        while True:
            more_ = (
                self.fetch(path, offset=0, limit=50, **kwargs)
                if (more is None)
                else self.fetch(None, url=more["next"])
            )
            more = more_
            # if a stop track id was specified then scan for it
            if stopTrackId != None:
                index = 0
                for item in more["items"]:
                    # check for track ID, if we hit it then grab the subset and return
                    if item["track"]["id"] in stopTrackId:
                        if index > 0:
                            items.extend(more["items"][0:index])
                        self.logger.info(
                            "Incremental Update. Added {0} items.".format(len(items))
                        )
                        return items
                    index = index + 1
            items.extend(more["items"])
            if more["next"] is None:
                break
        # self.logger.info("more {0}".format(more["next"]))
        return items

    def fetchPageIds(self, path, ids, **kwargs):
        return self.fetch(path=path, ids=",".join(ids), **kwargs)

    def fetchAllIds(
        self,
        path: str,
        ids: List[str],
        resultField: str = None,
        pageSize=50,
        existingDf=None,
        asArray=False,
        **kwargs
    ):
        if existingDf is not None:
            keys = list(existingDf.index.values)
            ids = list(filter(lambda id: (id not in keys), ids))
            existingDf = existingDf.reset_index()
        total = len(ids)
        #        self.logger.info(
        #            "Requesting {0} rows. {1} ... {2}".format(ids, path, resultField)
        #        )
        # self.logger.info(
        #     "DF size {0}".format(0 if existingDf is None else len(existingDf))
        # )
        offset = 0
        allItems = []
        while offset < total:
            try:
                result = self.fetchPageIds(
                    path, ids=ids[offset : min(total, offset + pageSize)], **kwargs
                )
                try:
                    if (resultField is not None) and (resultField not in result):
                        self.logger.error(
                            "Key not in results: {0}".format(result.keys())
                        )
                        raise Exception("Cannot find key in results")
                    items = result[resultField] if (resultField is not None) else result
                    # Some Audio Features returning null, filter these out as json_normalize fails for null records
                    items = list(filter(lambda x: x is not None, items))
                    # self.logger.info("Returned {0} not null rows".format(len(items)))
                    if asArray:
                        allItems = allItems + items
                    else:
                        items = json_normalize(items)
                        existingDf = (
                            items
                            if (existingDf is None)
                            else existingDf.append(items, ignore_index=True, sort=True)
                        )
                    offset += pageSize
                except:
                    self.logger.error("Cannot Parse: " + result)
                    raise
            except Exception as err:
                self.logger.error(err)
                # self.logger.error(
                #     "Cannot query skipping: " + (",".join(ids[offset: min(total, offset + pageSize)])))
                offset += pageSize
                raise
        # self.logger.info(
        #     "DF size after {0}".format(0 if existingDf is None else len(existingDf))
        # )
        return allItems if asArray else existingDf.to_dict(orient="records")

    def checkDeletes(self, trackIds: List[str]):
        saved = self.fetchAllIds(
            "/v1/me/tracks/contains", trackIds, asArray=True, market=self.market
        )
        # self.logger.info("IDS {0}".format("....".join(saved.tostring())))

        return list(
            filter(
                lambda x: x >= 0,
                [(-1 if (x == True) else i) for i, x in enumerate(saved)],
            )
        )

    def fetchLibrary(self, stopTrackId: List[str] = None):
        return self.fetchAll(
            "/v1/me/tracks", stopTrackId=stopTrackId, market=self.market
        )

    # Add tracks to the specified playlist ID. Maximum of 100
    def addTracks(self, playlistId: str, tracks):
        if len(tracks) > 100:
            raise Exception(
                "Too many tracks to add to playlist: {0}".format(len(tracks))
            )
        return self.post(
            "/v1/users/{0}/playlists/{1}/tracks".format(self.userId, playlistId),
            {"uris": tracks, "position": 0},
        )

    def addAllTracks(self, playlistId: str, urisAdd: List[str]):
        while len(urisAdd) > 0:
            page = urisAdd[-100:]
            self.addTracks(playlistId, page)
            urisAdd = urisAdd[:-100]

    def deleteAllTracks(self, playlistId: str, urisDel):
        while len(urisDel) > 0:
            page = urisDel[-100:]
            bodylist = list(map(lambda x: dict([("uri", x)]), page))
            url = "/v1/playlists/{0}/tracks".format(playlistId)
            self.delete(url, {"tracks": bodylist})
            urisDel = urisDel[:-100]

    def createPlaylist(self, name, description):
        return self.post(
            "/v1/users/{0}/playlists".format(self.userId),
            {"name": name, "description": description, "public": True},
        )

    def fetchPlaylists(self):
        return self.fetchAll("/v1/me/playlists")

    def fetchPlaylistTracks(self, playlistId):
        return self.fetchAll(
            "/v1/playlists/{0}/tracks".format(playlistId), market=self.market
        )

    def fetchPlaylistTracksDataframe(self, playlistId) -> DataFrame:
        existing = json_normalize(self.fetchPlaylistTracks(playlistId), sep="_")
        if not existing.empty:
            existing["original_id"] = existing.apply(
                lambda t: t["track_id"]
                if (
                    ("track_linked_from_id" not in t)
                    or pd.isnull(t["track_linked_from_id"])
                )
                else t["track_linked_from_id"],
                axis=1,
            )
            existing["original_uri"] = existing.apply(
                lambda t: t["track_uri"]
                if (
                    ("track_linked_from_uri" not in t)
                    or pd.isnull(t["track_linked_from_uri"])
                )
                else t["track_linked_from_uri"],
                axis=1,
            )
        return existing

    def fetchNamedPlaylist(self, playlistName: str):
        existingPlaylists = list(self.fetchPlaylists())
        existingPlaylist = list(
            filter(lambda playlist: playlist["name"] == playlistName, existingPlaylists)
        )
        return existingPlaylist[0] if (len(existingPlaylist) > 0) else None

    def deleteDuplicates(self, playlistId: str):
        existing = self.fetchPlaylistTracksDataframe(playlistId)
        l = sorted(
            existing[["original_uri", "track_uri"]].values.tolist(), key=lambda r: r[0]
        )
        check = []
        for k, g in groupby(l, lambda r: str(r[0])):
            if len(list(g)) > 1:
                for o in g:
                    check.append(o[1])
                check.append(k)
        if len(check) > 0:
            self.logger.debug("Deleting {0} With Duplicates".format(len(check)))
            self.deleteAllTracks(playlistId, check)
            existing = self.fetchPlaylistTracksDataframe(playlistId)
            return check
        else:
            return None

    def fetchPlaylistUris(self, playlistName: str):
        playlist = self.fetchNamedPlaylist(playlistName)
        if playlist is None:
            self.logger.debug("Cannot find excluded playlist {0}".format(playlistName))
            return []
        existing = self.fetchPlaylistTracksDataframe(playlist["id"])
        if existing.empty:
            return []
        else:
            return existing["original_uri"].values.tolist()

    def updatePlaylist(
        self,
        playlistName: str,
        libraryDataframe: DataFrame,
        description: str = None,
        excludingPlaylists=[],
    ):
        tracks = libraryDataframe["original_uri"].values.tolist()
        try:
            playlist = self.fetchNamedPlaylist(playlistName)
            if playlist is None:
                playlist = self.createPlaylist(
                    name=playlistName, description=description or playlistName
                )
            playlistId = playlist["id"]
            existing = self.fetchPlaylistTracksDataframe(playlistId)

            if existing.empty:
                existingUris = []
            else:
                self.deleteDuplicates(playlistId)
                existingUris = existing["original_uri"].values.tolist()
            # Go through the exclude playlist list, fetch the original URIs and filter out the tracks
            for excludingPlaylist in excludingPlaylists:
                exPlaylist = self.fetchPlaylistUris(excludingPlaylist)
                tracks = list(filter(lambda t: t not in exPlaylist, tracks))
            urisDel = list(filter(lambda e: e not in tracks, existingUris))
            if len(urisDel) > 0:
                self.logger.debug(
                    "{1}: Deleting {0} Tracks".format(len(urisDel), playlistName)
                )
            urisAdd = list(filter(lambda t: t not in existingUris, tracks))
            if len(urisAdd) > 0:
                self.logger.debug(
                    "{1}: Adding {0} Tracks".format(len(urisAdd), playlistName)
                )
            self.deleteAllTracks(playlist["id"], urisDel)
            self.addAllTracks(playlist["id"], urisAdd)
            return libraryDataframe[
                [
                    "track_name",
                    "artist",
                    "added_at",
                    "track_released",
                    "track_popularity",
                    "instrumentalness",
                    "danceability",
                    "energy",
                    "acousticness",
                    "loudness",
                    "tempo",
                ]
            ].head(3)
        except:
            self.logger.error("Error Processing Update to Playlist")
            raise

    def fetchLibraryDataFrame(self, cache=True):
        originIdLambda = (
            lambda t: t["track_linked_from_id"]
            if (
                ("track_linked_from_id" in t)
                and (not pd.isnull(t["track_linked_from_id"]))
                and (type(t["track_linked_from_id"] == str))
            )
            else t["track_id"]
        )
        originUriLambda = (
            lambda t: t["track_linked_from_uri"]
            if (
                ("track_linked_from_uri" in t)
                and (not pd.isnull(t["track_linked_from_uri"]))
            )
            else t["track_uri"],
        )

        # Read Cached File
        if (not cache) or (not os.path.isfile("mytracks.pkl")):
            data = self.fetchLibrary()
            tracksDf = json_normalize(data, sep="_")
            # Add Original URI and ID for linking
            tracksDf["original_id"] = tracksDf.apply(originIdLambda, axis=1)
            tracksDf["original_uri"] = tracksDf.apply(originUriLambda, axis=1)
        else:
            tracksDf = read_pickle("mytracks.pkl")
            data = self.fetchLibrary(
                stopTrackId=tracksDf[["original_id"]].iloc[0:10, 0].values.tolist()
            )
            datajs = json_normalize(data, sep="_")
            tracksDf = pd.concat([datajs, tracksDf], ignore_index=True, sort=True)
            self.logger.info(
                "Adding {0} new tracks. {1}".format(len(data), len(tracksDf))
            )
            tracksDf["original_id"] = tracksDf.apply(originIdLambda, axis=1)
            tracksDf["original_uri"] = tracksDf.apply(originUriLambda, axis=1)

        # delete unsaved tracks
        self.logger.info(
            "Checking for deletes - Library Size: {0}".format(len(tracksDf))
        )
        toDel = self.checkDeletes(tracksDf[["original_id"]].iloc[:, 0].values.tolist())
        if len(toDel) > 0:
            self.logger.info("Deleting {0} tracks".format(toDel))
            tracksDf.drop(((tracksDf.index[x]) for x in toDel), inplace=True)
            self.logger.info("Deleteted - Library Size: {0}".format(len(tracksDf)))
        tracksDf.to_pickle("mytracks.pkl")

        #        tracksDf = tracksDf.set_index("original_uri")
        # Add column foFr local release date to the library track if it's there
        tracksDf["track_released"] = tracksDf.apply(
            lambda t: datetime.strptime(
                t["track_album_release_date"],
                "%Y"
                if (t.track_album_release_date_precision == "year")
                else "%Y-%m"
                if (t.track_album_release_date_precision == "month")
                else "%Y-%m-%d",
            ),
            axis=1,
        )
        # Add an Artist Name column, first in the album list
        tracksDf["artist"] = tracksDf.apply(
            lambda a: a["track_artists"][0]["name"]
            if ("track_artists" in a)
            else "[Unknown]",
            axis=1,
        )

        # Read Albums, with cache
        self.logger.info("Checking Albums")
        albumsPickle = (
            read_pickle("albums.pkl") if (os.path.isfile("albums.pkl")) else None
        )
        album_ids = list(set(tracksDf["track_album_id"].values))
        albums = self.fetchAllIds(
            "/v1/albums",
            album_ids,
            resultField="albums",
            pageSize=20,
            existingDf=albumsPickle,
            market=self.market,
        )
        albumsDf = json_normalize(albums, sep="_").set_index("id")
        albumsDf.to_pickle("albums.pkl")

        # Add a Released DateTime Column, calculated from the release_date
        albumsDf["album_released"] = albumsDf.apply(
            lambda al: datetime.strptime(
                al["release_date"],
                "%Y"
                if (al.release_date_precision == "year")
                else "%Y-%m"
                if (al.release_date_precision == "month")
                else "%Y-%m-%d",
            ),
            axis=1,
        )

        albumIds = albumsDf.index.values
        missingAlbums = tracksDf[~tracksDf["track_album_id"].isin(albumIds)]
        if len(missingAlbums) > 0:
            self.logger.warn(
                "There are {0} tracks in your library with albums no longer Spotify".format(
                    len(missingAlbums)
                )
            )

        # Join the Albums Columns using track_album_id index to album
        libraryWithAlbums = merge(
            tracksDf,
            albumsDf,
            left_on="track_album_id",
            right_index=True,
            suffixes=("_track", "_album"),
            how="left",
            sort=True,
        )

        # Read the Features
        self.logger.info("Checking Features")
        featuresPickle = (
            read_pickle("features.pkl").set_index("id")
            if (os.path.isfile("features.pkl"))
            else None
        )
        features = self.fetchAllIds(
            "/v1/audio-features",
            tracksDf["original_id"].to_list(),
            resultField="audio_features",
            pageSize=50,
            existingDf=featuresPickle,
        )
        featuresDf = json_normalize(features, sep="_")
        featuresDf.to_pickle("features.pkl")

        # REMOVED - ARTIST FETCHING - Add BACK LATER
        # artist_and_track = json_normalize( data=data, record_path=['track','artists'],  meta=[["track","name"],["track","uri"]],  record_prefix='artist_',   sep="_" )
        # artist_and_track = artist_and_track[['track_name','artist_id','artist_name', 'track_uri']]
        # artistsPickle = read_pickle("artists.pkl") if (os.path.isfile("artists.pkl")) else None
        # artistIds = list(set(artist_and_track["artist_id"].values))
        # artists = spot.
        #                   ("/v1/artists","artists",artistIds,existingDf=artistsPickle)
        # artistsDf = json_normalize(artists).set_index("id")
        # artistsDf.to_pickle("artists.pkl")
        # artistsDf[["name","genres"]].head(2)

        # Merge Features
        lib = merge(
            libraryWithAlbums,
            featuresDf.set_index("uri"),
            left_on="original_uri",
            #  left_index=True,
            right_index=True,
            how="left",
            sort=True,
        )
        return lib
