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


class Fetch:
    auth = None
    # userId: str = None
    # imageUrl: str = None
    # user = None
    # market: str = None
    logger: None

    def __init__(self, auth, logger=logging.getLogger()):
        self.auth = auth
        self.logger = logger
        # self.user = self.fetch("/v1/me")
        # self.userId = self.user["id"]
        # self.imageUrl = self.user["images"][0]["url"]
        # self.market = self.user["country"]
        # logger.debug("Initialized Spotify: {0} @ {1}".format(self.userId, self.market))
        # self.fetch("/v1/me/tracks", limit=1, market=self.market)

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
            more: json = (
                self.fetch(path, offset=0, limit=50, **kwargs)
                if (more is None)
                else self.fetch(None, url=more["next"])
            )
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
