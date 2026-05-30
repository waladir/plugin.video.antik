# -*- coding: utf-8 -*-
import sys
import time

import xbmc
import xbmcaddon

from datetime import datetime, timezone

from resources.lib.iptvsc import generate_epg
from resources.lib.quality import QualityPlayer

tz_offset = int(datetime.now(timezone.utc).astimezone().utcoffset().total_seconds() / 3600)

addon = xbmcaddon.Addon()
monitor = xbmc.Monitor()
quality_player = QualityPlayer()

xbmc.log('Antik TV > service started', xbmc.LOGINFO)

if addon.getSetting('disabled_scheduler') == 'true':
    monitor.waitForAbort()
    sys.exit()

if monitor.waitForAbort(60):
    sys.exit()
if not addon.getSetting('epg_interval'):
    interval = 12*60*60
else:
    interval = int(addon.getSetting('epg_interval')) * 60 * 60
next = time.time() + 5*60

while not monitor.abortRequested():
    if next < time.time():
        if monitor.waitForAbort(3):
            break
        if addon.getSetting('username') and len(addon.getSetting('username')) > 0 and addon.getSetting('password') and len(addon.getSetting('password')) > 0:
            if addon.getSetting('autogen') == 'true':
                generate_epg(show_progress = False)
        if not addon.getSetting('epg_interval'):
            interval = 12 * 60 * 60
        else:
            interval = int(addon.getSetting('epg_interval')) * 60 * 60
        next = time.time() + float(interval)
    if monitor.waitForAbort(1):
        break

addon = None
