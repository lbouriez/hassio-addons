#!/usr/bin/env python
from __future__ import unicode_literals
import tidalapi
import logging
import requests
import simplejson as json
import sys
import os
import time
import spotipy
import spotipy.util as sp_util
import unicodedata
from difflib import SequenceMatcher as Matcher
from operator import itemgetter
from qobuz import QobuzApi
import uuid
import taglib


CUSTOM_REPLACE={
    "2 Unlimted": "2 Unlimited",
    "wokeuplikethis": "woke up like this",
    "CeeLo Green": "Cee-Lo Green",
    "Fun[k]house": "Fun{k}house",
    "fuck": "f**k",
    "2gether": "together",
    "R.I.O.": "Playlist DJs",
    "The Jacksons": "The Jackson 5",
    "B. Adams": "Bryan Adams",
    "ZAYN": "Zayn Malik",
    "Yusuf / Cat Stevens": "Cat Stevens",
    "Acda en de Munnik": "Acda & De Munnik",
    "De Kapitein Deel II": "De kapitein, deel II",
    "John Lennon & Paul McCartney": "The Beatles",
    "DJ Paul Elstak": "DJ Paul",
    "Paul Elstak": "DJ Paul",
    "Ch!pz": "Chipz",
    "12\" version": "full length version",
    "Feestteam": "Activ-8",
    "5ive": "Five"
}


############################################################################################
LOGFORMAT = logging.Formatter('%(asctime)-15s %(levelname)-5s  %(module)s -- %(message)s')
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)
consolehandler = logging.StreamHandler()
consolehandler.setFormatter(LOGFORMAT)
consolehandler.setLevel(logging.INFO)
LOGGER.addHandler(consolehandler)

if os.path.isdir("/data"):
    CACHE_FILE = "/data/cache.json"
else:
    CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),".cache")


