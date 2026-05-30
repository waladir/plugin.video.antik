# -*- coding: utf-8 -*-
import json
import re

import xbmc
import xbmcaddon
import xbmcgui

QUALITY_HEIGHTS = [1080, 576, 360]

PREFERRED_HEIGHT_PROP = 'antik.preferred_height'

_RES_XY = re.compile(r'(\d+)\s*[x×]\s*(\d+)', re.I)
_RES_P = re.compile(r'(\d+)\s*p\b', re.I)

def _read_target_height():
    addon = xbmcaddon.Addon()
    raw = addon.getSetting('stream_quality') or '0'
    try:
        idx = int(raw)
    except ValueError:
        idx = 0
    if 0 <= idx < len(QUALITY_HEIGHTS):
        return QUALITY_HEIGHTS[idx]
    return QUALITY_HEIGHTS[0]

def apply_to_listitem(list_item):
    target = _read_target_height()
    xbmcgui.Window(10000).setProperty(PREFERRED_HEIGHT_PROP, str(target))
    list_item.setProperty('inputstream.adaptive.stream_selection_type', 'manual-osd')

def _stream_height(stream):
    h = stream.get('height')
    if h:
        return int(h)
    name = stream.get('name', '') or ''
    m = _RES_XY.search(name)
    if m:
        return int(m.group(2))
    m = _RES_P.search(name)
    if m:
        return int(m.group(1))
    return 0

def get_closest_stream_index(streams, target_height):
    if target_height is None or not streams:
        return None
    best_idx = None
    best_diff = None
    for s in streams:
        idx = s.get('index')
        if idx is None:
            continue
        diff = abs(_stream_height(s) - target_height)
        if best_diff is None or diff < best_diff:
            best_diff = diff
            best_idx = idx
    return best_idx

def _active_video_playerid():
    req = {'jsonrpc': '2.0', 'id': 0, 'method': 'Player.GetActivePlayers'}
    resp = json.loads(xbmc.executeJSONRPC(json.dumps(req)))
    for p in resp.get('result') or []:
        if p.get('type') == 'video':
            return p.get('playerid')
    return None

class QualityPlayer(xbmc.Player):
    def __init__(self):
        xbmc.Player.__init__(self)

    def onAVStarted(self):
        try:
            win = xbmcgui.Window(10000)
            target_raw = win.getProperty(PREFERRED_HEIGHT_PROP)
            if not target_raw:
                return
            win.clearProperty(PREFERRED_HEIGHT_PROP)
            target = int(target_raw)
            playerid = _active_video_playerid()
            if playerid is None:
                return
            streams = []
            current_idx = None
            for _ in range(10):
                req = {
                    'jsonrpc': '2.0',
                    'id': 1,
                    'method': 'Player.GetProperties',
                    'params': {
                        'playerid': playerid,
                        'properties': ['videostreams', 'currentvideostream']
                    }
                }
                resp = json.loads(xbmc.executeJSONRPC(json.dumps(req)))
                result = resp.get('result') or {}
                streams = result.get('videostreams') or []
                current_idx = (result.get('currentvideostream') or {}).get('index')
                if len(streams) >= 2:
                    break
                xbmc.sleep(200)
            if len(streams) < 2:
                return
            idx = get_closest_stream_index(streams, target)
            if idx is None or idx == current_idx:
                return
            switch = {
                'jsonrpc': '2.0',
                'id': 2,
                'method': 'Player.SetVideoStream',
                'params': {
                    'playerid': playerid,
                    'stream': idx
                }
            }
            xbmc.executeJSONRPC(json.dumps(switch))
            xbmc.log('Antik TV > quality: switched to videostream idx={} (target ~{}p)'.format(idx, target), xbmc.LOGINFO)
        except Exception as e:
            xbmc.log('Antik TV > quality monitor error: {}'.format(e), xbmc.LOGERROR)
