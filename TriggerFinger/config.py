# uncompyle6 version 3.4.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (v2.7.16:413a49145e, Mar  2 2019, 14:32:10) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/TriggerFinger/config.py
# Compiled at: 2019-04-09 19:23:45
from __future__ import absolute_import, print_function, unicode_literals
from .consts import *
TRANSPORT_CONTROLS = {'STOP': GENERIC_STOP, 
   'PLAY': GENERIC_PLAY, 'REC': GENERIC_REC, 'LOOP': GENERIC_LOOP, 
   'RWD': GENERIC_RWD, 'FFWD': GENERIC_FFWD}
DEVICE_CONTROLS = (
 GENERIC_ENC1, GENERIC_ENC2, GENERIC_ENC3, GENERIC_ENC4,
 GENERIC_ENC5, GENERIC_ENC6, GENERIC_ENC7, GENERIC_ENC8)
VOLUME_CONTROLS = GENERIC_SLIDERS
TRACKARM_CONTROLS = (
 GENERIC_BUT1, GENERIC_BUT2, GENERIC_BUT3, GENERIC_BUT4,
 GENERIC_BUT5, GENERIC_BUT6, GENERIC_BUT7, GENERIC_BUT8)
BANK_CONTROLS = {'TOGGLELOCK': GENERIC_BUT9, 
   'BANKDIAL': -1, 
   'NEXTBANK': -1, 
   'PREVBANK': -1, 'BANK1': -1, 
   'BANK2': -1, 'BANK3': -1, 'BANK4': -1, 'BANK5': -1, 
   'BANK6': -1, 'BANK7': -1, 'BANK8': -1}
PAD_TRANSLATION = (
 (0, 0, 49, 9), (1, 0, 57, 9), (2, 0, 51, 9), (3, 0, 53, 9),
 (0, 1, 56, 9), (1, 1, 39, 9), (2, 1, 42, 9), (3, 1, 46, 9),
 (0, 2, 50, 9), (1, 2, 48, 9), (2, 2, 45, 9), (3, 2, 41, 9),
 (0, 3, 36, 9), (1, 3, 38, 9), (2, 3, 40, 9), (3, 3, 37, 9))
CONTROLLER_DESCRIPTIONS = {'INPUTPORT': 'Trigger', 'OUTPUTPORT': 'Trigger', 'CHANNEL': 9, 'PAD_TRANSLATION': PAD_TRANSLATION}
MIXER_OPTIONS = {'NUMSENDS': 2, 
   'SEND1': (-1, -1, -1, -1, -1, -1, -1, -1), 
   'SEND2': (-1, -1, -1, -1, -1, -1, -1, -1), 
   'MASTERVOLUME': 7}