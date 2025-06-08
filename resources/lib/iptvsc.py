# -*- coding: utf-8 -*-
import sys

import xbmcgui
import xbmcaddon
import xbmcvfs

from datetime import datetime
import time
from urllib.parse import quote

from resources.lib.channels import Channels
from resources.lib.utils import plugin_id, replace_by_html_entity
from resources.lib.epg import get_channels_epg

tz_offset = int((time.mktime(datetime.now().timetuple())-time.mktime(datetime.utcnow().timetuple()))/3600)

def save_file_test():
    addon = xbmcaddon.Addon()  
    try:
        content = ''
        output_dir = addon.getSetting('output_dir')      
        test_file = output_dir + 'test.fil'
        file = xbmcvfs.File(test_file, 'w')
        file.write(bytearray(('test').encode('utf-8')))
        file.close()
        file = xbmcvfs.File(test_file, 'r')
        content = file.read()
        if len(content) > 0 and content == 'test':
            file.close()
            xbmcvfs.delete(test_file)
            return 1  
        file.close()
        xbmcvfs.delete(test_file)
        return 0
    except Exception:
        file.close()
        xbmcvfs.delete(test_file)
        return 0 

def generate_playlist(output_file = ''):
    addon = xbmcaddon.Addon()
    if addon.getSetting('output_dir') is None or len(addon.getSetting('output_dir')) == 0:
        xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300312), xbmcgui.NOTIFICATION_ERROR, 5000)
        sys.exit() 
             
    channels = Channels()
    channels_list = channels.get_channels_list('channel_number')

    if len(output_file) > 0:
        filename = output_file
    else:
        filename = addon.getSetting('output_dir') + 'playlist.m3u'

    if save_file_test() == 0:
        xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300313), xbmcgui.NOTIFICATION_ERROR, 5000)
        return
    try:
        file = xbmcvfs.File(filename, 'w')
        if file == None:
            xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300313), xbmcgui.NOTIFICATION_ERROR, 5000)
        else:
            file.write(bytearray(('#EXTM3U\n').encode('utf-8')))
            for number in sorted(channels_list.keys()):  
                if addon.getSetting('use_picons_server') == 'true':
                    logo = 'http://' + addon.getSetting('picons_server_ip') + ':' + addon.getSetting('picons_server_port') + '/picons/' + quote(channels_list[number]['name'])
                else:
                    logo = channels_list[number]['logo']
                    if logo is None:
                        logo = ''
                if 'archive' not in channels_list[number] or channels_list[number]['archive'] == True:                    
                    if addon.getSetting('catchup_mode') == 'default':
                        line = '#EXTINF:-1 catchup="default" catchup-days="7" catchup-source="plugin://' + plugin_id + '/?action=iptsc_play_stream&id=' + str(channels_list[number]['id']) + '&catchup_start_ts={utc}&catchup_end_ts={utcend}" tvg-chno="' + str(number) + '" tvg-id="' + channels_list[number]['name'] + '" tvh-epg="0" tvg-logo="' + logo + '",' + channels_list[number]['name']
                    else:
                        line = '#EXTINF:-1 catchup="append" catchup-days="7" catchup-source="&catchup_start_ts={utc}&catchup_end_ts={utcend}" tvg-chno="' + str(number) + '" tvg-id="' + channels_list[number]['name'] + '" tvh-epg="0" tvg-logo="' + logo + '",' + channels_list[number]['name']
                else:
                    line = '#EXTINF:-1 tvg-chno="' + str(number) + '" tvg-id="' + channels_list[number]['name'] + '" tvh-epg="0" tvg-logo="' + logo + '",' + channels_list[number]['name']                    
                file.write(bytearray((line + '\n').encode('utf-8')))
                line = 'plugin://' + plugin_id + '/?action=iptsc_play_stream&id=' + str(channels_list[number]['id'])
                if addon.getSetting('isa') == 'true':
                    file.write(bytearray(('#KODIPROP:inputstream=inputstream.ffmpegdirect\n').encode('utf-8')))
                    file.write(bytearray(('#KODIPROP:inputstream.ffmpegdirect.stream_mode=timeshift\n').encode('utf-8')))
                    file.write(bytearray(('#KODIPROP:inputstream.ffmpegdirect.is_realtime_stream=true\n').encode('utf-8')))
                    file.write(bytearray(('#KODIPROP:mimetype=video/mp2t\n').encode('utf-8')))
                file.write(bytearray((line + '\n').encode('utf-8')))
            file.close()
            xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300314), xbmcgui.NOTIFICATION_INFO, 5000)    
    except Exception:
        file.close()
        xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300313), xbmcgui.NOTIFICATION_ERROR, 5000)

