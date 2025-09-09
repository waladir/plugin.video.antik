# -*- coding: utf-8 -*-
import os
import sys
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin

from xbmcvfs import translatePath
from urllib.parse import quote

import json
import codecs
import time 
from datetime import datetime

from resources.lib.settings import Settings
from resources.lib.api import API
from resources.lib.session import Session
from resources.lib.utils import get_url, plugin_id

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

def manage_channels(label):
    addon = xbmcaddon.Addon()        
    xbmcplugin.setPluginCategory(_handle, label)
    list_item = xbmcgui.ListItem(label = addon.getLocalizedString(300103))
    url = get_url(action='list_channels_edit', label = label + ' / ' + addon.getLocalizedString(300103))  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    list_item = xbmcgui.ListItem(label = addon.getLocalizedString(300104))
    url = get_url(action='list_channels_groups', label = label + ' / ' + addon.getLocalizedString(300104))  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    list_item = xbmcgui.ListItem(label = addon.getLocalizedString(300105))
    url = get_url(action='reset_channels_list')  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    list_item = xbmcgui.ListItem(label = addon.getLocalizedString(300106))
    url = get_url(action='list_channels_list_backups', label = label + ' / ' + addon.getLocalizedString(300106))  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle)

def list_channels_edit(label):
    addon = xbmcaddon.Addon()        
    xbmcplugin.setPluginCategory(_handle, label)
    channels = Channels()
    channels_list = channels.get_channels_list('channel_number', visible_filter = False)
    if len(channels_list) > 0:
        for number in sorted(channels_list.keys()):
            if channels_list[number]['visible'] == True:
                list_item = xbmcgui.ListItem(label=str(number) + ' ' + channels_list[number]['name'])
            else:
                list_item = xbmcgui.ListItem(label='[COLOR=gray]' + str(number) + ' ' + channels_list[number]['name'] + '[/COLOR]')
            if addon.getSetting('use_picons_server') == 'true':
                list_item.setArt({'icon' : 'http://' + addon.getSetting('picons_server_ip') + ':' + addon.getSetting('picons_server_port') + '/picons/' + quote(channels_list[number]['name'])}) 
            url = get_url(action='edit_channel', id = channels_list[number]['id'])
            list_item.addContextMenuItems([(addon.getLocalizedString(300302), 'RunPlugin(plugin://' + plugin_id + '?action=change_channels_numbers&from_number=' + str(number) + '&direction=increase)'),       
                                            (addon.getLocalizedString(300303), 'RunPlugin(plugin://' + plugin_id + '?action=change_channels_numbers&from_number=' + str(number) + '&direction=decrease)'),
                                            (addon.getLocalizedString(300304), 'RunPlugin(plugin://' + plugin_id + '?action=delete_channel&id='  + str(channels_list[number]['id']) + ')')])       
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
        xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)

def edit_channel(id):
    addon = xbmcaddon.Addon()        
    channels = Channels()
    channels_list = channels.get_channels_list('id', visible_filter = False)
    new_num = xbmcgui.Dialog().numeric(0, 'Číslo kanálu', str(channels_list[id]['channel_number']))
    if len(new_num) > 0 and int(new_num) > 0:
        channels_nums = channels.get_channels_list('channel_number', visible_filter = False)
        if int(new_num) in channels_nums:
            xbmcgui.Dialog().notification('Antik TV', 'Číslo kanálu ' + new_num +  addon.getLocalizedString(300212) + channels_nums[int(new_num)]['name'], xbmcgui.NOTIFICATION_ERROR, 5000)
        else:  
            channels.set_number(id = id, number = new_num)

def delete_channel(id):
    channels = Channels()
    channels.delete_channel(id)
    xbmc.executebuiltin('Container.Refresh')

