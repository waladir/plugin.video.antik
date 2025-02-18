# -*- coding: utf-8 -*-
import os
import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from xbmcvfs import translatePath
from resources.lib.session import Session
from resources.lib.utils import get_url, check_settings


def list_settings(label):
    addon = xbmcaddon.Addon()
    _handle = int(sys.argv[1])
    xbmcplugin.setPluginCategory(_handle, label)

    list_item = xbmcgui.ListItem(label = 'Kanály')
    url = get_url(action='manage_channels', label = 'Kanály')  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    list_item = xbmcgui.ListItem(label = addon.getLocalizedString(300101))
    url = get_url(action='list_devices', label = addon.getLocalizedString(300101))  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    list_item = xbmcgui.ListItem(label = addon.getLocalizedString(300102))
    url = get_url(action='addon_settings', label = addon.getLocalizedString(300102))  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    xbmcplugin.endOfDirectory(_handle)

def list_devices(label):
    addon = xbmcaddon.Addon()
    _handle = int(sys.argv[1])
    xbmcplugin.setPluginCategory(_handle, label)    
    session = Session()
    devices = session.get_devices()
    device_id = addon.getSetting('deviceid')
    for id in devices:
        if devices[id]['name'] == device_id:
            list_item = xbmcgui.ListItem(label = '[B]' + devices[id]['name'] + '[/B]')
        else:
            list_item = xbmcgui.ListItem(label = devices[id]['name'])
        url = get_url(action='remove_device', id = id, name = devices[id]['name'])  
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle)

def remove_device(id, name):
    addon = xbmcaddon.Addon()
    response = xbmcgui.Dialog().yesno(addon.getLocalizedString(300300), addon.getLocalizedString(300301) + ' ' + name + '?')
    if response == True:
        session = Session()
        session.delete_device(id, name)
        session.create_session()
        xbmc.executebuiltin('Container.Refresh')

class Settings:
    def __init__(self):
        self.is_settings_ok = check_settings()
           
    def save_json_data(self, file, data):
        addon = xbmcaddon.Addon()
        addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
        if self.is_settings_ok:
            filename = os.path.join(addon_userdata_dir, file['filename'])
            try:
                with open(filename, "w") as f:
                    f.write('%s\n' % data)
            except IOError:
                xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300201) + file['description'], xbmcgui.NOTIFICATION_ERROR, 5000)

    def load_json_data(self, file):
        data = None
        if self.is_settings_ok:
            addon = xbmcaddon.Addon()
            addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
            filename = os.path.join(addon_userdata_dir, file['filename'])
            try:
                with open(filename, "r") as f:
                    for row in f:
                        data = row[:-1]
            except IOError as error:
                if error.errno != 2:
                    xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300202) + file['description'], xbmcgui.NOTIFICATION_ERROR, 5000)
        return data    

    def reset_json_data(self, file):
        if self.is_settings_ok:
            addon = xbmcaddon.Addon()
            addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
            filename = os.path.join(addon_userdata_dir, file['filename'])
            if os.path.exists(filename):
                try:
                    os.remove(filename) 
                except IOError:
                    xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300203) + file['description'], xbmcgui.NOTIFICATION_ERROR, 5000)