class PlaylistSyncer():

    tidal_session = None
    tidal_user = None
    tidal_favorites = None
    sp = None
    sp_user = None
    qobuz = None
    cache = { "cache_run_count": 0 }
    search_cache = {}
    available_providers = []
    force_full_sync = False

    def __init__(self, *args, **kwargs):

        # init config and cache
        self.parse_config()
        self.load_cache()

        if self.cache["cache_run_count"] >= 7: # every week if scheduled once a day
            self.force_full_sync = True
            self.cache["cache_run_count"] = 0
        else:
            self.cache["cache_run_count"] += 1

        # login music providers
        self.login_qobuz()
        self.login_tidal()
        self.login_spotify()

        # run all sync jobs
        self.process_playlists()
        LOGGER.info("###### sync completed!")


    def parse_config(self):
        ''' grab config from file '''
        config = {
            "log_level": "info",
            "log_file": "",
            "force_full_sync": False,
            "matcher_strictness": 0.9,
            "spotify_username": "",
            "spotify_password": "",
            "tidal_username": "",
            "tidal_password": "",
            "qobuz_username": "",
            "qobuz_password": "",
            "local_music_dir": "",
            "playlists": []
        }
        if os.path.isfile("/data/options.json"):
            # grab from (hassio) config file
            with open("/data/options.json") as f:
                data = f.read()
                config = json.loads(data)
        else:
            LOGGER.error("Config file does not exist on disk!")
        log_file = config["log_file"]
        if log_file:
            logformat = logging.Formatter(LOGFORMAT)
            filehandler = logging.FileHandler(log_file, 'w')
            filehandler.setFormatter(LOGFORMAT)
            loglevel = eval("logging." + config["log_level"])
            filehandler.setLevel(loglevel)
            LOGGER.addHandler(filehandler)
        if config["force_full_sync"]:
            self.force_full_sync = True
        self.config = config
    
    def load_cache(self):
        '''load cache entries from file'''
        data = {}
        if os.path.isfile(CACHE_FILE):
            with open(CACHE_FILE) as json_data:
                data = json.load(json_data)
                self.cache = data

    def write_cache(self):
        '''write cache entries to file'''
        with open(CACHE_FILE, 'w') as outfile:
            json.dump(self.cache, outfile, indent=4)

    def login_tidal(self):
        '''log in to Tidal'''
        if not self.config["tidal_username"] or not self.config["tidal_password"]:
            return
        tidal_config = tidalapi.Config(tidalapi.Quality.lossless)
        self.tidal_session = tidalapi.Session(tidal_config)
        self.tidal_session.login(self.config["tidal_username"], self.config["tidal_password"])
        if self.tidal_session.check_login():
            LOGGER.info("succesfully logged in to Tidal as %s" % self.config["tidal_username"])
            self.tidal_user = self.tidal_session.user
            self.tidal_favorites = tidalapi.Favorites(self.tidal_session, self.tidal_user.id)
            self.available_providers.append("TIDAL")
            return True
        else:
            LOGGER.error("Could not log in to Tidal !")
            return False

    def login_qobuz(self):
        '''log in to Qobuz'''
        if not self.config["qobuz_username"] or not self.config["qobuz_password"]:
            return False
        try:
            self.qobuz = QobuzApi(self.config["qobuz_username"], self.config["qobuz_password"])
            self.available_providers.append("QOBUZ")
            return True
        except Exception as exc:
            LOGGER.error("Could not log in to Qobuz ! %s" % str(exc))
            return False

    def login_spotify(self):
        '''request spotify token by using the spotty binary'''
        if not self.config["spotify_username"] or not self.config["spotify_password"]:
            return False
        token_info = None
        import subprocess
        scopes = [
            "user-read-playback-state",
            "user-read-currently-playing",
            "user-modify-playback-state",
            "playlist-read-private",
            "playlist-read-collaborative",
            "playlist-modify-public",
            "playlist-modify-private",
            "user-follow-modify",
            "user-follow-read",
            "user-library-read",
            "user-library-modify",
            "user-read-private",
            "user-read-email",
            "user-read-birthdate",
            "user-top-read"]
        scope = ",".join(scopes)
        clientid = '2eb96f9b37494be1824999d58028a305'
        clientsecret = '038ec3b4555f46eab1169134985b9013'
        args = [self.get_spotty_binary(), "-t", "--client-id", clientid, "--scope", scope, "-n", "temp-spotty", "-u", self.config["spotify_username"], "-p", self.config["spotify_password"], "--disable-discovery"]
        spotty = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = spotty.communicate()
        result = json.loads(stdout)
        # transform token info to spotipy compatible format
        if result and "accessToken" in result:
            self.sp = spotipy.Spotify(auth=result["accessToken"])
            self.sp_user = self.sp.me()
            LOGGER.info("Succesfully logged in to Spotify as %s" % self.sp_user["id"])
            LOGGER.debug(self.sp_user)
            self.available_providers.append("SPOTIFY")
            return True
        LOGGER.error("Can't get Spotify token for user %s" % self.config["spotify_username"])
        return False

    def find_duplicates_in_playlist(self, provider, playlist_name):
        ''' find duplicates in playlist'''
        LOGGER.info(" ")
        LOGGER.info("###### Find duplicate songs in %s/%s ######" %(provider, playlist_name))
        all_ids = []
        tracks = self.get_playlist_tracks(provider, playlist_name)
        for track in tracks:
            track_str = "%s - %s" %("/".join(track["artists"]), track["title"])
            LOGGER.debug("Processing %s...." % track_str)
            match = self.find_duplicate_in_tracks(track, tracks)
            if match and (track["id"] != match["id"]) or (track["id"] in all_ids):
                LOGGER.info(" ")
                LOGGER.info("Duplicate track found in %s Playlist %s --> %s" % (provider, playlist_name, track_str))
                track_str2 = "%s - %s" %("/".join(match["artists"]), match["title"])
                LOGGER.info("...Duplicate: %s" % track_str2)
            all_ids.append(track["id"])
                        
    def process_playlists(self):
        ''' process all playlists '''
        for playlist in self.config["playlists"]:
            if not playlist["source_playlist"] or playlist["source_playlist"] == "*":
                continue
            if not playlist["destination_playlist"] or playlist["destination_playlist"] == "*":
                playlist["destination_playlist"] = playlist["source_playlist"]
            m3u_playlist = playlist.get("m3u_playlist")
            allow_other_version = playlist.get("allow_other_version", True)
            self.sync_playlist(playlist["source_provider"], playlist["source_playlist"], playlist["destination_provider"], playlist["destination_playlist"], playlist["add_library"], allow_other_version, m3u_playlist)
            if playlist["two_way"]:
                # also sync the other way around
                self.sync_playlist(playlist["destination_provider"], playlist["destination_playlist"], playlist["source_provider"], playlist["source_playlist"], playlist["add_library"], allow_other_version)
            # look for duplicate tracks
            if self.force_full_sync:
                self.find_duplicates_in_playlist(playlist["source_provider"], playlist["source_playlist"])
                self.find_duplicates_in_playlist(playlist["destination_provider"], playlist["destination_playlist"])
        #TODO: process wildcards

    def sync_playlist(self, source_provider, source_playlist, destination_provider, destination_playlist, add_library, allow_other_version, m3u_playlist=None):
        ''' process all spotify playlists'''
        LOGGER.info(" ")
        LOGGER.info("### SYNCING %s/%s to %s/%s" % (source_provider, source_playlist, destination_provider, destination_playlist))
        for provider in [source_provider, destination_provider]:
            if provider not in self.available_providers:
                LOGGER.error("%s is not initialized!" % provider)
                return
        src_tracks = self.get_playlist_tracks(source_provider, source_playlist)
        cache_key = "%s_%s_%s_%s" %(source_provider, source_playlist, destination_provider, destination_playlist)
        tracks_cache = self.cache.get(cache_key,[])
        dest_tracks = self.get_playlist_tracks(destination_provider, destination_playlist)
        m3u_entries = []
        destination_playlist_org = destination_playlist
        dest_tracks_count = len(dest_tracks) # funky workaround for qobuz 1000 tracks limit
        
        for track in src_tracks:
            if destination_provider == 'QOBUZ':
                # funky workaround for qobuz 1000 tracks limit
                if dest_tracks_count >= 3000:
                    destination_playlist = destination_playlist_org + "__3"
                elif dest_tracks_count >= 2000:
                    destination_playlist = destination_playlist_org + "__2"
                elif dest_tracks_count >= 1000:
                    destination_playlist = destination_playlist_org + "__1"
            track_str = "%s - %s" %("/".join(track["artists"]), track["title"])
            cache_match = self.find_match_in_tracks(track, tracks_cache)
            if cache_match and not self.force_full_sync and 'm3u_entry' in cache_match:
                LOGGER.debug("%s present in cache and will be ignored this run" % track_str)
                if cache_match.get('syncpartner_id'):
                    track["syncpartner_id"] = cache_match["syncpartner_id"]
                if cache_match.get('m3u_entry'):
                    m3u_entries.append( cache_match['m3u_entry'] )
                    track['m3u_entry'] = cache_match['m3u_entry']
            else:
                # this track is not in the cache from last run so it's added (or this is a full sync)
                dest_match = self.find_match_in_tracks(track, dest_tracks, version_match=True)
                if not dest_match:
                    # look for different version of the same track
                    dest_match = self.find_match_in_tracks(track, dest_tracks, version_match=False)
                    if dest_match:
                        track_str2 = "%s - %s" % ("/".join(dest_match["artists"]), dest_match["title"])
                        LOGGER.warning("Matched with different version ! %s: %s - %s: %s" %(source_provider, track_str, destination_provider, track_str2))
                if not dest_match:
                    add_match = self.add_track_to_playlist(track, destination_provider, destination_playlist, add_library, allow_other_version)
                    if add_match:
                        dest_tracks_count += 1
                        dest_match = add_match
                if dest_match:
                    track["syncpartner_id"] = dest_match["id"]
                    m3u_entry = self.create_m3u_entry(dest_match['id'], track_str, destination_provider)
                    m3u_entries.append( m3u_entry )
                    track['m3u_entry'] = m3u_entry
                else:
                    local_match = self.find_match_file(track, source_provider)
                    if local_match:
                        m3u_entry = self.create_m3u_entry(local_match, track_str, 'FILE')
                        m3u_entries.append( m3u_entry )
                        track['m3u_entry'] = m3u_entry
                        LOGGER.warning("Track %s matched to local file: %s" %(track_str, local_match))
                    else:
                        m3u_entry = self.create_m3u_entry(track['id'], track_str, source_provider)
                        m3u_entries.append( m3u_entry )
                        track['m3u_entry'] = m3u_entry
                        LOGGER.warning("Track %s could not be added to %s/%s" %(track_str, destination_provider, destination_playlist))

        # write m3u playlist
        if m3u_playlist:
            with open(m3u_playlist, 'w+') as m3u_file:
                m3u_file.write('#EXTM3U\n')
                for item in m3u_entries:
                    m3u_file.write(item)

        # process track deletions
        LOGGER.info(" ")
        LOGGER.info("# Checking for deleted tracks in playlist %s/%s...." % (source_provider, source_playlist))
        for track in tracks_cache:
            track_str = "%s - %s" %("/".join(track["artists"]), track["title"])
            if not self.find_match_in_tracks(track, src_tracks, version_match=True):
                LOGGER.debug("%s is removed from %s/%s" % (track_str, source_provider, source_playlist))
                if track.get("syncpartner_id"): 
                    LOGGER.warning("%s will be removed from %s/%s" % (track_str, destination_provider, destination_playlist_org))
                    self.remove_track_from_playlist(destination_provider, destination_playlist_org, track["syncpartner_id"])
        # save cache
        self.cache[cache_key] = src_tracks
        self.write_cache()
        
    def remove_track_from_playlist(self, provider, playlist_name, track_id):
        if provider == "TIDAL":
            tidal_playlist = self.get_tidal_playlist(playlist_name)
            self.tidal_user.remove_playlist_entry(tidal_playlist.id, item_id=track_id)
        elif provider == "QOBUZ":
            qobuz_playlist = self.qobuz.get_playlist(playlist_name)
            for track in self.get_qobuz_playlist_tracks(playlist_name):
                if track["id"] == track_id:
                    self.qobuz.remove_playlist_tracks(qobuz_playlist["id"], track["playlist_track_id"])
        elif provider == "SPOTIFY":
            spotify_playlist = self.get_spotify_playlist(playlist_name)
            self.sp.user_playlist_remove_all_occurrences_of_tracks(spotify_playlist["owner"]["id"], spotify_playlist["id"], [track_id])

    def find_match_in_tracks(self, track_left, tracks_right, prefer_quality=0, version_match=False, album_match=False):
        ''' match given track in list with tracks from other service'''
        # double check that we have enough details
        if not track_left["title"] or not track_left["artists"]:
            LOGGER.error("malformed track found: %s" % (track_left))
            return None
        # iterate through the items to find a match
        for allow_loose_matching in [False, True]:
            for track_right in tracks_right:
                # make sure we have a title and artists
                if not track_right["title"] or not track_right["artists"]:
                    LOGGER.error("malformed track found: %s - %s" %(track_right["artists"], track_right["title"]))
                    continue
                if track_left["id"] == track_right["id"]:
                    return track_right
                # continue with matching the title and artists
                if self.find_title_match(track_left["title"], track_right["title"], allow_loose_matching) and self.find_artist_match(track_left["artists"], track_right["artists"], allow_loose_matching):
                    # track match found !
                    # check track version
                    if version_match and not self.version_match(track_left["version"], track_right["version"], track_left["album"], track_right["album"], allow_loose_matching):
                        continue # version does not match
                    # check album
                    if album_match and track_left["album"] and track_right["album"] and not self.find_title_match(track_left["album"], track_right["album"], allow_loose_matching):
                        continue # album does not match
                    if track_right["quality"] >= prefer_quality:
                        return track_right
        return None

    def find_duplicate_in_tracks(self, track_left, tracks_right):
        ''' find duplicate of tracks in list'''
        track_count = 0
        for track_right in tracks_right:
            if track_left["id"] == track_right["id"]:
                if track_count == 0:
                    # this is the actual track found in the list
                    track_count += 1
                else:
                    # the exact same track is found multiple times
                    return track_right
            elif self.find_title_match(track_left["title"], track_right["title"], True) and self.find_artist_match(track_left["artists"], track_right["artists"], True):
                # track match found !
                return track_right
        return None

    def find_title_match(self, item_left, item_right, allow_loose_matching):
        # try strict matching first
        if item_left.lower() == item_right.lower():
            # perfect match
            return True
        if self.get_comparestring(item_left.lower()) == self.get_comparestring(item_right.lower()):
            # near perfect match
            return True
        if Matcher(None, item_left.lower(), item_right.lower()).ratio() >= 0.97:
            # near perfect match
            return True
        # try matching with using substitutes
        if allow_loose_matching:
            all_titles_left = self.split_title(item_left)
            all_titles_right = self.split_title(item_right)
            # use sequencematcher to solve small typos
            for strictness in [0.97, self.config["matcher_strictness"]]:
                for _title_left in all_titles_left:
                    for _title_right in all_titles_right:
                        if Matcher(None, _title_left.lower(), _title_right.lower()).ratio() >= strictness:
                            # title match found
                            return True
        return False

    def find_artist_match(self, artists_left, artists_right, allow_loose_matching):
        # try strict matching first
        _artists_left = artists_left + self.get_replacements(artists_left)
        _artists_right = artists_right + self.get_replacements(artists_right)
        if _artists_left[0] in _artists_right or _artists_right[0] in _artists_left:
            # perfect match
            return True
        # try matching with using substitutes (loose matching)
        if allow_loose_matching:
            for _artist_left in _artists_left:
                for _artist_right in _artists_right:
                    if Matcher(None, _artist_left.lower(), _artist_right.lower()).ratio() >= 0.95:
                        # near perfect match
                        return True
            all_artists_left = self.split_artists(_artists_left)
            all_artists_right = self.split_artists(_artists_right)
            for strictness in [0.95, self.config["matcher_strictness"]]:    
                for _artist_left in all_artists_left:
                    for _artist_right in all_artists_right:
                        if Matcher(None, _artist_left.lower(), _artist_right.lower()).ratio() >= strictness:
                            return True
        return False

    

    ####### SEARCH TRACKS ######################

    def search_track(self, track_details, provider, version_match=True):
        ''' locate track on streaming provider'''
        minimum_qualities = [0]
        if provider == "TIDAL":
            minimum_qualities = [7, 0]
        elif provider == "QOBUZ":
            minimum_qualities = [26, 7, 0]

        for artist_str in track_details["artists"] + self.split_artists(track_details["artists"]):
            for title_str in self.split_title(track_details["title"]):
                searchstring = "%s - %s" %(artist_str, title_str)
                # we prefer a match with the highest quality (only applies to tidal and qobuz)
                for minimum_quality in minimum_qualities:
                    for album_match in [True, False]:
                        if searchstring in self.search_cache:
                            results = self.search_cache[searchstring]
                        else:
                            LOGGER.debug("searching %s for %s" % (provider, searchstring))
                            if provider == "TIDAL":
                                results = self.tidal_session.search("track", searchstring)
                                results = self.parse_tidal_tracks(results.tracks)
                            elif provider == "QOBUZ":
                                results = self.qobuz.search(searchstring, "tracks")
                                results = self.parse_qobuz_tracks(results)
                            elif provider == "SPOTIFY":
                                results = self.sp.search(q="%s artist:%s" %(title_str, artist_str), type="track", market="from_token")
                                results = self.parse_spotify_tracks(results["tracks"]["items"])
                            else:
                                return
                        self.search_cache[searchstring] = results
                        if results:
                            match = self.find_match_in_tracks(track_details, results, 
                                    prefer_quality=minimum_quality, album_match=album_match, version_match=version_match)
                            if match:
                                return match
                            elif minimum_quality and not match and version_match:
                                other_match = self.find_match_in_tracks(track_details, results, 
                                    prefer_quality=minimum_quality, album_match=False, version_match=False)
                                if other_match:
                                    LOGGER.warning("Match available with better quality (%s)! %s" % (other_match["quality"], other_match["title"]))
        return None

    def search_track_spotify(self, track_details, version_match=True):
        ''' locate track on spotify'''
        return self.search_track(track_details, "SPOTIFY", version_match)

    def search_track_tidal(self, track_details, version_match=True):
        ''' locate track on tidal'''
        return self.search_track(track_details, "TIDAL", version_match)

    def search_track_qobuz(self, track_details, version_match=True):
        ''' locate track on qobuz'''
        return self.search_track(track_details, "QOBUZ", version_match)

    

    ####### ADD TRACK TO PLAYLIST ####################

    def add_track_to_playlist(self, track_details, provider, playlist_name, add_library=False, allow_other_version=False):
        ''' search and add track to playlist '''
        track_str = "%s - %s" % ("/".join(track_details["artists"]), track_details["title"])
        result = None
        for version_match in [True, not allow_other_version]:
            if provider == "TIDAL":
                result = self.add_track_to_tidal_playlist(track_details, playlist_name, add_library, version_match)
            elif provider == "QOBUZ":
                result = self.add_track_to_qobuz_playlist(track_details, playlist_name, add_library, version_match)
            elif provider == "SPOTIFY":
                result = self.add_track_to_spotify_playlist(track_details, playlist_name, add_library, version_match)
            if result:
                track_str2 = "%s - %s" % ("/".join(result["artists"]), result["title"])
                if version_match == False:
                    LOGGER.warning("Accepted different version ! %s --> %s" %(track_str, track_str2))
                return result
        return None


    def add_track_to_tidal_playlist(self, track_details, playlist_name, add_library=False, version_match=True):
        ''' attempt to add a track to a Tidal playlist '''
        tidal_playlist = self.get_tidal_playlist(playlist_name, True)
        tidal_track = self.search_track_tidal(track_details, version_match)
        if tidal_track:
            if add_library:
                self.tidal_favorites.add_album(str(tidal_track["album_id"]))
                LOGGER.debug("Added album %s to Tidal library" % (tidal_track["album"]))
                self.tidal_favorites.add_track(str(tidal_track["id"]))
                LOGGER.debug("Added track %s to Tidal library" % tidal_track["title"])
            self.tidal_user.add_playlist_entries(tidal_playlist, [str(tidal_track["id"])])
            track_str = "%s - %s" %("/".join(tidal_track["artists"]), tidal_track["title"])
            LOGGER.info("Added track %s to Tidal playlist %s" % (track_str, playlist_name))
            return tidal_track
        else:
            return None

    def add_track_to_qobuz_playlist(self, track_details, playlist_name, add_library=False, version_match=True):
        ''' attempt to add a track to a Qobuz playlist '''
        qobuz_playlist = self.qobuz.get_playlist(playlist_name, True)
        qobuz_track = self.search_track_qobuz(track_details, version_match)
        if qobuz_track:
            track_str = "%s - %s" % ("/".join(qobuz_track["artists"]), qobuz_track["title"])
            if add_library:
                self.qobuz.add_albums_library(qobuz_track["album_id"])
                self.qobuz.add_favourites(album_ids=qobuz_track["album_id"])
                LOGGER.debug("Added album %s to Qobuz library" % (qobuz_track["album"]))
                self.qobuz.add_tracks_library(qobuz_track["id"])
                self.qobuz.add_favourites(track_ids=qobuz_track["id"])
                LOGGER.debug("Added track %s to Qobuz library" % track_str)
            self.qobuz.add_playlist_tracks(qobuz_playlist["id"], qobuz_track["id"])
            if qobuz_track["quality"] > 1:
                LOGGER.info("Added track %s to Qobuz playlist %s - HIRES %s" % (track_str, qobuz_playlist["name"], qobuz_track["quality"]))
            else:
                LOGGER.info("Added track %s to Qobuz playlist %s" % (track_str, qobuz_playlist["name"]))
            return qobuz_track
        else:
            return None

    def add_track_to_spotify_playlist(self, track_details, playlist_name, add_library=False, version_match=True):
        '''add track to spotify playlist'''
        playlist = self.get_spotify_playlist(playlist_name)
        sp_track = self.search_track_spotify(track_details, version_match)
        if sp_track:
            self.sp.user_playlist_add_tracks(self.sp_user["id"], playlist["id"], [sp_track["id"]])
            track_str = "%s - %s" %("/".join(sp_track["artists"]), sp_track["title"])
            LOGGER.info("Added track to Spotify playlist %s: %s" % (playlist["name"], track_str))
            return sp_track
        else:
            return None

    ###### PLAYLISTS ##################

    def get_spotify_playlists(self):
        '''get all current users playlists'''
        playlists = self.sp.current_user_playlists()
        if playlists and playlists.get("items"):
            return playlists["items"]
        else:
            return []

    def get_spotify_playlist(self, playlist_name, allow_create=True):
        for sp_playlist in self.get_spotify_playlists():
            if playlist_name.lower() == sp_playlist["name"].lower():
                return sp_playlist
        if allow_create:
            return self.sp.user_playlist_create(self.sp_user["id"], playlist_name, public=False)
        return None

    def get_tidal_playlist(self, playlist_name, allow_create=True):
        for playlist in self.tidal_user.playlists():
            if playlist.title == playlist_name:
                return playlist
        # create playlist if not found
        if allow_create:
            LOGGER.warning("Playlist %s not found on Tidal, creating it..." % playlist_name)
            return self.tidal_user.create_playlist(playlist_name)
        return None

    def get_tidal_playlists(self, filter=None):
        '''return all Tidal playlists'''
        playlists = []
        if not filter:
            return self.tidal_user.playlists()
        else:
            for playlist in self.tidal_user.playlists():
                if playlist.title.startswith(filter):
                    playlists.append(playlist)
        return playlists

    
    ##### PLAYLIST TRACKS ##############

    def get_playlist_tracks(self, provider, playlist_name):
        if provider == "TIDAL":
            return self.get_tidal_playlist_tracks(playlist_name)
        elif provider == "QOBUZ":
            return self.get_qobuz_playlist_tracks(playlist_name)
        elif provider == "SPOTIFY":
            return self.get_spotify_playlist_tracks(playlist_name)
        else:
            return []
    
    def get_tidal_playlist_tracks(self, playlist_name):
        tidal_playlist = self.get_tidal_playlist(playlist_name)
        if not tidal_playlist:
            return []
        result = self.tidal_session.get_playlist_tracks(tidal_playlist.id)
        return self.parse_tidal_tracks(result)

    def get_qobuz_playlist_tracks(self, playlist_name):
        '''grab all tracks for the given playlist'''
        result = []
        for postfix in ["","__1","__2","__3"]: # funky workaround for 1000 tracks limit of qobuz
            playlist_name = playlist_name + postfix
            res = self.qobuz.get_playlist_tracks(playlist_name=playlist_name)
            if res:
                result += res
            else:
                break
        return self.parse_qobuz_tracks(result)

    def get_spotify_playlist_tracks(self, playlist_name):
        sp_playlist = self.get_spotify_playlist(playlist_name)
        playlist_id = sp_playlist["id"]
        user_id = sp_playlist["owner"]["id"]
        offset = 0
        all_tracks = []
        while True:
            tracks = self.sp.user_playlist_tracks(user_id, playlist_id, limit=100, offset=offset, market=self.sp_user["country"])
            if tracks and tracks.get("items"):
                all_tracks += tracks["items"]
                offset += len(tracks["items"])
            else:
                break
        return self.parse_spotify_tracks(all_tracks)


    ###### HELPER METHODS ###########


    @staticmethod
    def get_comparestring(txt):
        txt = unicodedata.normalize('NFKD', txt).encode('ASCII', 'ignore').decode()
        txt = txt.replace("'","").replace("!","").replace("?","").replace("#","").replace("*","").replace("(","").replace(")","")
        return txt

    def get_comparestrings(self, lst):
        new_list = []
        for item in lst:
            item2 = self.get_comparestring(item)
            if item != item2 and item2 not in new_list:
                new_list.append(item2)
        return new_list

    def split_artists(self, artists):
        all_artists = []
        all_artists += artists
        splitters = [" vs ", " vs. ", " feat", " Feat", " / ", " & ", " /\\ ", " with ", " x "]
        for artist in artists:
            for splitter in splitters:
                if splitter in artist:
                    all_artists += artist.split(splitter)
        
        # handle comparestrings
        all_artists += self.get_comparestrings(all_artists)
        # add custom replacement strings
        all_artists += self.get_replacements(all_artists)
        return all_artists

    def split_title(self, title):
        all_titles = [title]
        # handle splitters
        splitters = [" (",  " [", ",", " vs", " - ", "...", " feat", " Feat", " Live"]
        for splitter in splitters:
            if splitter in title:
                all_titles.append(title.split(splitter)[0])
                break

        if "," in title:
            all_titles.append(title.replace(",", ""))
        if " & " in title:
            all_titles.append(title.replace(" & ", " and "))
        if " And " in title:
            all_titles.append(title.replace(" And ", " & "))

        # handle comparestrings
        all_titles += self.get_comparestrings(all_titles)
        # add custom replacement strings
        all_titles += self.get_replacements(all_titles)
        return all_titles

    @staticmethod
    def remove_duplicates(all_strings):
        '''remove dupes (case-insensitive) from list'''
        result=[]
        marker = set()
        for l in all_strings:
            ll = l.lower()
            if ll not in marker:   # test presence
                marker.add(ll)
                result.append(l)   # preserve order
        return result

    @staticmethod
    def get_replacements(all_strings):
        '''append replacements of strings to list'''
        new_list = []
        for org_string, repl_string in CUSTOM_REPLACE.items():
            for item in all_strings:
                if item == org_string:
                    new_list.append(repl_string)
                elif item == repl_string:
                    new_list.append(org_string)
                elif org_string in item:
                    new_list.append(item.replace(org_string, repl_string))
                elif repl_string in item:
                    new_list.append(item.replace(repl_string, org_string))
        for item in all_strings:
            if item.startswith("The "):
                new_list.append(item.replace("The ", ""))
            if item.startswith("De "):
                new_list.append(item.replace("De ", ""))
            if item.startswith("Les "):
                new_list.append(item.replace("Les ", ""))
            if item.endswith(",The"):
                new_list.append(item.replace(",The", ""))
            if item.endswith(",De"):
                new_list.append(item.replace(",De", ""))
            if "Deejay" in item:
                new_list.append(item.replace("Deejay", "DJ"))
        return new_list

    @staticmethod
    def get_filename(str):
        return str.replace("/","").replace(",","")

    def find_match_file(self, track_details, provider):
        ''' try to find a match in files'''
        if not self.config["local_music_dir"]:
            return None
        artists = track_details['artists']
        title = track_details['title']
        album = track_details['album']
        clean_artist = self.get_filename(artists[0])
        clean_title = self.get_filename(title)
        if not album:
            album = title
        clean_album = self.get_filename(album)
        file_dir = "%s/%s/%s" % (self.config["local_music_dir"], clean_artist, clean_album)
        filename = "%s/%s - %s.flac" % (file_dir, clean_artist, clean_title)
        if os.path.isfile(filename):
            return filename
        elif provider == "SPOTIFY":
            # grab file from spotify just as workaround for now and as last resort
            tmp_file = None
            import subprocess
            tmp_file = "/tmp/%s.flac" % track_details["id"]
            cmd = "%s -n test -u %s -p %s --single-track %s | flac - --endian little --channels 2 --bps 16 --sample-rate 44100 --sign signed -f -o %s" % (self.get_spotty_binary(), self.config["spotify_username"], self.config["spotify_password"], track_details["id"], tmp_file)
            subprocess.call(cmd, shell=True)
            import shutil
            time.sleep(1)
            song = taglib.File(tmp_file)
            song.tags["ARTIST"] = artists
            song.tags["TITLE"] = [title]
            song.tags["ALBUM"] = [album]
            song.save()
            # save to final dest
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            shutil.move(tmp_file, filename)
            return filename
        return None

    def parse_spotify_tracks(self, spotify_tracks):
        ''' convert output from Spotify to universal layout '''
        result = []
        for track in spotify_tracks:
            if track.get("track"):
                track = track["track"]
            if not track["is_playable"]:
                continue
            item = { 
                "id": track["id"], 
                "title": track["name"], 
                "album":"", 
                "album_id": track["album"]["id"],
                "artists": [],
                "quality": 0
            }
            # append album details
            if track["album"]["artists"][0]["name"] and not "various" in track["album"]["artists"][0]["name"].lower():
                item["album"] = track["album"]["name"] # ignore various artists collections
                item["artists"].append(track["album"]["artists"][0]["name"])
            for artist in [artist["name"] for artist in track["artists"]]:
                if artist not in item["artists"]:
                    item["artists"].append(artist)
            item["version"] = self.parse_track_version(item["title"], item["album"])
            result.append(item)
        return result

    def parse_track_version(self, title, album):
        ''' try to extract the version from the title or album '''
        version = ""
        # try to extract from title first
        for splitter in ["(", "[", "-", " - "]:
            if splitter in title:
                for title_part in title.split(splitter):
                    # look for the end splitter
                    for end_splitter in [")", "]"]:
                        if end_splitter in title_part:
                            title_part = title_part.split(end_splitter)[0]
                    for version_str in ["version", "live", "edit", "remix", "mix", "acoustic", " instrumental", "karaoke", "remaster", "versie", "explicit", "radio cut"]:
                        if version_str in title_part.lower():
                            version = title_part.strip()
                            return version
        # fall back to album
        for splitter in ["(", "[", "-", " - "]:
            if splitter in album:
                for title_part in album.split(splitter):
                    # look for the end splitter
                    for end_splitter in [")", "]"]:
                        if end_splitter in title_part:
                            title_part = title_part.split(end_splitter)[0]
                    for version_str in ["live", " edit ", "remix", " mix", "acoustic", "instrumental", "karaoke", "remaster"]:
                        if version_str in title_part.lower():
                            version = title_part.strip()
                            return version
        # last resort
        for version_str in ["remaster", "karaoke", "acoustic", "instrumental", "live"]:
            if version_str in album.lower() or version_str in title.lower():
                return version_str
        return version

    def parse_tidal_tracks(self, tidal_tracks):
        ''' convert output from Tidal to universal layout '''
        result = []
        for track in tidal_tracks:
            if not track.available:
                continue
            item = { 
                "id": track.id, 
                "title": track.title, 
                "album":"", 
                "album_id": track.album.id,
                "artists": []
            }
            if track.audioQuality == "HI_RES":
                item["quality"] = 26
            elif track.audioQuality == "LOSSLESS":
                item["quality"] = 1
            else:
                item["quality"] = 0
            # append album details
            if track.album.name and not "various" in track.album.name.lower():
                item["album"] = track.album.name # ignore various artists collections
                item["artists"].append(track.album.artist.name)
            item["artists"] += [artist.name for artist in track.album.artists]
            item["version"] = self.parse_track_version(item["title"], item["album"])
            result.append(item)
        return result

    def parse_qobuz_tracks(self, tracks):
        ''' convert output from Qobuz to universal layout '''
        result = []
        for track in tracks:
            if not track["streamable"]:
                continue
            item = { 
                "id": track["id"], 
                "title": track["title"], 
                "album":"", 
                "album_id": track["album"]["id"],
                "artists": [],
                "quality": 1
            }
            # append album details
            if track["album"]["artist"]["name"] and not "various" in track["album"]["artist"]["name"].lower():
                item["album"] = track["album"]["title"] # ignore various artists collections
                item["artists"].append(track["album"]["artist"]["name"])
            if "performer" in track:
                item["artists"] += [track["performer"]["name"]]
            if track.get("performers"):
                for artist_str in track["performers"].split(" - "):
                    if "Performer" in artist_str or "MainArtist" in artist_str or "Main Artist" in artist_str:
                        artist = artist_str.split(", ")[0]
                        if artist not in item["artists"]:
                            item["artists"].append(artist)
            # append quality score
            if track["hires"] and track["maximum_sampling_rate"] > 96:
                item["quality"] = 27
            elif track["hires"] and track["maximum_sampling_rate"] > 48:
                item["quality"] = 26
            elif track["hires"]:
                item["quality"] = 7
            if track.get("version"):
                item["version"] = track["version"]
            else:
                item["version"] = self.parse_track_version(item["title"], item["album"])
            if 'playlist_track_id' in track:
                item['playlist_track_id'] = track['playlist_track_id']
            result.append(item)
        return result

    def version_match(self, version_left, version_right, album_left, album_right, allow_loose_matching=False):
        ''' double check if the title is not mixed up with some other version '''
        if not version_left and not version_right:
            return True
        
        if self.find_title_match(version_left, version_right, True):
            return True

        # treat video mix/edit the same as radio edit/mix
        if ("radio" in version_left.lower() and "video" in version_right.lower()) or ("radio" in version_right.lower() and "video" in version_left.lower()):
            return True
        
        if allow_loose_matching:
            if version_left and version_right and (version_left.lower() in version_right.lower() or version_right.lower() in version_left.lower()):
                return True
            # fuzzy match version
            for version_str in ["radio", "remaster", "single", "album", "stereo", "english", "explicit", "airplay", "video", "hi-res", "deluxe", "mono", "clean", "acoustic", "live", "original", "short"]:
                if version_str in version_left.lower() and version_str in version_right.lower():
                    return True
            # for allow_phrase in ["radio", "remaster", "english", "explicit", "airplay", "video", "hi-res", "album", "single"]:
            #     if (not version_left and allow_phrase in version_right.lower()) or (not version_right and allow_phrase in version_left.lower()):
            #         return True
            for allow_phrase in ["remaster", "hi-res"]:
                if (not version_left and allow_phrase in version_right.lower()) or (not version_right and allow_phrase in version_left.lower()):
                    return True

            # if album is the same assume same version
            if version_left and album_right and version_left in album_right:
                return True
            if version_right and album_left and version_right in album_left:
                return True
            if not version_left and version_right.lower() in ["radio edit", "radio mix", "album version", "single version"]:
                return True
            if not version_right and version_left.lower() in ["radio edit", "radio mix", "album version", "single version"]:
                return True
            if not version_left and "explicit" in version_right.lower():
                return True

        return False

    def artist_match(self, title_left, title_right):
        ''' double check if the artist is not mixed up with some tribute or musical stuff '''
        for ignore_phrase in ["tribute", "soundtrack", "concert", "movie"]:
            if ignore_phrase not in title_left.lower() and ignore_phrase in title_right.lower():
                return False
        return True

    @staticmethod
    def create_m3u_entry(track_id, track_str, provider):
        ''' create uri to use in m3u file which LMS can understand '''
        if provider == 'FILE':
            uri = track_id
        elif provider == "QOBUZ":
            uri = "qobuz://%s.flac" % track_id
        else:
            uri = "%s://track:%s" % (provider.lower(), track_id)
        m3u_entry = '#EXTURL:%s\n' % uri
        m3u_entry += '#EXTINF:-1,%s\n' % track_str
        m3u_entry += '%s\n' % uri
        return m3u_entry

    @staticmethod
    def get_spotty_binary():
        '''find the correct spotty binary belonging to the platform'''
        import platform
        sp_binary = None
        if platform.system() == "Windows":
            sp_binary = os.path.join(os.path.dirname(__file__), "spotty", "windows", "spotty.exe")
        elif platform.system() == "Darwin":
            # macos binary is x86_64 intel
            sp_binary = os.path.join(os.path.dirname(__file__), "spotty", "darwin", "spotty")
        elif platform.system() == "Linux":
            # try to find out the correct architecture by trial and error
            architecture = platform.machine()
            if architecture.startswith('AMD64') or architecture.startswith('x86_64'):
                # generic linux x86_64 binary
                sp_binary = os.path.join(os.path.dirname(__file__), "spotty", "x86-linux", "spotty-x86_64")
            else:
                sp_binary = os.path.join(os.path.dirname(__file__), "spotty", "arm-linux", "spotty-muslhf")
        return sp_binary

#Main entry point
PlaylistSyncer()