def change_channels_numbers(from_number, direction):
    addon = xbmcaddon.Addon()        
    channels = Channels()
    if direction == 'increase':
        change = xbmcgui.Dialog().numeric(0, addon.getLocalizedString(300305) + ' ' + str(from_number) + ' o: ', str(1))
    else:
        change = xbmcgui.Dialog().numeric(0, addon.getLocalizedString(300306) + ' ' + str(from_number) + ' o: ', str(1))
    if len(change) > 0:
        change = int(change)
        if change > 0:
            if direction == 'decrease':
                change = change * -1
            channels.change_channels_numbers(from_number, change)
            xbmc.executebuiltin('Container.Refresh')
        else:  
            xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300213), xbmcgui.NOTIFICATION_ERROR, 5000)
    else:  
        xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300213), xbmcgui.NOTIFICATION_ERROR, 5000)

def list_channels_list_backups(label):
    xbmcplugin.setPluginCategory(_handle, label)
    addon = xbmcaddon.Addon()
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    channels = Channels()
    backups = channels.get_backups()
    if len(backups) > 0:
        for backup in sorted(backups):
            date_list = backup.replace(addon_userdata_dir, '').replace('channels_backup_', '').replace('.txt', '').split('-')
            item = 'Záloha z ' + date_list[2] + '.' + date_list[1] + '.' + date_list[0] + ' ' + date_list[3] + ':' + date_list[4] + ':' + date_list[5]
            list_item = xbmcgui.ListItem(label = item)
            url = get_url(action='restore_channels', backup = backup)
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
        xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)
    else:
        xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300214), xbmcgui.NOTIFICATION_INFO, 5000)          

def list_channels_groups(label):
    addon = xbmcaddon.Addon()
    xbmcplugin.setPluginCategory(_handle, label)    
    channels_groups = Channels_groups()
    list_item = xbmcgui.ListItem(label='Nová skupina')
    url = get_url(action='add_channel_group', label = 'Nová skupina')  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    if channels_groups.selected == None:
        list_item = xbmcgui.ListItem(label='[B]' + addon.getLocalizedString(300107) + '[/B]')
    else:  
        list_item = xbmcgui.ListItem(label = addon.getLocalizedString(300107))
    url = get_url(action='list_channels_groups', label = 'Kanály / ' + addon.getLocalizedString(300108))  
    list_item.addContextMenuItems([(addon.getLocalizedString(300307), 'RunPlugin(plugin://' + plugin_id + '?action=select_channel_group&group=all)' ,)])       
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)    
    for channels_group in channels_groups.groups:
        if channels_groups.selected == channels_group:
            list_item = xbmcgui.ListItem(label='[B]' + channels_group + '[/B]')                
        else:
            list_item = xbmcgui.ListItem(label=channels_group)
        url = get_url(action='edit_channel_group', group = channels_group, label = addon.getLocalizedString(300108) + ' / ' + channels_group) 
        list_item.addContextMenuItems([(addon.getLocalizedString(300307), 'RunPlugin(plugin://' + plugin_id + '?action=select_channel_group&group=' + quote(channels_group) + ')'), 
                                      (addon.getLocalizedString(300308), 'RunPlugin(plugin://' + plugin_id + '?action=delete_channel_group&group=' + quote(channels_group) + ')')])       
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle,cacheToDisc = False)

def add_channel_group(label):
    addon = xbmcaddon.Addon()
    input = xbmc.Keyboard('', addon.getLocalizedString(300309))
    input.doModal()
    if not input.isConfirmed(): 
        return
    group = input.getText()
    if len(group) == 0:
        xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300216), xbmcgui.NOTIFICATION_ERROR, 5000)
        sys.exit()          
    channels_groups = Channels_groups()
    if group in channels_groups.groups:
        xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300217), xbmcgui.NOTIFICATION_ERROR, 5000)
        sys.exit()          
    channels_groups.add_channels_group(group)    
    xbmc.executebuiltin('Container.Refresh')

