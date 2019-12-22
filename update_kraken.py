#!/usr/bin/python
import requests
import raven
import praw
import re
import time
from datetime import datetime
import os

client = raven.Client(
    dsn='',

    include_paths=[__name__.split('.', 1)[0]],
)

api_url = 'https://api.twitch.tv/kraken/streams'
headers = {'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': os.environ['TWITCH_CLIENTID']}

#login to reddit.
reddit = praw.Reddit(client_id=os.environ['REDDIT_CLIENTID'],
                     client_secret=os.environ['REDDIT_CLIENTSECRET'],
                     password=os.environ['REDDIT_PASSWORD'],
                     user_agent='mirrorbot V1.1 by /u/powerjaxx and /u/skyrossm',
                     username=os.environ['REDDIT_USERNAME'])

#define subreddit
subreddit = reddit.subreddit(os.environ['REDDIT_SUBREDDIT'])

#get subreddits settings
settings = subreddit.mod.settings()

sidebar = '''
    Streamer | Viewer Count
    ---|---
    [{0}](https://www.twitch.tv/{0}) |{11}
    [{1}](https://www.twitch.tv/{1}) |{12}
    [{2}](https://www.twitch.tv/{2}) |{13}
    [{3}](https://www.twitch.tv/{3}) |{14}
    [{4}](https://www.twitch.tv/{4}) |{15}
    [{5}](https://www.twitch.tv/{5}) |{16}
    [{6}](https://www.twitch.tv/{6}) |{17}
    [{7}](https://www.twitch.tv/{7}) |{18}
    [{8}](https://www.twitch.tv/{8}) |{19}
    [{9}](https://www.twitch.tv/{9}) |{20}
    '''

def fetch_names():
    #payload for api request
    payload = { 'broadcaster_language': 'en', 'game': 'grand theft auto v',}

    #API request
    r = requests.get(api_url, headers=headers, params=payload)

    #JSON response
    data = r.json()
    #print(data)

    #get id's from users that have certain words in their title
    #words = 'rp', 'nopixel'
    names = [x['channel']['display_name'] for x in data['streams'] if any(s in x['channel'].get('status', '').lower() for s in ['nopixel', 'rp', 'roleplay', 'family', 'No Pixel']) and x['broadcast_platform']=='live']
    print(names)


    #gets the viewercounts of the people that certain words in their title
    viewer_count = [x['viewers'] for x in data['streams'] if any(s in x['channel'].get('status', '').lower() for s in ['nopixel', 'rp', 'roleplay', 'family', 'No Pixel']) and x['broadcast_platform']=='live']
    print(viewer_count)
    return sidebar.format(names[0], names[1], names[2], names[3], names[4], names[5], names[6], names[7], names[8], names[9], viewer_count[0], viewer_count[1], viewer_count[2], viewer_count[3], viewer_count[4], viewer_count[5], viewer_count[6], viewer_count[7],  viewer_count[8], viewer_count[9])


def get_name(ids):
    global names
    api_url = 'https://api.twitch.tv/helix/users'
    headers = {'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': os.environ['TWITCH_CLIENTID']}
    payload = {'id': ids}
    r = requests.get(api_url, headers=headers, params=payload)
    data = r.json()
    #print(data)
    names = [x['display_name'] for x in data['data']]

#get_name(ids)


def update_sidebar(updateText):
    custom = None
    widgets = subreddit.widgets
    for widget in widgets.sidebar:
        if isinstance(widget, praw.models.CustomWidget):
            if (widget.shortName == "TOP GTA STREAMERS"):
                custom = widget
                break
    custom.mod.update(text=updateText)


while True:
    update_sidebar(fetch_names())
    print("Updated widget")
    time.sleep(60)

    

