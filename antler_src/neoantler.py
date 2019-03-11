#!/usr/bin/python3

import logging.handlers
import os
import sys
import json
import configparser
import spotipy
from spotipy import oauth2
from datetime import datetime


class NeoAntler:
    def __init__(self, sp: spotipy.Spotify):
        self.sp = sp
        self.all_playlists = []
        self.all_tracks = {}
        self._log = logging.getLogger('antler')

    def load_track_index(self, filename):
        """
        Loads the track index from file.
        :param filename:
        :return:
        """
        with open(filename) as file:
            self.all_tracks = json.load(file)

    def fetch_playlists(self):
        """
        Fetches all playlists for the authenticated user from the Spotify API.
        :return:
        """
        playlists_offset = 0

        while True:
            playlists = self.sp.current_user_playlists(limit=50, offset=playlists_offset)
            for playlist in playlists['items']:
                current_list = {
                    'name': playlist['name'],
                    'collaborative': playlist['collaborative'],
                    'public': playlist['public'],
                    'uri': playlist['uri'],
                    'owner_id': playlist['owner']['id'],
                    'tracks': []
                }

                tracks_offset = 0
                while True:
                    playlist_tracks = self.sp.user_playlist_tracks(
                        user=current_list['owner_id'], playlist_id=playlist['id'],
                        fields='items(is_local,track(uri,id,name,artists.name,album.name)),next',
                        limit=100,
                        offset=tracks_offset
                    )
                    for playlist_item in playlist_tracks['items']:
                        track = playlist_item['track']
                        if track:  # Fixed bug; sometimes the Spotify API returns just {'is_local': False, 'track': None}
                            track_id = track['id']
                            self._log.debug('Doing track {}'.format(track_id))

                            # Local tracks doesn't have a Spotify ID, so we'll use its Spotify URI as an ID instead
                            if playlist_item['is_local']:
                                track_id = track['uri']

                            current_list['tracks'].append(track_id)
                            if track_id not in self.all_tracks:
                                self._log.debug('Adding new track {} to track index'.format(track['name']))
                                self.all_tracks[track_id] = {
                                    'name': track['name'],
                                    'artists': [artist['name'] for artist in track['artists']],
                                    'album': track['album']['name']
                                }
                        else:
                            self._log.warning('API returned None for a track in list {}'.format(current_list['name']))

                    if playlist_tracks['next'] is None:
                        break
                    tracks_offset += 100

                self._log.debug('List {} has {} tracks'.format(current_list['name'], len(current_list['tracks'])))
                self.all_playlists.append(current_list)

            if playlists['next'] is None:
                break
            playlists_offset += 50

        self._log.debug('Playlists fetched')
        self._log.debug('Total num lists: {}'.format(len(self.all_playlists)))
        self._log.debug('Total num unique tracks: {}'.format(len(self.all_tracks)))

    def save_track_index(self, filename):
        """
        Saves the track index to a JSON file, if it has been loaded.
        :param filename:
        :return:
        """
        if self.all_tracks:
            with open(filename, 'w') as track_index_file:
                json.dump(obj=self.all_tracks, fp=track_index_file, separators=(',', ':'))

    def dump_track_index(self):
        """
        Returns the track index as a JSON string.
        :return:
        """
        return json.dumps(obj=self.all_tracks, separators=(',', ':'))

    def save_playlists(self, filename):
        """
        Saves the playlists to a JSON file.
        :param filename:
        :return:
        """
        with open(filename, 'w') as playlists_file:
            json.dump(obj=self.all_playlists, fp=playlists_file, separators=(',', ':'))

    def dump_playlists(self):
        """
        Returns the playlists as a JSON string.
        :return:
        """
        return json.dumps(obj=self.all_playlists, separators=(',', ':'))


def main():
    log = logging.getLogger('antler')

    try:
        conf = configparser.ConfigParser()
        conf.read('/etc/antler/antler.conf')

        client_id = conf.get('spotify_oauth', 'client_id')
        client_secret = conf.get('spotify_oauth', 'client_secret')
        username = conf.get('spotify_oauth', 'username')
        redirect_uri = 'http://localhost'
        scope = 'playlist-read-private playlist-read-collaborative'

        backup_dir = conf.get('backup', 'dir')

        log.setLevel(conf.get('log', 'level', fallback='INFO'))
        formatter = logging.Formatter('%(name)s: [%(levelname)s] %(message)s')

        if conf.get('log', 'stdout', fallback='0').lower() in ['1', 'true', 'y', 'yes']:
            stdout_handler = logging.StreamHandler(sys.stdout)
            stdout_handler.setFormatter(formatter)
            log.addHandler(stdout_handler)

        if conf.get('log', 'syslog', fallback='0').lower() in ['1', 'true', 'y', 'yes']:
            syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')
            syslog_handler.setFormatter(formatter)
            log.addHandler(syslog_handler)

    except configparser.Error as ex:
        log.error('Config file error: ' + ex.message)
        sys.exit(1)

    log.info('Antler started')

    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope,
                                           cache_path='/etc/antler/oauth_cache_' + username + '.json')
    token_info = sp_oauth.get_cached_token()
    if token_info is None:
        log.critical('No cached Spotify OAuth2 token found')
        auth_url = sp_oauth.get_authorize_url()
        log.critical('Navigate to: {}'.format(auth_url))
        response = input('Enter the URL you were redirected to: ')
        code = sp_oauth.parse_response_code(response)
        token_info = sp_oauth.get_access_token(code)
        log.critical('Token info: {}'.format(token_info))
        sys.exit(1)

    sp = spotipy.Spotify(auth=token_info['access_token'])
    na = NeoAntler(sp)

    track_index_filename = os.path.join(backup_dir, 'spotify_track_index.json')
    log.debug('Track index path: {}'.format(track_index_filename))
    na.load_track_index(track_index_filename)
    log.debug('Loaded track index ({} tracks)'.format(len(na.all_tracks)))

    log.debug('Fetching playlists')
    na.fetch_playlists()

    playlists_filename = os.path.join(
        backup_dir,
        'spotify_backup_{}_{}.json'.format(sp.me()['id'], datetime.now().strftime('%Y-%m-%d_%H%M'))
    )
    na.save_playlists(playlists_filename)
    log.debug('Playlists saved to file {}'.format(playlists_filename))

    na.save_track_index(track_index_filename)
    log.debug('Track index saved to file {}'.format(track_index_filename))

    log.info('Done backing up {} playlists'.format(len(na.all_playlists)))


if __name__ == '__main__':
    main()