def generate_epg(output_file = ''):
    addon = xbmcaddon.Addon()
    channels_ids = []
    channels = Channels()
    channels_list = channels.get_channels_list('channel_number', visible_filter = False)
    channels_list_by_id = channels.get_channels_list('id', visible_filter = False)

    if len(channels_list) > 0:
        if save_file_test() == 0:
            xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300315), xbmcgui.NOTIFICATION_ERROR, 5000)
            return
        output_dir = addon.getSetting('output_dir') 
        try:
            if len(output_file) > 0:
                file = xbmcvfs.File(output_file, 'w')
            else:
                file = xbmcvfs.File(output_dir + 'antik_epg.xml', 'w')
            if file == None:
                xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300315), xbmcgui.NOTIFICATION_ERROR, 5000)
            else:
                file.write(bytearray(('<?xml version="1.0" encoding="UTF-8"?>\n').encode('utf-8')))
                file.write(bytearray(('<tv generator-info-name="EPG grabber">\n').encode('utf-8')))
                content = ''
                for number in sorted(channels_list.keys()):
                    if addon.getSetting('use_picons_server') == 'true':
                        logo = 'http://' + addon.getSetting('picons_server_ip') + ':' + addon.getSetting('picons_server_port') + '/picons/' + quote(channels_list[number]['name'])
                    else:
                        logo = channels_list[number]['logo']
                        if logo is None:
                            logo = ''
                    channels_ids.append(channels_list[number]['id'])
                    channel = channels_list[number]['name']
                    content = content + '    <channel id="' + replace_by_html_entity(channel) + '">\n'
                    content = content + '            <display-name lang="cs">' + replace_by_html_entity(channel) + '</display-name>\n'
                    content = content + '            <icon src="' + logo + '" />\n'
                    content = content + '    </channel>\n'
                file.write(bytearray((content).encode('utf-8')))
                for i in range(0, len(channels_ids), 10):
                    cnt = 0
                    content = ''
                    epg = get_channels_epg(channels = channels_ids[i:i+10])
                    for epg_item in epg:
                        starttime = datetime.fromtimestamp(epg_item['startts']).strftime('%Y%m%d%H%M%S')
                        endtime = datetime.fromtimestamp(epg_item['endts']).strftime('%Y%m%d%H%M%S')
                        content = content + '    <programme start="' + starttime + ' +0' + str(tz_offset) + '00" stop="' + endtime + ' +0' + str(tz_offset) + '00" channel="' + replace_by_html_entity(channels_list_by_id[epg_item['channel_id']]['name']) + '">\n'
                        content = content + '       <title lang="cs">' + replace_by_html_entity(str(epg_item['title'])) + '</title>\n'
                        if epg_item['description'] != None and len(epg_item['description']) > 0:
                            content = content + '       <desc lang="cs">' + replace_by_html_entity(epg_item['description']) + '</desc>\n'
                        if epg_item['genres'] and epg_item['genres'] is not None:
                            for category in epg_item['genres']:
                                content = content + '       <category>' +  replace_by_html_entity(category) + '</category>\n'
                        content = content + '    </programme>\n'
                        cnt = cnt + 1
                        if cnt > 20:
                            file.write(bytearray((content).encode('utf-8')))
                            content = ''
                            cnt = 0
                    file.write(bytearray((content).encode('utf-8')))                          
                file.write(bytearray(('</tv>\n').encode('utf-8')))
                file.close()
                xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300316), xbmcgui.NOTIFICATION_INFO, 5000)    
        except Exception:
            file.close()
            xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300315), xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit()
    else:
        xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300317), xbmcgui.NOTIFICATION_ERROR, 5000)
        sys.exit()