def edit_channel_group(group, label):
    addon = xbmcaddon.Addon()
    xbmcplugin.setPluginCategory(_handle, label)    
    channels_groups = Channels_groups()
    channels = Channels()
    channels_list = channels.get_channels_list('name', visible_filter = False)
    list_item = xbmcgui.ListItem(label = addon.getLocalizedString(300109))
    url = get_url(action='edit_channel_group_list_channels', group = group, label = group + ' / ' + addon.getLocalizedString(300109))  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    list_item = xbmcgui.ListItem(label = addon.getLocalizedString(300110))
    url = get_url(action='edit_channel_group_add_all_channels', group = group, label = group + ' / ' + addon.getLocalizedString(300110))   
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    if group in channels_groups.channels:
        for channel in channels_groups.channels[group]:
            if channel in channels_list:
                list_item = xbmcgui.ListItem(label = channels_list[channel]['name'])
                if addon.getSetting('use_picons_server') == 'true':
                    list_item.setArt({'icon' : 'http://' + addon.getSetting('picons_server_ip') + ':' + addon.getSetting('picons_server_port') + '/picons/' + quote(channels_list[channel]['name'])}) 
                url = get_url(action='edit_channel_group', group = group, label = label)  
                list_item.addContextMenuItems([(addon.getLocalizedString(300304), 'RunPlugin(plugin://' + plugin_id + '?action=edit_channel_group_delete_channel&group=' + quote(group) + '&channel='  + quote(channel) + ')',)])       
                xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    xbmcplugin.endOfDirectory(_handle,cacheToDisc = False)

def delete_channel_group(group):
    addon = xbmcaddon.Addon()
    response = xbmcgui.Dialog().yesno(addon.getLocalizedString(300310), addon.getLocalizedString(300311) + ' ' + group + '?', nolabel = 'Ne', yeslabel = 'Ano')
    if response:
        channels_groups = Channels_groups()
        channels_groups.delete_channels_group(group)
        xbmc.executebuiltin('Container.Refresh')

def select_channel_group(group):
    channels_groups = Channels_groups()
    channels_groups.select_group(group)
    xbmc.executebuiltin('Container.Refresh')
    if (not group in channels_groups.channels or len(channels_groups.channels[group]) == 0) and group != 'all':
        xbmcgui.Dialog().notification('Antik TV', 'Vybraná skupina je prázdná', xbmcgui.NOTIFICATION_WARNING, 5000)    

def edit_channel_group_list_channels(group, label):
    addon = xbmcaddon.Addon()
    xbmcplugin.setPluginCategory(_handle, label)  
    channels_groups = Channels_groups()
    channels = Channels()
    channels_list = channels.get_channels_list('channel_number', visible_filter = False)
    for number in sorted(channels_list.keys()):
        if not group in channels_groups.groups or not group in channels_groups.channels or not channels_list[number]['name'] in channels_groups.channels[group]:
            list_item = xbmcgui.ListItem(label=str(number) + ' ' + channels_list[number]['name'])
            if addon.getSetting('use_picons_server') == 'true':
                list_item.setArt({'icon' : 'http://' + addon.getSetting('picons_server_ip') + ':' + addon.getSetting('picons_server_port') + '/picons/' + quote(channels_list[number]['name'])}) 
            url = get_url(action='edit_channel_group_add_channel', group = group, channel = channels_list[number]['name'])  
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle,cacheToDisc = False)

def edit_channel_group_add_channel(group, channel):
    channels_groups = Channels_groups()
    channels_groups.add_channel_to_group(channel, group)
    xbmc.executebuiltin('Container.Refresh')

def edit_channel_group_add_all_channels(group):
    channels_groups = Channels_groups()
    channels_groups.add_all_channels_to_group(group)
    xbmc.executebuiltin('Container.Refresh')

def edit_channel_group_delete_channel(group, channel):
    channels_groups = Channels_groups()
    channels_groups.delete_channel_from_group(channel, group)
    xbmc.executebuiltin('Container.Refresh')

