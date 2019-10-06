#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    import simplejson as json
except Exception:
    import json
import requests
import time
from traceback import format_exc
import logging
import sys
import time
import hashlib


LOGGER = logging.getLogger("playlistsyncer")

class QobuzApi(object):
    __user_auth_token = None
    __app_id = "285473059"
    __app_secret = "47249d0eaefa6bf43a959c09aacdbce8"

    def __init__(self, username, password):
        # perform login
        self.__login__(username, password)


    def get_playlists(self):
        ''' get the playlists of teh current user '''
        return self.__get_all_items("playlist/getUserPlaylists", key="playlists")

    def get_playlist(self, name, create_if_not_exists=False):
        ''' get playlist by name '''
        for playlist in self.get_playlists():
            if playlist["name"] == name:
                return playlist
        return self.create_playlist(name) if create_if_not_exists else None

    def get_playlist_tracks(self, playlist_id=None, playlist_name=None):
        ''' get playlist tracks '''
        if not playlist_id:
            playlist = self.get_playlist(playlist_name)
            if not playlist:
                return None
            playlist_id = playlist["id"]
        params = {"playlist_id": playlist_id, "extra": "tracks"}
        result = self.__get_all_items("playlist/get", params, key="tracks")
        return result

    def create_playlist(self, name, is_public=False):
        ''' create a new playlist '''
        is_public = "1" if is_public else "0"
        params = {"name": name, "is_public": is_public}
        return self.__get_data("playlist/create", params)

    def delete_playlist(self, playlist_id):
        ''' delete a playlist '''
        params = {"playlist_id": playlist_id}
        return self.__get_data("playlist/delete", params)

    def add_favourites(self, artist_ids=None, album_ids=None, track_ids=None):
        '''
            Create favorites.
            artist_ids - optional : List of artist_ids to add to favorites
            album_ids - optional : List of album_ids to add to favorites
            track_ids - optional : List of track_ids to add to favorites
        '''
        for key in ["artist_ids", "album_ids", "track_ids"]:
            data = eval(key)
            if data:
                if isinstance(data, list):
                    data = [str(item) for item in data]
                    data = ",".join(data)
                else:
                    data = str(data)
                params = {key: data}
        return self.__get_data("favorite/create", params)

    def add_albums_library(self, album_ids):
        '''
            Add albums to the user's library.
            album_ids - album id or Ordered list of album IDs.
        '''
        if isinstance(album_ids, list):
            album_ids = [str(item) for item in album_ids]
            album_ids = ",".join(album_ids)
        else:
            album_ids = str(album_ids)
        params = {"albums": album_ids}
        signing_data = "userLibraryputLibraryAlbumsalbums" + params["albums"].replace(",","")
        return self.__get_data("userLibrary/putLibraryAlbums", params, signing_data=signing_data)

    def add_tracks_library(self, track_ids):
        '''
            Add tracks to the user's library.
            track_ids - track id or Ordered list of track IDs.
        '''
        if isinstance(track_ids, list):
            track_ids = [str(item) for item in track_ids]
            track_ids = ",".join(track_ids)
        else:
            track_ids = str(track_ids)
        params = {"tracks": track_ids}
        signing_data = "userLibraryputLibraryTrackstracks" + params["tracks"].replace(",","")
        return self.__get_data("userLibrary/putLibraryTracks", params, signing_data=signing_data)

    def add_playlist_tracks(self, playlist_id, track_ids):
        '''
            Add tracks in the playlist queue.
            playlist_id - The playlist ID to add the tracks to.
            track_ids - track id or Ordered list of track IDs.
        '''
        if isinstance(track_ids, list):
            track_ids = [str(item) for item in track_ids]
            track_ids = ",".join(track_ids)
        else:
            track_ids = str(track_ids)
        params = {"playlist_id": str(playlist_id), "track_ids": track_ids}
        return self.__get_data("playlist/addTracks", params)

    def remove_playlist_tracks(self, playlist_id, playlist_track_ids):
        '''
            Remove tracks from the playlist queue.
            playlist_id - The playlist ID to remove the tracks from.
            playlist_track_ids - track id or Ordered list of track IDs.
        '''
        if isinstance(playlist_track_ids, list):
            playlist_track_ids = [str(item) for item in playlist_track_ids]
            playlist_track_ids = ",".join(playlist_track_ids)
        else:
            playlist_track_ids = str(playlist_track_ids)
        params = {"playlist_id": str(playlist_id), "playlist_track_ids": playlist_track_ids}
        return self.__get_data("playlist/deleteTracks", params)

    def search(self, query_str, query_type="tracks"):
        ''' search Qobuz '''
        params = {"query": query_str, "type": query_type}
        return self.__get_all_items("catalog/search", params, query_type)

    def __login__(self, username, password):
        ''' login to qobuz and store the token'''
        params = { "username": username, "password": password}
        details = self.__get_data("user/login", params)
        self.__user_auth_token = details["user_auth_token"]
        LOGGER.info("Succesfully logged in to Qobuz as %s" % (details["user"]["display_name"]))

    def __get_all_items(self, endpoint, params=None, key="playlists"):
        ''' retrieve all results of a large (paged) list '''
        if not params:
            params = {}
        items = []
        offset = 0
        total_items = 1
        while total_items > len(items):
            result = self.__get_data(endpoint, params)
            total_items = result[key]["total"]
            items += result[key]["items"]
            params["offset"] = result[key]["offset"] + result[key]["limit"]
        return items

    def __get_data(self, endpoint, params=None, retries=0, signing_data=None):
        '''get info from the rest api'''
        result = {}
        if not params:
            params = {}
        headers = {"X-App-Id": self.__app_id}
        if self.__user_auth_token:
            headers["X-User-Auth-Token"] = self.__user_auth_token
        url = "http://www.qobuz.com/api.json/0.2/%s" % endpoint
        if signing_data:
            request_ts = time.time()
            request_sig = signing_data + str(request_ts) + self.__app_secret
            request_sig = str(hashlib.md5(request_sig.encode()).hexdigest())
            params["request_ts"] = request_ts
            params["request_sig"] = request_sig
        try:
            response = requests.get(url, params=params, headers=headers, timeout=20)
            if response and response.content and response.status_code == 200:
                result = json.loads(response.content.decode('utf-8', 'replace'))
            else:
                raise Exception(str(response))
        except Exception as exc:
            result = None
            if "Read timed out" in str(exc) and retries < 5:
                # retry on connection error or http server limiting
                LOGGER.info("retry request")
                time.sleep(5)
            else:
                LOGGER.error("Error in __get_data: %s" % str(exc))
                LOGGER.error("endpoint: %s - params: %s" %(endpoint, params))
        # return result
        #LOGGER.debug(result)
        return result



def log_exception(modulename, exceptiondetails):
    '''helper to properly log an exception'''
    LOGGER.warning(format_exc(sys.exc_info()))
    LOGGER.error("ERROR in %s ! --> %s" % (modulename, exceptiondetails))