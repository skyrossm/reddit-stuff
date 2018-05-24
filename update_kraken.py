#!/usr/bin/python
import requests
import raven
import praw
import re
from datetime import datetime

client = raven.Client(
    dsn='',

    include_paths=[__name__.split('.', 1)[0]],
)

api_url = 'https://api.twitch.tv/kraken/streams'
headers = {'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': ''}

#login to reddit.
reddit = praw.Reddit(client_id='',
                        client_secret='',
                        password='',
                        user_agent='streamer-update V1.0.0 fby /u/powerjaxx',
                        username='')

#define subreddit
subreddit = reddit.subreddit('')

#get subreddits settings
settings = subreddit.mod.settings()

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






def get_name(ids):
    global names
    api_url = 'https://api.twitch.tv/helix/users'
    headers = {'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': ''}
    payload = {'id': ids}
    r = requests.get(api_url, headers=headers, params=payload)
    data = r.json()
    #print(data)
    names = [x['display_name'] for x in data['data']]

#get_name(ids)

sidebar = '''
-
**Emotes usage guide [](#LUL)**
---

1. Turn subreddit style on.

2. Use this example in your comment.

----------

    [](#LUL)
or

    [LUL](#LUL)

If you want people without the subreddit style turned on to see it


#### [Full list of emotes here](https://www.reddit.com/r/rpclipsgta/wiki/meta/emotes)

--------------------------------

[](https://discord.gg/bkVuuXF)

--------------------------------



**RULES:**
---

1. Do not organize attacks on streamers through the sub-reddit. 

2. No personal attacks against each other.

3. No repost. Search before posting one if you are unsure.

4. Non-GTAVRP content is not allowed.

5. No NSFW images or videos.

6. No racist, sexist, or hate speech.





-------------------------------------------------------------
**Top GTA RP Streamers live**
---
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
^(Last updated {10} (UTC)^)

-------------------------------------------------------------

'''.format(names[0], names[1], names[2], names[3], names[4], names[5], names[6], names[7], names[8], names[9], datetime.utcnow().replace(microsecond=0), viewer_count[0], viewer_count[1], viewer_count[2], viewer_count[3], viewer_count[4], viewer_count[5], viewer_count[6], viewer_count[7],  viewer_count[8], viewer_count[9])



def update_sidebar(names, settings):
    sidebar_contents = settings['description']
    subreddit.mod.update(description=sidebar)



update_sidebar(names, settings)

    

