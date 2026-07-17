# -*- coding: utf-8 -*-
import sys

import xbmcgui
import xbmcplugin
import xbmcaddon

from urllib.parse import urlencode
import json

from resources.lib.session import Session
from resources.lib.api import API
from resources.lib.epg import get_channel_epg
from resources.lib.utils import get_api_url, get_isa_version, get_kodi_version, ua
from resources.lib.channels import Channels
from resources.lib.quality import apply_to_listitem as apply_quality

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
    isa = get_isa_version()
    kodi = get_kodi_version()
    addon = xbmcaddon.Addon()
    session = Session()
    api = API()
    channels = Channels()
    channels_list = channels.get_channels_list('id')   
    post = {'channel' : id }
    response = api.call_api(api = 'channel/detail', data = post, method = 'post', cookies = session.get_cookies())

    if 'data' in response and 'streams' in response['data'] and len(response['data']['streams']) > 0:
        url = response['data']['streams'][0]['url']
        
        list_item = xbmcgui.ListItem()
        uses_isa = False
        if response['data']['streams'][0]['playlist'] == 'm3u8':
            if 'radio' not in channels_list[id] or channels_list[id]['radio'] == 0:
                list_item.setProperty('inputstream', 'inputstream.adaptive')
                uses_isa = True
                if kodi < 21:
                    list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
        else:
            list_item.setProperty('inputstream', 'inputstream.adaptive')
            uses_isa = True
            if kodi < 21:
                list_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
            list_item.setMimeType('application/dash+xml')
            
        if uses_isa:
            apply_quality(list_item)
            stream_headers = "Referer=https://webtv.tv&User-Agent=" + ua
            list_item.setProperty('inputstream.adaptive.stream_headers', stream_headers)
            if kodi < 21:
                list_item.setProperty('inputstream.adaptive.manifest_headers', stream_headers)

        if 'drm' in response['data']['streams'][0]:
            license_url = 'https://drm.antik.sk/widevine/key'
            drm_headers = urlencode({'Content-Type': 'application/octet-stream', 'User-Agent': ua})
            
            if isa >= 22:
                drm_config = {
                    'com.widevine.alpha': {'license': {'server_url': license_url, 'req_headers': drm_headers}}}
                list_item.setProperty('inputstream.adaptive.drm', json.dumps(drm_config))
            elif isa >= 21.5:
                list_item.setProperty('inputstream.adaptive.drm_legacy', f'com.widevine.alpha|{license_url}|{drm_headers}')
            else:
                list_item.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
                list_item.setProperty('inputstream.adaptive.license_key', f'{license_url}||R{{SSM}}|{drm_headers}')

        headers = f"Referer=https://webtv.tv&User-Agent={ua}"
        list_item.setProperty('inputstream.adaptive.stream_headers', headers)
        list_item.setProperty('inputstream.adaptive.manifest_update_parameter', f"|{headers}")
        if kodi >= 21:
            url = f"{url}|{headers}"
        
        list_item.setPath(url)
        list_item.setContentLookup(False)       
        xbmcplugin.setResolvedUrl(_handle, True, list_item)
    else:
        xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300218), xbmcgui.NOTIFICATION_ERROR, 5000)


def play_archive(id, start, stop):
    kodi = get_kodi_version()
    addon = xbmcaddon.Addon()
    session = Session()
    api = API()
    channels = Channels()
    channels_list = channels.get_channels_list('id')   
    post = {'channelIdentifier' : id, 'showStart' : start, 'showStop' : stop}
    response = api.call_api(api = 'archive/verify', data = post, method = 'post', cookies = session.get_cookies())
    if 'showIdentifier' in response and len(response['showIdentifier']) > 0:
        url = get_api_url() + 'archive/playShow/' + response['showIdentifier']
        list_item = xbmcgui.ListItem(path = url)
        if 'radio' not in channels_list[id] or channels_list[id]['radio'] == 0:
            list_item.setProperty('inputstream', 'inputstream.adaptive')
            list_item.setProperty('inputstream.adaptive.manifest_headers', 'cookie=' + urlencode(session.get_cookies()))
            if kodi < 21:
                list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
        list_item.setContentLookup(False)       
        xbmcplugin.setResolvedUrl(_handle, True, list_item)
    else:
        xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300218), xbmcgui.NOTIFICATION_ERROR, 5000)
