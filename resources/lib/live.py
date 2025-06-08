# -*- coding: utf-8 -*-
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon

from datetime import datetime
from urllib.parse import quote

from resources.lib.channels import Channels 
from resources.lib.epg import get_live_epg, epg_listitem
from resources.lib.utils import get_url

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

def list_live(label):
    addon = xbmcaddon.Addon()
    xbmcplugin.setPluginCategory(_handle, label)
    xbmcplugin.setContent(_handle, 'twshows')
    channels = Channels()
    channels_list = channels.get_channels_list('channel_number')
    epg = get_live_epg()
    for num in sorted(channels_list.keys()):
        if channels_list[num]['id'] in epg:
            epg_item = epg[channels_list[num]['id']]
            list_item = xbmcgui.ListItem(label = channels_list[num]['name'] + ' | ' + epg_item['title'] + ' | ' + datetime.fromtimestamp(epg_item['startts']).strftime('%H:%M') + ' - ' + datetime.fromtimestamp(epg_item['endts']).strftime('%H:%M'))
            if addon.getSetting('use_picons_server') == 'true':
                list_item = epg_listitem(list_item = list_item, epg = epg_item, logo = 'http://' + addon.getSetting('picons_server_ip') + ':' + addon.getSetting('picons_server_port') + '/picons/' + quote(channels_list[num]['name']))
            else:
                list_item = epg_listitem(list_item = list_item, epg = epg_item, logo = None)
        else:
            list_item = xbmcgui.ListItem(label = channels_list[num]['name'])
            list_item.setInfo('video', {'mediatype':'movie', 'title': channels_list[num]['name']}) 
        list_item.setContentLookup(False)          
        list_item.setProperty('IsPlayable', 'true')
        url = get_url(action='play_live', id = channels_list[num]['id'], title = channels_list[num]['name'])
        xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)


