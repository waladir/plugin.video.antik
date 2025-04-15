# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

import time
import requests

from resources.lib.session import Session
from resources.lib.api import API
from resources.lib.epg import get_channel_epg
from resources.lib.utils import get_api_url

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

def play_catchup(id, start_ts, end_ts):
    start_ts = int(start_ts)
    end_ts = int(end_ts)
    epg = get_channel_epg(id = id, from_ts = start_ts, to_ts = end_ts)
    if start_ts in epg:
        play_archive(id = epg[start_ts]['channel_id'], start = epg[start_ts]['start'], stop = epg[start_ts]['stop'])
    else:
        play_live(id = id)

def play_live(id):
    addon = xbmcaddon.Addon()
    session = Session()
    api = API()
    post = {'channel' : id }
    response = api.call_api(api = 'channel/detail', data = post, method = 'post', cookies = session.get_cookies())
    if 'data' in response and 'streams' in response['data'] and len(response['data']['streams']) > 0:
        url = response['data']['streams'][0]['url']
        list_item = xbmcgui.ListItem(path = url)
        list_item.setProperty('inputstream', 'inputstream.adaptive')
        if response['data']['streams'][0]['playlist'] == 'm3u8':
            list_item.setProperty('inputstream', 'inputstream.adaptive')
            list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
        else:
            list_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
            list_item.setMimeType('application/dash+xml')
        if 'drm' in response['data']['streams'][0]:
            list_item.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
            list_item.setProperty('inputstream.adaptive.license_key', 'https://drm.antik.sk/widevine/key||R{SSM}|')                
        list_item.setContentLookup(False)       
        xbmcplugin.setResolvedUrl(_handle, True, list_item)
    else:
        xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300218), xbmcgui.NOTIFICATION_ERROR, 5000)

def play_archive(id, start, stop):
    addon = xbmcaddon.Addon()
    session = Session()
    api = API()
    post = {'channelIdentifier' : id, 'showStart' : start, 'showStop' : stop}
    response = api.call_api(api = 'archive/verify', data = post, method = 'post', cookies = session.get_cookies())
    if 'showIdentifier' in response and len(response['showIdentifier']) > 0:
        url = get_api_url() + 'archive/playShow/' + response['showIdentifier']
        list_item = xbmcgui.ListItem(path = url)
        list_item.setProperty('inputstream', 'inputstream.adaptive')
        list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
        list_item.setProperty('ResumeTime', '312' )
        list_item.setProperty('TotalTime', '20000' )
        list_item.setContentLookup(False)       
        xbmcplugin.setResolvedUrl(_handle, True, list_item)
    else:
        xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300218), xbmcgui.NOTIFICATION_ERROR, 5000)