class Channels:
    def __init__(self):
        self.channels = {}    
        self.valid_to = -1
        self.load_channels()

    def set_visibility(self, id, visibility):
        self.channels[id].update({'visible' : visibility})
        self.save_channels()

    def set_number(self, id, number):
        if id in self.channels:
            self.channels[id].update({'channel_number' : int(number)})
        self.save_channels()

    def delete_channel(self, id):
        if id in self.channels:
            del self.channels[id]
        self.save_channels()

    def change_channels_numbers(self, from_number, change):
        from_number = int(from_number)
        change = int(change)
        channels_list = self.get_channels_list('channel_number', visible_filter = False)
        for number in sorted(channels_list.keys(), reverse = True):
            if number >= from_number:
                self.channels[channels_list[number]['id']].update({'channel_number' : int(number)+int(change)})
        self.save_channels()                

    def get_channels_list(self, bykey = None, visible_filter = True):
        channels = {}
        if bykey == None:
            channels = self.channels
        else:
            for channel in self.channels:
                channels.update({self.channels[channel][bykey] : self.channels[channel]})
        for channel in list(channels):
            if visible_filter == True and channels[channel]['visible'] == False:
                del channels[channel]
        return channels

    def get_channels(self):
        addon = xbmcaddon.Addon()        
        channels = {}
        session = Session()
        api = API()
        post = {'type' : 'TV', 'meta' : {'adult' : True, 'promo' : True}}
        response = api.call_api(api = 'channels', method = 'post', data = post, cookies = session.get_cookies())
        if 'data' not in response:
            xbmcgui.Dialog().notification('Antik TV',addon.getLocalizedString(300211), xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit() 
        for channel in response['data']:
            if 'logo' in response['data'][channel]:
                image = response['data'][channel]['logo']
            else:
                image = None
            channels.update({response['data'][channel]['id_content'] : {'id' : response['data'][channel]['id_content'], 'channel_number' : len(channels) + 1, 'antik_number' : int(response['data'][channel]['id']), 'name' : response['data'][channel]['name'], 'logo' : image, 'archive' : response['data'][channel]['meta']['archive'], 'adult' : response['data'][channel]['meta']['adult'], 'radio' : 0, 'visible' : True}})

        if addon.getSetting('enable_radio') == 'true':
            post = {'type' : 'RADIO'}
            response = api.call_api(api = 'channels', method = 'post', data = post, cookies = session.get_cookies())
            if 'data' not in response:
                xbmcgui.Dialog().notification('Antik TV',addon.getLocalizedString(300211), xbmcgui.NOTIFICATION_ERROR, 5000)
                sys.exit() 
            for channel in response['data']:
                if 'logo' in response['data'][channel]:
                    image = response['data'][channel]['logo']
                else:
                    image = None
                channels.update({response['data'][channel]['id_content'] : {'id' : response['data'][channel]['id_content'], 'channel_number' : len(channels) + 1, 'antik_number' : int(response['data'][channel]['id']), 'name' : response['data'][channel]['name'], 'logo' : image, 'archive' : response['data'][channel]['meta']['archive'], 'adult' : response['data'][channel]['meta']['adult'], 'radio' : 1, 'visible' : True}})
        return channels

    def load_channels(self):
        settings = Settings()
        data = settings.load_json_data({'filename' : 'channels.txt', 'description' : 'kanálů'})
        if data is not None:
            data = json.loads(data)
            if 'channels' in data and data['channels'] is not None and len(data['channels']) > 0:
                self.valid_to = int(data['valid_to'])
                channels = data['channels']
                for channel in channels:
                    self.channels.update({channel : channels[channel]})
            else:
                self.channels = {}
                self.valid_to = -1
            if not self.valid_to or self.valid_to == -1 or self.valid_to < int(time.time()):
                self.valid_to = -1
                self.merge_channels()
                self.save_channels()
        else:
            self.channels = {}
            self.merge_channels()
            self.save_channels()

    def save_channels(self):
        addon = xbmcaddon.Addon()
        addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
        filename = os.path.join(addon_userdata_dir, 'channels.txt')
        if os.path.exists(filename):
            self.backup_channels()            
        settings = Settings()
        self.valid_to = int(time.time()) + 60*60*24
        data = json.dumps({'channels' : self.channels, 'valid_to' : self.valid_to})
        settings.save_json_data({'filename' : 'channels.txt', 'description' : 'kanálů'}, data)

    def reset_channels(self):
        addon = xbmcaddon.Addon()
        addon_userdata_dir = translatePath(addon.getAddonInfo('profile')) 
        filename = os.path.join(addon_userdata_dir, 'channels.txt')
        if os.path.exists(filename):
            self.backup_channels()            
        settings = Settings()
        settings.reset_json_data({'filename' : 'channels.txt', 'description' : 'kanálů'})
        self.channels = {}
        self.valid_to = -1
        self.load_channels()
        xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300318), xbmcgui.NOTIFICATION_INFO, 5000)

    def get_backups(self):
        import glob
        backups = []
        addon = xbmcaddon.Addon()
        addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
        backups = sorted(glob.glob(os.path.join(addon_userdata_dir, 'channels_backup_*.txt')))
        return backups

    def backup_channels(self):
        import glob, shutil
        max_backups = 10
        addon = xbmcaddon.Addon()
        addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
        channels = os.path.join(addon_userdata_dir, 'channels.txt')
        suffix = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        filename = os.path.join(addon_userdata_dir, 'channels_backup_' + suffix + '.txt')
        backups = sorted(glob.glob(os.path.join(addon_userdata_dir, 'channels_backup_*.txt')))
        if len(backups) >= max_backups:
            for i in range(len(backups) - max_backups + 1):
                if os.path.exists(backups[i]):
                    os.remove(backups[i]) 
        shutil.copyfile(channels, filename)

    def restore_channels(self, backup):
        addon = xbmcaddon.Addon()
        if os.path.exists(backup):
            try:
                with codecs.open(backup, 'r', encoding='utf-8') as file:
                    for row in file:
                        data = row[:-1]
            except IOError as error:
                if error.errno != 2:
                    xbmcgui.Dialog().notification('Rebi.tv', addon.getLocalizedString(300319), xbmcgui.NOTIFICATION_ERROR, 5000)
            if data is not None:
                try:            
                    data = json.loads(data)
                    if 'valid_to' in data:
                        data['valid_to'] = int(time.time()) + 60*60*24
                        data = json.dumps(data)
                        addon = xbmcaddon.Addon()
                        addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
                        filename = os.path.join(addon_userdata_dir, 'channels.txt')
                        try:
                            with codecs.open(filename, 'w', encoding='utf-8') as file:
                                file.write('%s\n' % data)
                                xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300320), xbmcgui.NOTIFICATION_INFO, 5000) 
                        except IOError:
                            xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300321), xbmcgui.NOTIFICATION_ERROR, 5000)      
                except:
                    xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300319), xbmcgui.NOTIFICATION_ERROR, 5000)
        else:
            xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300322), xbmcgui.NOTIFICATION_ERROR, 5000)      

    def merge_channels(self):
        antik_channels = self.get_channels()
        max_number = 0
        if len(self.channels) > 0:
            max_number = self.channels[max(self.channels, key = lambda channel: self.channels[channel]['channel_number'])]['channel_number']
        for channel in sorted(antik_channels, key = lambda channel: antik_channels[channel]['channel_number']):
            if channel in self.channels:
                if self.channels[channel]['name'] != antik_channels[channel]['name']:
                    self.channels[channel].update({'name' : antik_channels[channel]['name']})
                if self.channels[channel]['antik_number'] != antik_channels[channel]['antik_number']:
                    self.channels[channel].update({'antik_number' : antik_channels[channel]['antik_number']})
                if self.channels[channel]['logo'] != antik_channels[channel]['logo']:
                    self.channels[channel].update({'logo' : antik_channels[channel]['logo']})
                if 'archive' not in self.channels[channel] or self.channels[channel]['archive'] != antik_channels[channel]['archive']:
                    self.channels[channel].update({'archive' : antik_channels[channel]['archive']})                    
                if 'adult' not in self.channels[channel] or self.channels[channel]['adult'] != antik_channels[channel]['adult']:
                    self.channels[channel].update({'adult' : antik_channels[channel]['adult']})                    
                if 'radio' not in self.channels[channel] or self.channels[channel]['radio'] != antik_channels[channel]['radio']:
                    self.channels[channel].update({'radio' : antik_channels[channel]['radio']})                    
            else:
                max_number = max_number + 1
                antik_channels[channel]['channel_number'] = max_number
                self.channels.update({channel : antik_channels[channel]})
        for channel in list(self.channels):
            if channel not in antik_channels:
                del self.channels[channel]

