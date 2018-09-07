from datetime import datetime
import json
import sys
from pprint import pprint

sys.path.insert(0, "C:\\Users\Magnus\Programmering\spotipy")
import spotipy
from spotipy import util as sputil


_track_index = None
def get_track_index():
    global _track_index

    if _track_index is None:
        with open('spotify_track_index.json') as file:
            _track_index = json.load(file)

    return _track_index


def save_track_index():
    global _track_index
    with open('spotify_track_index.json', 'w') as file:
        json.dump(_track_index, file)


def is_same_track(track1_id, track2_id):
    if track1_id == track2_id:
        return True
    else:
        track_index = get_track_index()
        track1 = track_index.get(track1_id, None)
        track2 = track_index.get(track2_id, None)

        # TODO


def backup_all_playlists(sp: spotipy.Spotify, file=None):
    all_playlists = []
    all_tracks = {}
    playlists_offset = 0

    while True:
        playlists = sp.current_user_playlists(limit=50, offset=playlists_offset)
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
                playlist_tracks = sp.user_playlist_tracks(user=current_list['owner_id'], playlist_id=playlist['id'],
                                                          fields='items(is_local,track(uri,id,name,artists.name,'
                                                                 'album.name)),next',
                                                          limit=100,
                                                          offset=tracks_offset)
                for playlist_item in playlist_tracks['items']:
                    track = playlist_item['track']
                    track_id = track['id']

                    # Local tracks doesn't have a Spotify ID, so we'll use its Spotify URI as an ID instead
                    if playlist_item['is_local']:
                        track_id = track['uri']

                    current_list['tracks'].append(track_id)
                    if track_id not in all_tracks:
                        all_tracks[track_id] = {
                            'name': track['name'],
                            'artists': [artist['name'] for artist in track['artists']],
                            'album': track['album']['name'],
                        }

                if playlist_tracks['next'] is None:
                    break
                tracks_offset += 100

            print('List {} has {} tracks'.format(current_list['name'], len(current_list['tracks'])))
            all_playlists.append(current_list)

        if playlists['next'] is None:
            break
        playlists_offset += 50

    print('Total num lists: {}'.format(len(all_playlists)))
    print('Total num unique tracks: {}'.format(len(all_tracks)))

    def json_dump_compact(obj, fp):
        json.dump(obj=obj, fp=fp, separators=(',', ':'))

    if file is None:
        user_id = sp.me()['id']
        with open('spotify_backup_{}_{}.json'.format(user_id, datetime.now().strftime('%Y-%m-%d_%H%M')), 'w') as file:
            json_dump_compact(all_playlists, file)
    else:
        json_dump_compact(all_playlists, file)

    with open('spotify_track_index.json', 'w') as track_index_file:
        json_dump_compact(all_tracks, track_index_file)


if __name__ == "__main__":
    token = sputil.prompt_for_user_token(username='spotipy')

    sp = spotipy.Spotify(auth=token)

    print('Backing up all lists...')
    backup_all_playlists(sp)
