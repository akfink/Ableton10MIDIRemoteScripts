#!/usr/bin/env python

import Live # This allows us (and the Framework methods) to use the Live API on occasion
import time # We will be using time functions for time-stamping our log file outputs

""" We are only using using some of the Framework classes them in this script (the rest are not listed here) """
from _Framework.ButtonElement import ButtonElement # Class representing a button a the controller
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ChannelStripComponent import ChannelStripComponent # Class attaching to the mixer of a given track
from _Framework.ClipSlotComponent import ClipSlotComponent # Class representing a ClipSlot within Live
from _Framework.CompoundComponent import CompoundComponent # Base class for classes encompasing other components to form complex components
from _Framework.ControlElement import ControlElement # Base class for all classes representing control elements on a controller
from _Framework.ControlSurface import ControlSurface # Central base class for scripts based on the new Framework
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent # Base class for all classes encapsulating functions in Live
from _Framework.InputControlElement import * # Base class for all classes representing control elements on a controller
from _Framework.MixerComponent import MixerComponent # Class encompassing several channel strips to form a mixer
from _Framework.SceneComponent import SceneComponent # Class representing a scene in Live
from _Framework.SessionComponent import SessionComponent # Class encompassing several scene to cover a defined section of Live's session
from _Framework.SessionZoomingComponent import SessionZoomingComponent
from _Framework.SliderElement import SliderElement # Class representing a slider on the controller
from _Framework.TransportComponent import TransportComponent # Class encapsulating all functions in Live's transport section
from _Framework.EncoderElement import EncoderElement
from _Framework.DeviceComponent import DeviceComponent

""" Here we define some global variables """
CHANNEL = 15
session = None
mixer = None

class NanoKontrol_NoPan(ControlSurface):
    __module__ = __name__
    __doc__ = " NanoKontrolcontroller script "

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        self.log_message(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()) + "--------------= NanoKontrol log opened =--------------") # Writes message into Live's main log file. This is a ControlSurface method.
        self._send_midi(switchxfader)
        self.set_suppress_rebuild_requests(True)
        self._setup_mixer_control()
        self._setup_session_control()
        self.set_suppress_rebuild_requests(False)

    def handle_sysex(self, midi_bytes):
        self._send_midi(240, 00, 01, 97, 02, 15, 01, 247)
        response = [long(0),long(0)]
        self.log_message(response)

    def _setup_mixer_control(self):
        is_momentary = True
        num_tracks = 8
        global mixer
        mixer = MixerComponent(num_tracks, 0, with_eqs=False, with_filters=False)
        mixer.set_track_offset(0)
        """set up the mixer buttons"""
        self.song().view.selected_track = mixer.channel_strip(0)._track
        master_volume_control = SliderElement(MIDI_CC_TYPE, CHANNEL, 9)
        for index in range(num_tracks):
            mixer.channel_strip(index).set_mute_button(ButtonElement(is_momentary,MIDI_CC_TYPE, CHANNEL, (index+19)))
            mixer.channel_strip(index).set_volume_control(SliderElement(MIDI_CC_TYPE, CHANNEL,(index+1)))
            #mixer.channel_strip(index).set_pan_control(EncoderElement(MIDI_CC_TYPE, CHANNEL, (index+10), Live.MidiMap.MapMode.absolute))
        master_volume_control.name = 'Master_Volume_Control'
        mixer.master_strip().set_volume_control(master_volume_control)

    def _setup_session_control(self):
        is_momentary = True
        self._shift_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 87)
        right_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 0, 107) #78
        left_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 0, 106) #77
        right_button.name = 'Bank_Select_Right_Button'
        left_button.name = 'Bank_Select_Left_Button'
        global session
        session = SessionComponent(8, 40)
        session.name = 'Session_Control'
        session.set_track_bank_buttons(right_button, left_button)
        matrix = ButtonMatrixElement()
        matrix.name = 'Button_Matrix'
        scene_launch_notes = [56,57,58,59,60,61,62,63]
        scene_launch_buttons = [ ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, scene_launch_notes[index]) for index in range(8) ]
        track_stop_buttons = [ ButtonElement(is_momentary,MIDI_CC_TYPE, CHANNEL, (index+28)) for index in range(8) ]
        for index in range(len(scene_launch_buttons)):
            scene_launch_buttons[index].name = 'Scene_'+ str(index) + '_Launch_Button'
        for index in range(len(track_stop_buttons)):
            track_stop_buttons[index].name = 'Track_' + str(index) + '_Stop_Button'
        session.set_stop_track_clip_buttons(tuple(track_stop_buttons))
        for scene_index in range(8):
            scene = session.scene(scene_index)
            scene.name = 'Scene_' + str(scene_index)
            button_row = []
            scene.set_launch_button(scene_launch_buttons[scene_index])
            for track_index in range(7):
                button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, (track_index * (8)) + scene_index)
                button.name = str(track_index) + '_Clip_' + str(scene_index) + '_Button'
                button_row.append(button)
                clip_slot = scene.clip_slot(track_index)
                clip_slot.set_stopped_value(0)
                clip_slot.set_started_value(64)
                clip_slot.set_launch_button(button)

            matrix.add_row(tuple(button_row))

        session.selected_scene().name = 'Selected_Scene'
        session.set_mixer(mixer)
        return None #return session

    def disconnect(self):
        """clean things up on disconnect"""
        self.log_message(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()) + "--------------= NanoKontrolcontroller log closed =--------------") #Create entry in log file
        ControlSurface.disconnect(self)
        return None
