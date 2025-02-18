# -*- coding: utf-8 -*-
import sys
import xbmcaddon
import xbmcgui

import json
import time 

from resources.lib.api import API
from resources.lib.utils import get_api_url, get_session_cookie
import requests

class Session:
    def __init__(self):
        self.valid_to = -1
        self.load_session()

    def create_session(self):
        self.get_token()

    def get_cookies(self):
        if self.sessionid and self.token:
            return {get_session_cookie() : self.sessionid, 'XSRF-TOKEN' : self.token}
        else:
            return {get_session_cookie()  : '', 'XSRF-TOKEN' : ''}

    def get_token(self):
        addon = xbmcaddon.Addon()
        session = requests.Session()
        api = API()
        req = session.get(get_api_url() + 'sanctum/csrf-cookie', headers = api.headers)
        if req.status_code not in [200, 201, 204]:
            xbmcgui.Dialog().notification('Antik TV',addon.getLocalizedString(300206), xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit() 
        post = {'login' : addon.getSetting('username'), 'password' : addon.getSetting('password')} 
        session.post(get_api_url() + 'login', json = post, headers = api.headers)
        cookies = session.cookies.get_dict()
        if req.status_code not in [200, 201, 204] or get_session_cookie() not in cookies or len(cookies[get_session_cookie()]) == 0 or 'XSRF-TOKEN' not in cookies or len(cookies['XSRF-TOKEN']) == 0:
            xbmcgui.Dialog().notification('Antik TV',addon.getLocalizedString(300206), xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit() 
        self.sessionid = cookies[get_session_cookie()]
        self.token = cookies['XSRF-TOKEN']
        self.expires = int(time.time()) + 24 * 60 * 60
        self.save_session()
        self.register_device()

    def register_device(self):
        addon = xbmcaddon.Addon()
        api = API()
        device_id = addon.getSetting('deviceid')
        devices = self.get_devices()
        for device in devices:
            if devices[device]['name'] == device_id:
                self.delete_device(id = device, name = devices[device]['name'])

        response = api.call_api(api = 'user', method = 'get', cookies = self.get_cookies())
        if len(response) == 0 or 'device_id' not in response:
            xbmcgui.Dialog().notification('Antik TV',addon.getLocalizedString(300207), xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit() 
        user_device_id = response['device_id']
        devices = self.get_devices()
        for device in devices:
            if devices[device]['public_id'] == user_device_id:
                post = {'device_id' : int(device), 'newName' : device_id}
                api.call_api(api = 'changeDeviceName', data = post, method = 'post', cookies = self.get_cookies())                
                return
        xbmcgui.Dialog().notification('Antik TV',addon.getLocalizedString(300209), xbmcgui.NOTIFICATION_ERROR, 5000)

    def refresh_session(self):
        api = API()
        cookies = self.get_cookies()
        if len(cookies[get_session_cookie()]) > 0 and len(cookies['XSRF-TOKEN']) > 0:
            api.call_api(api = 'auth/logout', method = 'get', cookies = cookies)
        self.get_token()
    
    def get_devices(self):
        devices = {}
        addon = xbmcaddon.Addon()
        api = API()
        response = api.call_api(api = 'devices', method = 'get', cookies = self.get_cookies())
        if len(response) == 0:
            xbmcgui.Dialog().notification('Antik TV',addon.getLocalizedString(300207), xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit() 
        for device in response:
            if 'id' in device:
                devices.update({device['id'] : {'name' : device['name'], 'public_id' : device['public_id']}})
        if len(devices) == 0:
            xbmcgui.Dialog().notification('Antik TV',addon.getLocalizedString(300207), xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit() 
        return devices

    def delete_device(self, id, name):
        addon = xbmcaddon.Addon()
        api = API()
        post = {'device_id' : int(id), 'device_id_name' : name, 'password' : addon.getSetting('password')}
        api.call_api(api = 'removeDevice', data = post, method = 'post', cookies = self.get_cookies())
        self.remove_session()

    def load_session(self):
        from resources.lib.settings import Settings
        settings = Settings()
        data = settings.load_json_data({'filename' : 'session.txt', 'description' : 'session'})
        if data is not None:
            data = json.loads(data)
            self.sessionid = data['sessionid']
            self.token = data['token']
            self.expires = int(data['expires'])
            if self.expires: 
                if self.expires < int(time.time()):
                    self.refresh_session()
            else:
                self.create_session()
        else:
            self.create_session()

    def save_session(self):
        from resources.lib.settings import Settings
        settings = Settings()
        data = json.dumps({'sessionid' : self.sessionid, 'token' : self.token, 'expires' : self.expires})
        settings.save_json_data({'filename' : 'session.txt', 'description' : 'session'}, data)

    def remove_session(self):
        api = API()
        cookies = self.get_cookies()
        if len(cookies[get_session_cookie()]) > 0 and len(cookies['XSRF-TOKEN']) > 0:
            api.call_api(api = 'auth/logout', method = 'get', cookies = cookies)
        from resources.lib.settings import Settings
        addon = xbmcaddon.Addon()
        settings = Settings()
        settings.reset_json_data({'filename' : 'session.txt', 'description' : 'session'})
        self.valid_to = -1
        self.create_session()
        xbmcgui.Dialog().notification('Antik TV', addon.getLocalizedString(300205), xbmcgui.NOTIFICATION_INFO, 5000)
