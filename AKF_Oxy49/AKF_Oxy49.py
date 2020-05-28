# AKF custom script for M-Audio Oxygen 61 (blue)
# NOTE: Script assumes MIDI mapping for factory preset 10, except with Buttons C1-C9 changed to toggle by removing CTRL ASSN = 146.



from __future__ import absolute_import, print_function, unicode_literals, with_statement
import Live # This allows us (and the Framework methods) to use the Live API on occasion
import time # We will be using time functions for time-stamping our log file outputs
from functools import partial


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
from _Framework.CompoundElement import CompoundElement
from _Framework.ControlElement import ControlElement
#todo: remove unused classes

""" Here we define some global variables """
CHANNEL = 15 # Channels are numbered 0 through 15, this script only makes use of one MIDI Channel (Channel 1)
session = None #Global session object - global so that we can manipulate the same session object from within our methods
mixer = None #Global mixer object - global so that we can manipulate the same mixer object from within our methods

class AKF_Oxy49(ControlSurface):
    __module__ = __name__
    __doc__ = "MAudio Oxygen 49 MIDI Remote script "

    def __init__(self, c_instance):
        with self.component_guard():
            ControlSurface.__init__(self, c_instance)
            self.log_message(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()) + "+ + ========= AKF_Oxy61 log opened ========= + +")
            # Writes message into Live's main log file. This is a ControlSurface method.
            self.set_suppress_rebuild_requests(True) # Turn off rebuild MIDI map until after we're done setting up

        #paste from Oxygen_3rd_Gen.py
            is_momentary = True
            self._suggested_input_port = 'Oxygen'
            self._suggested_output_port = 'Oxygen'
            self._has_slider_section = True
            self._shift_button = ButtonElement(is_momentary, MIDI_CC_TYPE, GLOBAL_CHANNEL, 57)
            self._shift_button.add_value_listener(self._shift_value)
            self._mixer = SpecialMixerComponent(NUM_TRACKS)
            self._mute_solo_buttons = []
            self._track_up_button = ButtonElement(is_momentary, MIDI_CC_TYPE, GLOBAL_CHANNEL, 111)
            self._track_down_button = ButtonElement(is_momentary, MIDI_CC_TYPE, GLOBAL_CHANNEL, 110)
            self._master_slider = SliderElement(MIDI_CC_TYPE, GLOBAL_CHANNEL, 41)
            for index in range(NUM_TRACKS):
                self._mute_solo_buttons.append(ButtonElement(is_momentary, MIDI_CC_TYPE, GLOBAL_CHANNEL, 49 + index))
                self._mixer.channel_strip(index).set_volume_control(SliderElement(MIDI_CC_TYPE, GLOBAL_CHANNEL, 33 + index))

            self._setup_mixer_control() # Setup the mixer object
            self._setup_session_control()  # Setup the session object

            self.set_suppress_rebuild_requests(False) # Turn rebuild back on, once we're done setting up

    def
