import argparse
import requests
import youtube_dl
import re
from bs4 import BeautifulSoup
from jsonfinder import jsonfinder
from nested_lookup import nested_lookup

parser = argparse.ArgumentParser(description='Download YouTube videos from a channel using youtube-dl.')
parser.add_argument('channelURL', metavar='YouTube Channel URL', type=str, help='The channel\'s URL')

args = parser.parse_args()

url = args.channelURL


# Check if user input is valid youtube URL
if url.startswith("https://www.youtube.com/channel/") != True:
    print("Input is not valid YouTube channel URL.")
    exit(0)


# remove "/featured" if it exists
url = url.replace('/featured', '')


# stick "/videos" to input URL
if url.endswith("/videos") != True:
    url += "/videos"


# Access le youtube chanel
print("Accessing YouTube channel...\n")
try:
    res = requests.get(url)
except requests.exceptions.RequestException as e:
    raise SystemExit(e)


# Create BeautifulSoup object from html response
print("Parsing YouTube channel...\n")
soup = BeautifulSoup(res.text, 'html.parser')


scripts = soup.find_all('script')
for script in scripts:
    if script.string != None and script.string.find('window["ytInitialData"]') >0:
        for _, __, obj in jsonfinder(script.string, json_only=True):
            if(len(obj))> 2:
                target = nested_lookup('playAllButton', obj)
                playlist_id = target[0]['buttonRenderer']['navigationEndpoint']['watchPlaylistEndpoint']['playlistId']
                playlist_url = "https://youtube.com/playlist?list="+playlist_id

                print("Playlist ID for all videos:")
                print(playlist_id,"\n")
                print("Playlist URL for youtube-dl:")
                print(playlist_url,"\n")


print("Calling youtube-dl...\n")


ydl_opts = {}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([playlist_url])
