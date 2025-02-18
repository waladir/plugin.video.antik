# -*- coding: utf-8 -*-
import os
import sys 
import xbmcgui
import xbmcplugin
import xbmcaddon

from urllib.parse import parse_qsl

from resources.lib.utils import get_url, check_settings
from resources.lib.session import Session
from resources.lib.channels import Channels, manage_channels, list_channels_edit, list_channels_list_backups, edit_channel, delete_channel, change_channels_numbers
from resources.lib.channels import list_channels_groups, add_channel_group, edit_channel_group, edit_channel_group_list_channels, edit_channel_group_add_channel, edit_channel_group_add_all_channels, edit_channel_group_delete_channel, select_channel_group, delete_channel_group
from resources.lib.live import list_live
from resources.lib.archive import list_archive, list_archive_days, list_program
from resources.lib.stream import play_live, play_archive, play_catchup
from resources.lib.settings import list_settings, list_devices, remove_device
from resources.lib.iptvsc import generate_playlist, generate_epg

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

def main_menu():
    addon = xbmcaddon.Addon()
    icons_dir = os.path.join(addon.getAddonInfo('path'), 'resources','images')

    list_item = xbmcgui.ListItem(label = addon.getLocalizedString(300111))
    url = get_url(action='list_live', label = addon.getLocalizedString(300111))  
    list_item.setArt({ 'thumb' : os.path.join(icons_dir , 'livetv.png'), 'icon' : os.path.join(icons_dir , 'livetv.png') })
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    list_item = xbmcgui.ListItem(label = addon.getLocalizedString(300112))
    url = get_url(action='list_archive', label = addon.getLocalizedString(300112))  
    list_item.setArt({ 'thumb' : os.path.join(icons_dir , 'archive.png'), 'icon' : os.path.join(icons_dir , 'archive.png') })
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    if addon.getSetting('hide_settings') != 'true':
        list_item = xbmcgui.ListItem(label = addon.getLocalizedString(300100))
        url = get_url(action='list_settings', label = addon.getLocalizedString(300100))  
        list_item.setArt({ 'thumb' : os.path.join(icons_dir , 'settings.png'), 'icon' : os.path.join(icons_dir , 'settings.png') })
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    xbmcplugin.endOfDirectory(_handle)

def router(paramstring):
    params = dict(parse_qsl(paramstring))
    check_settings() 
    if params:
        if params['action'] == 'list_live':
            list_live(label = params['label'])
        elif params['action'] == 'play_live':
            play_live(id = params['id'])

        elif params['action'] == 'list_archive':
            list_archive(label = params['label'])
        elif params['action'] == 'list_archive_days':
            list_archive_days(id = params['id'], label = params['label'])
        elif params['action'] == 'list_program':
            list_program(id = params['id'], day_min = params['day_min'], label = params['label'])
        elif params['action'] == 'play_archive':
            play_archive(id = params['id'], start = params['start'], stop = params['stop'])

        elif params['action'] == 'manage_channels':
            manage_channels(label = params['label'])
        elif params['action'] == 'reset_channels_list':
            channels = Channels()
            channels.reset_channels()      
        elif params['action'] == 'restore_channels':
            channels = Channels()
            channels.restore_channels(backup = params['backup'])        
        elif params['action'] == 'list_channels_list_backups':
            list_channels_list_backups(label = params['label'])

        elif params['action'] == 'list_channels_edit':
            list_channels_edit(label = params['label'])
        elif params['action'] == 'edit_channel':
            edit_channel(id = params['id'])
        elif params['action'] == 'delete_channel':
            delete_channel(id = params['id'])
        elif params['action'] == 'change_channels_numbers':
            change_channels_numbers(from_number =params['from_number'], direction = params['direction'])

        elif params['action'] == 'list_channels_groups':
            list_channels_groups(label = params['label'])
        elif params['action'] == 'add_channel_group':
            add_channel_group(label = params['label'])
        elif params['action'] == 'edit_channel_group':
            edit_channel_group(group = params['group'], label = params['label'])
        elif params['action'] == 'delete_channel_group':
            delete_channel_group(group = params['group'])
        elif params['action'] == 'select_channel_group':
            select_channel_group(group = params['group'])

        elif params['action'] == 'edit_channel_group_list_channels':
            edit_channel_group_list_channels(group = params['group'], label = params['label'])
        elif params['action'] == 'edit_channel_group_add_channel':
            edit_channel_group_add_channel(group = params['group'], channel = params['channel'])
        elif params['action'] == 'edit_channel_group_add_all_channels':
            edit_channel_group_add_all_channels(group = params['group'])
        elif params['action'] == 'edit_channel_group_delete_channel':
            edit_channel_group_delete_channel(group = params['group'], channel = params['channel'])

        elif params['action'] == 'list_devices':
            list_devices(label = params['label'])
        elif params['action'] == 'remove_device':
            remove_device(id = params['id'], name = params['name'])

        elif params['action'] == 'list_settings':
            list_settings(label = params['label'])
        elif params['action'] == 'addon_settings':
            xbmcaddon.Addon().openSettings()

        elif params['action'] == 'reset_session':
           session = Session()
           session.remove_session()

        elif params['action'] == 'generate_playlist':
            if 'output_file' in params:
                generate_playlist(params['output_file'])
                xbmcplugin.addDirectoryItem(_handle, '1', xbmcgui.ListItem())
                xbmcplugin.endOfDirectory(_handle, succeeded = True)
            else:
                generate_playlist()
        elif params['action'] == 'generate_epg':
            if 'output_file' in params:
                generate_epg(params['output_file'])
                xbmcplugin.addDirectoryItem(_handle, '1', xbmcgui.ListItem())
                xbmcplugin.endOfDirectory(_handle, succeeded = True)
            else:
                generate_epg()
        elif params['action'] == 'iptsc_play_stream':
            if 'catchup_start_ts' in params and 'catchup_end_ts' in params:
                play_catchup(id = params['id'], start_ts = params['catchup_start_ts'], end_ts = params['catchup_end_ts'])
            else:
                play_live(params['id'])

        else:
            raise ValueError('Neznámý parametr: {0}!'.format(paramstring))
    else:
        main_menu()

if __name__ == '__main__':
    router(sys.argv[2][1:])
