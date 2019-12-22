#!/usr/bin/env python3
import sqlite3
import time
import praw
import requests
from retrying import retry
import raven
import os
import re

client = raven.Client(
    dsn='',

    include_paths=[__name__.split('.', 1)[0]],
)


print("Beep boop!")

reply_template = '''
[MIRROR: {0}](https://streamable.com/{1})


Credit to {2} for the content.

{3}

-----------------------------
^(I am a bot. Beep Boop)
''' 

#@retry(wait_fixed=600000, stop_max_attempt_number=6)
def main():
    print('Loaded App')
    print('logging in....')
    reddit = praw.Reddit(client_id=os.environ['REDDIT_CLIENTID'],
                         client_secret=os.environ['REDDIT_CLIENTSECRET'],
                         password=os.environ['REDDIT_PASSWORD'],
                         user_agent='mirrorbot V1.1 by /u/powerjaxx and /u/skyrossm',
                         username=os.environ['REDDIT_USERNAME'])
    print('retreiving subreddit....')
    subreddit = reddit.subreddit(os.environ['REDDIT_SUBREDDIT'])
    while True:
        for submission in subreddit.stream.submissions(skip_existing=True):
            print('Processing submission...')
            process_submission(submission)
        #try to start stream every hour just in case.
        time.sleep(3600)

def streamable(clip_url, submission):
    api_url = 'https://api.streamable.com/import'
    payload = {'url': clip_url}
    headers = {'User-Agent': 'A bot that creates mirrors of Twitch clips'}
    global shortcode
    r = requests.get(api_url, params=payload, auth=(os.environ['STREAMABLE_USER'], os.environ['STREAMABLE_PW']), headers=headers)
    print(r.status_code)
    if r.status_code == 200:
        json = r.json()
        shortcode = json['shortcode']
        clipinfo(clip_url)
        reply_text = reply_template.format(title_clip, shortcode, broadcaster_url, vod_link)
        reply = submission.reply(reply_text)
        reply.mod.distinguish(sticky=True)
    else:
        pass

def clipinfo(clip_url):
    global broadcaster_url
    global title_clip
    global vod_link
    headers = {'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': os.environ['TWITCH_CLIENTID']}
    if clip_url.startswith('https://clips.twitch.tv'):
        url_end = clip_url[24:]
        print(url_end)
    else:
        pass
    api_url = 'https://api.twitch.tv/kraken/clips/{0}'.format(url_end)
    r = requests.get(api_url, headers=headers)
    json = r.json()
    broadcaster_url = json["broadcaster"]["channel_url"]
    title_clip = json["title"]
    if 'vod' in json:
        if 'url' in json['vod']:
                vod_link = '[Continue watching](' + json["vod"]["url"] + ')'
        else:
            vod_link = ''
    else:
        vod_link = ''



def process_submission(submission):
    clip_url = submission.url
    sid = submission.id
    if not submission.archived:
        if clip_url.startswith('https://clips.twitch.tv'):
            streamable(clip_url, submission)
        elif re.match('https://www.twitch.tv/.*/clip/.*', clip_url):
            new_url = 'https://clips.twitch.tv/' + clip_url.split("clip/")[1]
            print("Fixed broken twitch url");
            #Could also configure to auto remove post
            streamable(new_url, submission)
        print('Replied to {0}'.format(sid))
         #prevent rate limiting (>1 request per second)
        time.sleep(5)
    else:
        pass

if __name__ == '__main__':
    main()
    
