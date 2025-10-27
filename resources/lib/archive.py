# -*- coding: utf-8 -*-
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
    
from datetime import date, datetime, timedelta
import time
from urllib.parse import quote

from resources.lib.utils import get_url, day_translation, day_translation_short
from resources.lib.channels import Channels 
from resources.lib.epg import get_channel_epg, epg_listitem

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

def list_archive(label):
    addon = xbmcaddon.Addon()    
    xbmcplugin.setPluginCategory(_handle, label)
    channels = Channels()
    channels_list = channels.get_channels_list('channel_number')
    for number in sorted(channels_list.keys()):  
        if 'archive' not in channels_list[number] or channels_list[number]['archive'] == True or 'archive_days' not in channels_list[number] or channels_list[number]['archive_days'] != 0:
            if 'archive_days' not in channels_list[number]:
                channels_list[number]['archive_days'] = 7
            list_item = xbmcgui.ListItem(label=channels_list[number]['name'])
            if addon.getSetting('use_picons_server') == 'true':
                list_item.setArt({'icon' : 'http://' + addon.getSetting('picons_server_ip') + ':' + addon.getSetting('picons_server_port') + '/picons/' + quote(channels_list[number]['name'])}) 
            url = get_url(action='list_archive_days', id = channels_list[number]['id'], days = channels_list[number]['archive_days'], label = label + ' / ' + channels_list[number]['name'])  
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)

def list_archive_days(id, label, days):
    xbmcplugin.setPluginCategory(_handle, label)
    for i in range (int(days) + 1):
        day = date.today() - timedelta(days = i)
        if i == 0:
            den_label = 'Dnes'
            den = 'Dnes'
        elif i == 1:
            den_label = 'Včera'
            den = 'Včera'
        else:
            den_label = day_translation_short[day.strftime('%w')] + ' ' + day.strftime('%d.%m')
            den = day_translation[day.strftime('%w')] + ' ' + day.strftime('%d.%m.%Y')
        list_item = xbmcgui.ListItem(label = den)
        url = get_url(action='list_program', id = id, day_min = i, label = label + ' / ' + den_label)  
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)

def list_program(id, day_min, label):
    addon = xbmcaddon.Addon()
    label = label.replace(addon.getLocalizedString(300112) + ' /','')
    xbmcplugin.setPluginCategory(_handle, label)
    xbmcplugin.setContent(_handle, 'twshows')
    today_date = datetime.today() 
    today_start_ts = int(time.mktime(datetime(today_date.year, today_date.month, today_date.day) .timetuple()))
    today_end_ts = today_start_ts + 60*60*24 -1
    if int(day_min) == 0:
        from_ts = today_start_ts - int(day_min)*60*60*24
        to_ts = int(time.mktime(datetime.now().timetuple()))
    else:
        from_ts = today_start_ts - int(day_min)*60*60*24
        to_ts = today_end_ts - int(day_min)*60*60*24
    epg = get_channel_epg(id, from_ts, to_ts)
    for key in sorted(epg.keys(), reverse = False):
        if int(epg[key]['endts']) > int(time.mktime(datetime.now().timetuple()))-60*60*24*(int(day_min) + 1) and int(epg[key]['endts']) < int(time.mktime(datetime.now().timetuple())):
            list_item = xbmcgui.ListItem(label = day_translation_short[datetime.fromtimestamp(epg[key]['startts']).strftime('%w')] + ' ' + datetime.fromtimestamp(epg[key]['startts']).strftime('%d.%m %H:%M') + ' - ' + datetime.fromtimestamp(epg[key]['endts']).strftime('%H:%M') + ' | ' + epg[key]['title'])
            list_item = epg_listitem(list_item = list_item, epg = epg[key], logo = None)
            list_item.setProperty('IsPlayable', 'true')
            list_item.setContentLookup(False)          
            url = get_url(action='play_archive', id = epg[key]['channel_id'], start = epg[key]['start'], stop = epg[key]['stop'])
            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)
