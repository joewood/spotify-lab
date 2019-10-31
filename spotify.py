import requests
import json
import logging

from pandas.io.json import json_normalize
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Spotify:
    auth = None
    userId = None
    imageUrl = None
    user = None

    def __init__(self, auth):
        self.auth = auth
        self.user = self.fetch("/v1/me")
        self.userId = self.user["id"]
        self.imageUrl = self.user["images"][0]["url"]

    def fetch(self, path, url=None):
        callPath = url if (url != None) else ("https://api.spotify.com" + path)
        response = requests.get(
            callPath, headers={"Authorization": "Bearer " + self.auth.access_token})
        if (response.status_code != 200):
            logging.debug("error ")
        return response.json()

    def post(self, path, body, url=None):
        callPath = url if (url != None) else ("https://api.spotify.com" + path)
        response = requests.post(callPath, headers={
                                 "Authorization": "Bearer " + self.auth.access_token}, data=json.dumps(body))
        if (response.status_code != 200):
            logging.debug("error ")
        return response.json()

    def delete2(self, path, body, url=None):
        callPath = url if (url != None) else ("https://api.spotify.com" + path)
        response = requests.delete(callPath, headers={
                                   "Authorization": "Bearer " + self.auth.access_token}, data=json.dumps(body))
        if (response.status_code != 200):
            logging.debug("error ")
        return response.json()

    def fetchPage(self, path, offset, limit):
        return self.fetch(path + "?offset=" + str(offset) + "&limit=" + str(limit))

    def fetchAll(self, path):
        more = self.fetchPage(path, 0, 50)
        limit = more["limit"]
        total = more["total"] - limit
        items = more["items"]
        while((total > 0) and (more["next"] != None)):
            more = self.fetch(None, url=more["next"])
            items.extend(more["items"])
            total = total - len(more["items"])
        return items

    def fetchPageIds(self, path, ids):
        return self.fetch("{0}?ids={1}".format(path, ",".join(ids)))

    def fetchAllIds(self, path, resultField, ids, pageSize=50, existingDf=None):
        if (existingDf is not None):
            logging.info("Update Rows {0} IDs. Cache {1}".format(
                len(ids), len(existingDf)))
            keys = list(existingDf.index.values)
            ids = list(filter(lambda id: (id not in keys), ids))
            existingDf = existingDf.reset_index()
            logging.info("Filtering out {0} IDs. Now {1}".format(
                len(keys), len(ids)))
        total = len(ids)
        logging.info("Requesting {0} rows. {1} ... {2}".format(
            total, path, resultField))
        offset = 0
        while (offset < total):
            result = self.fetchPageIds(
                path, ids[offset: min(total, offset + pageSize)])
            if (resultField not in result):
                logger.error("Key not in results: {0}".format(result.keys()))
                raise Exception("Cannot find key in results")
            items = json_normalize(result[resultField])
            if (existingDf is None):
                logging.info("Creating new DF {0}".format(len(items)))
                existingDf = items
            else:
                existingDf = existingDf.append(items, ignore_index=True)
            offset += len(items)
        return existingDf.to_dict(orient="records")

    def addTracks(self, playlistId, tracks):
        return self.post("/v1/users/{0}/playlists/{1}/tracks".format(self.userId, playlistId), {
            "uris": tracks
        })

    def createPlaylist(self, name, description):
        return self.post("/v1/users/{0}/playlists".format(self.userId), {
            "name": name,
            "description": description,
            "public": True
        })

    def fetchPlaylists(self):
        return self.fetchAll("/v1/me/playlists")

    def fetchPlaylistTracks(self, playlistId):
        return self.fetchAll("/v1/playlists/{0}/tracks".format(playlistId))

    def updatePlaylist(self, playlistName, description, tracks):
        existingPlaylists = list(self.fetchPlaylists())
        existingPlaylist = list(
            filter(lambda playlist: playlist["name"] == playlistName, existingPlaylists))
        playlist = existingPlaylist[0] if (len(existingPlaylist) > 0) else self.createPlaylist(
            name=playlistName, description=description)
        existing = json_normalize(
            self.fetchPlaylistTracks(playlist["id"]), sep="_")
        if (existing.empty):
            return self.addTracks(playlist["id"], tracks)
        existingUris = existing["track_uri"].values.tolist()
        urisDel = list(filter(lambda e: e not in tracks, existingUris))
        urisAdd = list(filter(lambda t: t not in existingUris, tracks))
        while (len(urisDel) > 0):
            page = urisDel[-100:]
            bodylist = list(map(lambda x: dict([('uri', x)]), page))
            url = "/v1/playlists/{0}/tracks".format(str(playlist["id"]))
            self.delete2(url, {"tracks": bodylist})
            urisDel = urisDel[:-100]
        while (len(urisAdd) > 0):
            page = urisAdd[-100:]
            self.addTracks(playlist["id"], page)
            urisAdd = urisAdd[:-100]
        return (urisAdd, urisDel)
