#!/usr/bin/python
import requests
import raven
import praw
import re
import time
import random
from datetime import datetime
import os

client = raven.Client(
    dsn='',

    include_paths=[__name__.split('.', 1)[0]],
)

api_url = 'https://api.twitch.tv/kraken/streams?limit=70&language=en'
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
    [{0}](https://www.twitch.tv/{0}) |{10}
    [{1}](https://www.twitch.tv/{1}) |{11}
    [{2}](https://www.twitch.tv/{2}) |{12}
    [{3}](https://www.twitch.tv/{3}) |{13}
    [{4}](https://www.twitch.tv/{4}) |{14}
    [{5}](https://www.twitch.tv/{5}) |{15}
    [{6}](https://www.twitch.tv/{6}) |{16}
    [{7}](https://www.twitch.tv/{7}) |{17}
    [{8}](https://www.twitch.tv/{8}) |{18}
    **Random Streamer:** |[{9}](https://www.twitch.tv/{9})
    '''
oldsidebar = '''
[](https://discord.gg/bkVuuXF)

--------------------------------

**[CLICK HERE FOR RULES](https://www.reddit.com/r/RPClipsGTA/wiki/subreddit/rules)**
---

-------------------------------------------------------------
**Top GTA RP Streamers live**
---
Streamer | Viewer Count
    ---|---
    [{0}](https://www.twitch.tv/{0}) |{10}
    [{1}](https://www.twitch.tv/{1}) |{11}
    [{2}](https://www.twitch.tv/{2}) |{12}
    [{3}](https://www.twitch.tv/{3}) |{13}
    [{4}](https://www.twitch.tv/{4}) |{14}
    [{5}](https://www.twitch.tv/{5}) |{15}
    [{6}](https://www.twitch.tv/{6}) |{16}
    [{7}](https://www.twitch.tv/{7}) |{17}
    [{8}](https://www.twitch.tv/{8}) |{18}
    **Random Streamer:** |[{9}](https://www.twitch.tv/{9})

-------------------------------------------------------------
'''

def contains_word(s, w):
    return (' ' + w + ' ') in (' ' + s + ' ')

def fetch_names():
    #payload for api request
    payload = { 'broadcaster_language': 'en', 'game': 'grand theft auto v',}

    #API request
    r = requests.get(api_url, headers=headers, params=payload)

    #JSON response
    data = r.json()
    #print(data)
    
    #words = 'rp', 'nopixel'
    wordList = ['nopixel', ' rp ', 'roleplay', ' family ', 'no pixel', ' np ', 'no-pixel', 'svrp', 'twitchrp', 'aftermathrp', 'aftermath']

    #backup for streamers with stupid titles
    streamerList = ['Lord_Kebun', 'Ramee', 'dasMEHDI', 'koil', 's0upes', 'NewFaceSuper', 'AfriicanSnowball', 'mantisobagan', 'Madmoiselle', 'Viviana', 'JoeSmitty123', 'Xaphgnok', 'JdotField', 'the_halfhand', 'Choi', 'Armeeof1', 'NotoriousNorman', 'Jayce', 'kfruntrfrunt', 'YoinksOG', 'aXed_U', 'xReklez', 'MasterMisuri', 'Coolio']

    names = [x['channel']['display_name'] for x in data['streams'] if (any(s in x['channel'].get('status', '').lower() for s in wordList) or any(u in x['channel'].get('display_name', '').lower() for u in streamerList)) and x['broadcast_platform']=='live']
    print(names)


    #gets the viewercounts of the people that certain words in their title
    viewer_count = [x['viewers'] for x in data['streams'] if (any(s in x['channel'].get('status', '').lower() for s in wordList) or any(u in x['channel'].get('display_name', '').lower() for u in streamerList)) and x['broadcast_platform']=='live']
    print(viewer_count)
    
    for i in range(10):
        try:
            gotdata = names[i]
        except IndexError:
            names.append(' ')
            viewer_count.append(0)
    
    newlist = sorted(i for i in viewer_count if i <= 250)
    print(newlist)
    if len(newlist) != 0:
        ran = random.choice(newlist)
    else:
        ran = viewer_count[-1]
    newindex = viewer_count.index(ran)
    random_stream = names[newindex]
    
    global sidebartemplate
    
    sidebartemplate = oldsidebar.format(names[0], names[1], names[2], names[3], names[4], names[5], names[6], names[7], names[8], random_stream, viewer_count[0], viewer_count[1], viewer_count[2], viewer_count[3], viewer_count[4], viewer_count[5], viewer_count[6], viewer_count[7],  viewer_count[8])
    return sidebar.format(names[0], names[1], names[2], names[3], names[4], names[5], names[6], names[7], names[8], random_stream, viewer_count[0], viewer_count[1], viewer_count[2], viewer_count[3], viewer_count[4], viewer_count[5], viewer_count[6], viewer_count[7],  viewer_count[8])

print("Beep boop!")

reply_template = '''
[MIRROR: {0}](https://streamable.com/{1})


Credit to {2} for the content.

{3}

-----------------------------
^(I am a bot. Beep Boop)
''' 

def update_sidebar(updateText):
    custom = None
    widgets = subreddit.widgets
    for widget in widgets.sidebar:
        if isinstance(widget, praw.models.CustomWidget):
            if (widget.shortName == "TOP GTA STREAMERS"):
                custom = widget
                break
    custom.mod.update(text=updateText)
    sidebar_contents = settings['description']
    subreddit.mod.update(description=sidebartemplate)
 
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
        clipinfo(clip_url, submission)
        reply_text = reply_template.format(title_clip, shortcode, broadcaster_url, vod_link)
        reply = submission.reply(reply_text)
        reply.mod.distinguish(sticky=True)
        reply.mod.lock()
    else:
        print("Error posting streamable clip")
        pass

def clipinfo(clip_url, submission):
    global broadcaster_url
    global title_clip
    global vod_link
    headers = {'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': os.environ['TWITCH_CLIENTID']}
    if clip_url.startswith('https://clips.twitch.tv'):
        url_end = clip_url[24:]
        print(url_end)
    elif clip_url.startswith('http://clips.twitch.tv'):
        url_end = clip_url[23:]
        print(url_end)
    else:
        pass
    api_url = 'https://api.twitch.tv/kraken/clips/{0}'.format(url_end)
    r = requests.get(api_url, headers=headers)
    json = r.json()
    broadcaster_url = json["broadcaster"]["channel_url"]
    choices = submission.flair.choices()
    template_id = next(x for x in choices
        if x['flair_text_editable'])['flair_template_id']
    submission.flair.select(template_id, json["broadcaster"]["display_name"])
    title_clip = json["title"]
    try:
         vod_link = '[Continue watching](' + json["vod"]["url"] + ')'
    except TypeError:
        print("No vod link")
        vod_link = ''



def process_submission(submission):
    clip_url = submission.url
    sid = submission.id
    if not submission.archived:
        if clip_url.startswith('https://clips.twitch.tv'):
            streamable(clip_url, submission)
        elif clip_url.startswith('http://clips.twitch.tv'):
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

submission_stream = subreddit.stream.submissions(pause_after=-1, skip_existing=True)
while True:
    for submission in submission_stream:
        if submission is None:
            print("No new submissions")
            break
        print(submission.title)
        process_submission(submission)
    update_sidebar(fetch_names())
    print("Updated widget")
    time.sleep(300)

    

