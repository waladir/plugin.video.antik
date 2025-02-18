# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon

import requests
from resources.lib.utils import ua, get_api_url

class API:
    def __init__(self):
        self.headers = {'User-Agent' : ua, 'Accept' : '*/*', 'Content-type' : 'application/json;charset=UTF-8'} 

    def call_api(self, api, method, cookies, data = None):
        url = get_api_url() + api
        addon = xbmcaddon.Addon()
        if addon.getSetting('log_request_url') == 'true':
            xbmc.log('Antik TV > ' + str(url))
        try:
            if method == 'get':
                response = requests.get(url = url, cookies = cookies, headers = self.headers)
            elif method == 'post':
                response = requests.post(url = url, json = data, cookies = cookies, headers = self.headers)
            try:
                data = response.json()
            except Exception as e:
                xbmc.log('Antik TV> ' + str(response))
                data = {}
            if addon.getSetting('log_response') == 'true':
                xbmc.log('Antik TV > ' + str(data))
            return data
        except Exception as e:
            xbmc.log('Antik TV > ' + addon.getLocalizedString(300204) + str(url) + ': ' + e.reason)
            return { 'err' : e.reason }  