class Channels_groups:
    def __init__(self):
        self.groups = []
        self.channels = {}
        self.selected = None
        self.load_channels_groups()

    def add_channel_to_group(self, channel, group):
        channel_group = []
        channels = Channels()
        channels_list = channels.get_channels_list('channel_number', visible_filter = False)
    
        for number in sorted(channels_list.keys()):
            if (group in self.channels and channels_list[number]['name'] in self.channels[group]) or channels_list[number]['name'] == channel:
                channel_group.append(channels_list[number]['name'])
        if group in self.channels:
            del self.channels[group]
        self.channels.update({group : channel_group})
        self.save_channels_groups()
        if group == self.selected:
            self.select_group(group) 

    def add_all_channels_to_group(self, group):
        channel_group = []
        channels = Channels()
        channels_list = channels.get_channels_list('channel_number', visible_filter = False)
        if group in self.channels:
            del self.channels[group]
        for number in sorted(channels_list.keys()):
            channel_group.append(channels_list[number]['name'])
        self.channels.update({group : channel_group})
        self.save_channels_groups()
        if group == self.selected:
            self.select_group(group) 

    def delete_channel_from_group(self, channel, group):
        self.channels[group].remove(channel)
        self.save_channels_groups()
        if group == self.selected:
            self.select_group(group) 

    def add_channels_group(self, group):
        self.groups.append(group)
        self.save_channels_groups()

    def delete_channels_group(self, group):
        self.groups.remove(group)
        if group in self.channels:
            del self.channels[group]
        if self.selected == group:
            self.selected = None
            self.save_channels_groups()
            self.select_group('all')
        self.save_channels_groups()

    def select_group(self, group):
        channels = Channels()
        if group == 'all':
            self.selected = None
            channels_list = channels.get_channels_list(visible_filter = False)
            for channel in channels_list:
                channels.set_visibility(channel, True)
        else:
            self.selected = group
            if group in self.channels and len(self.channels[group]):
                channels_list = channels.get_channels_list(visible_filter = False)
                for channel in channels_list:
                    if channels_list[channel]['name'] in self.channels[group]:
                        channels.set_visibility(channel, True)
                    else:
                        channels.set_visibility(channel, False)
        self.save_channels_groups()      

    def load_channels_groups(self):
        addon = xbmcaddon.Addon()
        addon_userdata_dir = translatePath(addon.getAddonInfo('profile')) 
        filename = os.path.join(addon_userdata_dir, 'channels_groups.txt')
        try:
            with codecs.open(filename, 'r', encoding='utf-8') as file:
                for line in file:
                    if line[:-1].find(';') != -1:
                        channel_group = line[:-1].split(';')
                        if channel_group[0] in self.channels:
                            groups = self.channels[channel_group[0]]
                            groups.append(channel_group[1])
                            self.channels.update({channel_group[0] : groups})
                        else:
                            self.channels.update({channel_group[0] : [channel_group[1]]})
                    else:
                        group = line[:-1]
                        if group[0] == '*':
                            self.selected = group[1:]
                            self.groups.append(group[1:])
                        else:
                            self.groups.append(group)
        except IOError:
            self.groups = []
            self.channels = {}
            self.selected = None

    def save_channels_groups(self):
        addon = xbmcaddon.Addon()
        addon_userdata_dir = translatePath(addon.getAddonInfo('profile')) 
        filename = os.path.join(addon_userdata_dir, 'channels_groups.txt')
        if(len(self.groups)) > 0:
            try:
                with codecs.open(filename, 'w', encoding='utf-8') as file:
                    for group in self.groups:
                        if group == self.selected:
                            line = '*' + group
                        else:
                            line = group
                        file.write('%s\n' % line)
                    for group in self.groups:
                        if group in self.channels:
                            for channel in self.channels[group]:
                                line = group + ';' + channel
                                file.write('%s\n' % line)
            except IOError:
                xbmcgui.Dialog().notification('Antik TV', 'Chyba uložení skupiny', xbmcgui.NOTIFICATION_ERROR, 5000)      
        else:
            if os.path.exists(filename):
                os.remove(filename) 
