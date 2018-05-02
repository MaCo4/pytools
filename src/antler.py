from pprint import pprint
import spotipy
from spotipy import util as sputil


if __name__ == "__main__":
    token = sputil.prompt_for_user_token(username='spotipy',
                                         scope='playlist-read-collaborative playlist-read-private '
                                               'user-read-playback-state')

    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_playlists()

    for item in results['items']:
        print("Name: {}, num tracks: {}".format(item['name'], item['tracks']['total']))
