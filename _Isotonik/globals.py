#Embedded file name: globals.py
""" (c) 2014-20 Sigabort, Lee Huddleston, Isotonik Studios; admin@sigabort.co, http://sigabort.co, http://www.isotonikstudios.com """
from os import path
import Live
import logging
logger = logging.getLogger(__name__)
import inspect
frm = inspect.stack()[1]
mod = inspect.getmodule(frm[0])
if mod == None:
    mod_name = frm[1]
else:
    mod_name = mod.__name__
max_frames = 10
frame = 0
g_push = False
g_push2 = False
g_apc40 = False
for i in inspect.stack():
    filename = str(i[1])
    if filename.find('Push2') != -1:
        g_push2 = True
    if filename.find('Push') != -1:
        g_push = True
    if filename.find('APC40') != -1:
        g_apc40 = True
    frame += 1
    if frame > 10:
        break

major = Live.Application.get_application().get_major_version()
minor = Live.Application.get_application().get_minor_version()
bugfix = Live.Application.get_application().get_bugfix_version()
g_10 = False
g_10_0_2 = False
g_10_0_4 = False
if major >= 10:
    g_10 = True
    if minor >= 1 or bugfix >= 2:
        g_10_0_2 = True
    if minor >= 1 or bugfix >= 4:
        g_10_0_4 = True
g_path = path.dirname(path.realpath(__file__))
g_v2_api = g_push and g_10
g_mapper = path.isfile(g_path + '/PrEditor/DeviceComponent_Mapping.py') or path.isfile(g_path + '/PrEditor/DeviceComponent_Mapping.pyc')
g_strip = path.isfile(g_path + '/../_Isotonik/DeviceComponent_Strip.py') or path.isfile(g_path + '/../_Isotonik/DeviceComponent_Strip.pyc')
g_hud = False
g_preditor2 = True
ver = str(major) + '.' + str(minor) + '.' + str(bugfix)
logger.info('Isotonik core: ' + g_path + ', v2: ' + str(g_v2_api) + ', ver: ' + str(ver) + ', module: ' + str(mod_name) + ', mapper: ' + str(g_mapper) + ', strip: ' + str(g_strip) + ', Push: ' + str(g_push) + ', Push2: ' + str(g_push2) + ', ACP40: ' + str(g_apc40) + ', Live10: ' + str(g_10) + ', 10.0.2: ' + str(g_10_0_2) + ', 10.0.4: ' + str(g_10_0_4))
