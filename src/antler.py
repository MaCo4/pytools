import json
import sys
from pprint import pprint

sys.path.insert(0, "C:\\Users\Magnus\Programmering\spotipy")
import spotipy
from spotipy import util as sputil


def backup_all_playlists(sp: spotipy.Spotify, file=None):
    all_playlists = []
    playlists_offset = 0
    while True:
        playlists = sp.current_user_playlists(limit=50, offset=playlists_offset)
        for playlist in playlists['items']:
            current_list = {
                'name': playlist['name'],
                'collaborative': playlist['collaborative'],
                'public': playlist['public'],
                'uri': playlist['uri'],
                'ownerId': playlist['owner']['id'],
                'tracks': []
            }

            tracks_offset = 0
            while True:
                playlist_tracks = sp.user_playlist_tracks(user=current_list['owner_id'], playlist_id=playlist['id'],
                                                          fields='items.track.uri,next', limit=100,
                                                          offset=tracks_offset)
                for playlist_items in playlist_tracks['items']:
                    current_list['tracks'].append(playlist_items['track']['uri'])

                if playlist_tracks['next'] is None:
                    break
                tracks_offset += 100

            print('List {} has {} tracks'.format(current_list['name'], len(current_list['tracks'])))
            all_playlists.append(current_list)

        if playlists['next'] is None:
            break
        playlists_offset += 50

    print('Total num lists: {}'.format(len(all_playlists)))

    if file is None:
        user_id = sp.me()['id']
        with open('spotify_backup_{}.json'.format(user_id), 'w') as file:
            json.dump(all_playlists, file)
    else:
        json.dump(all_playlists, file)


if __name__ == "__main__":
    token = sputil.prompt_for_user_token(username='spotipy')

    sp = spotipy.Spotify(auth=token)

    print('Backing up all lists...')
    backup_all_playlists(sp)
