# -*- coding: utf-8 -*-
from resources.lib.session import Session
from resources.lib.channels import Channels
from resources.lib.api import API
from resources.lib.utils import get_kodi_version

from datetime import datetime
import time

def get_live_epg():
    session = Session()
    api = API()
    epg = []
    post = {'type' : 'TV', 'meta' : {'adult' : True, 'promo' : True}}
    response = api.call_api(api = 'channels', method = 'post', data = post, cookies = session.get_cookies())
    if 'epg' in response:
        for channel in response['epg']:
            if 'content' in channel and channel['content'] is not None:
                for item in channel['content']:
                    startts = int(datetime.fromisoformat(item['Start']).timestamp())
                    endts = int(datetime.fromisoformat(item['Stop']).timestamp())
                    if time.time() >= startts and time.time() <= endts:
                        epg.append({'id' : item['SeriesID'], 'title' : item['Title'], 'channel_id' : channel['id'], 'description' : item['Description'], 'startts' : startts, 'endts' : endts, 'start' : item['Start'], 'stop' : item['Stop'], 'genres' : item['Genres']})
        return epg_api(data = epg, key = 'channel_id')
    else:
        return {}

def get_channel_epg(id, from_ts, to_ts):
    session = Session()
    api = API()
    epg = []
    post = {'date': datetime.fromtimestamp(from_ts).strftime('%Y-%m-%d') ,'offset' : 0, 'limit': 200, 'filter' : [id], 'search' : ''}
    response = api.call_api(api = 'epg/channels', data = post, method = 'post', cookies = session.get_cookies())    
    if len(response) > 0 and 'epg' in response[0]:
        for item in response[0]['epg']:
            startts = int(datetime.fromisoformat(item['Start']).timestamp())
            endts = int(datetime.fromisoformat(item['Stop']).timestamp())
            epg.append({'id' : item['SeriesID'], 'title' : item['Title'], 'channel_id' : item['Channel'], 'description' : item['Description'], 'startts' : startts, 'endts' : endts, 'start' : item['Start'], 'stop' : item['Stop'], 'genres' : item['Genres']})
        return epg_api(data = epg, key = 'startts')
    else:
        return {}

def get_channels_epg(channels):
    today_date = datetime.today() 
    today_start_ts = int(time.mktime(datetime(today_date.year, today_date.month, today_date.day) .timetuple()))
    session = Session()
    api = API()
    epg = []
    for day in range(-7, 7, 1):
        post = {'date': datetime.fromtimestamp(today_start_ts + (day* 60*60*24)).strftime('%Y-%m-%d') ,'offset' : 0, 'limit': 200, 'filter' : channels, 'search' : ''}
        response = api.call_api(api = 'epg/channels', data = post, method = 'post', cookies = session.get_cookies())    
        for channel in response:
            if 'epg' in channel:
                for item in channel['epg']:
                    startts = int(datetime.fromisoformat(item['Start']).timestamp())
                    endts = int(datetime.fromisoformat(item['Stop']).timestamp())
                    epg.append({'id' : item['SeriesID'], 'title' : item['Title'], 'channel_id' : item['Channel'], 'description' : item['Description'], 'startts' : startts, 'endts' : endts, 'start' : item['Start'], 'stop' : item['Stop'], 'genres' : item['Genres']})
    return epg


def epg_api(data, key):
    epg = {}
    channels = Channels()
    channels_list = channels.get_channels_list('id', visible_filter = False)            
    for item in data:
        id = item['id']
        channel_id = item['channel_id']
        title = item['title']
        description = item['description']
        startts = item['startts']
        endts = item['endts']
        start = item['start']
        stop = item['stop']
        genres = item['genres']
        epg_item = {'id' : id, 'title' : title, 'channel_id' : channel_id, 'description' : description, 'startts' : startts, 'endts' : endts, 'start' : start, 'stop' : stop, 'genres' : genres}
        if key == 'startts':
            epg.update({startts : epg_item})
        elif key == 'channel_id':
            epg.update({channel_id : epg_item})
        elif key == 'id':
            epg.update({id : epg_item})
        elif key == 'startts_channel_number':
            if channel_id in channels_list:
                epg.update({int(str(startts)+str(channels_list[channel_id]['channel_number']).zfill(5))  : epg_item})
    return epg

def epg_listitem(list_item, epg, logo):
    kodi_version = get_kodi_version()
    genres = []
    if kodi_version >= 20:
        infotag = list_item.getVideoInfoTag()
        infotag.setMediaType('movie')
    else:
        list_item.setInfo('video', {'mediatype' : 'movie'})    
    if 'description' in epg and len(epg['description']) > 0:
        if kodi_version >= 20:
            infotag.setPlot(epg['description'])
        else:
            list_item.setInfo('video', {'plot': epg['description']})
    if 'genres' in epg and len(epg['genres']) > 0:
        for genre in epg['genres']:      
          genres.append(genre)
        if kodi_version >= 20:
            infotag.setGenres(genres)
        else:
            list_item.setInfo('video', {'genre' : genres})          
    return list_item

