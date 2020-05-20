import Live # This allows us (and the Framework methods) to use the Live API on occasion
import time # We will be using time functions for time-stamping our log file outputs

""" We are only using using some of the Framework classes them in this script (the rest are not listed here) """
from _Framework.ButtonElement import ButtonElement # Class representing a button a the controller
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
from _Framework.SliderElement import SliderElement # Class representing a slider on the controller
from _Framework.TransportComponent import TransportComponent # Class encapsulating all functions in Live's transport section

""" Here we define some global variables """
CHANNEL = 0 # Channels are numbered 0 through 15, this script only makes use of one MIDI Channel (Channel 1)
session = None #Global session object - global so that we can manipulate the same session object from within our methods
mixer = None #Global mixer object - global so that we can manipulate the same mixer object from within our methods

class ProjectY(ControlSurface):
    __module__ = __name__
    __doc__ = " ProjectY keyboard controller script "

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        self.log_message(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()) + "--------------= ProjectY log opened =--------------") # Writes message into Live's main log file. This is a ControlSurface method.
        self.set_suppress_rebuild_requests(True) # Turn off rebuild MIDI map until after we're done setting up
        self._setup_mixer_control() # Setup the mixer object
        self._setup_session_control()  # Setup the session object
        self.set_suppress_rebuild_requests(False) # Turn rebuild back on, once we're done setting up


    def _setup_mixer_control(self):
        is_momentary = True # We use non-latching buttons (keys) throughout, so we'll set this as a constant
        num_tracks = 7 # Here we define the mixer width in tracks (a mixer has only one dimension)
        global mixer # We want to instantiate the global mixer as a MixerComponent object (it was a global "None" type up until now...)
        mixer = MixerComponent(num_tracks, 0, with_eqs=False, with_filters=False) #(num_tracks, num_returns, with_eqs, with_filters)
        mixer.set_track_offset(0) #Sets start point for mixer strip (offset from left)
        """set up the mixer buttons"""
        self.song().view.selected_track = mixer.channel_strip(0)._track
        #mixer.selected_strip().set_mute_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 42))
        #mixer.selected_strip().set_solo_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 44))
        #mixer.selected_strip().set_arm_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 46))
        track_select_notes = [36, 38, 40, 41, 43, 45, 47] #more note numbers need to be added if num_scenes is increased
        for index in range(num_tracks):
            mixer.channel_strip(index).set_select_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, track_select_notes[index]))

    def _setup_session_control(self):
        is_momentary = True
        num_tracks = 7
        num_scenes = 1
        global session #We want to instantiate the global session as a SessionComponent object (it was a global "None" type up until now...)
        session = SessionComponent(num_tracks, num_scenes) #(num_tracks, num_scenes)
        session.set_offsets(0, 0) #(track_offset, scene_offset) Sets the initial offset of the red box from top left
        """set up the session buttons"""
        session.set_track_bank_buttons(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 39), ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 37)) # (right_button, left_button) This moves the "red box" selection set left & right. We'll use the mixer track selection instead...
        session.set_mixer(mixer) #Bind the mixer to the session so that they move together
        selected_scene = self.song().view.selected_scene #this is from the Live API
        all_scenes = self.song().scenes
        index = list(all_scenes).index(selected_scene)
        session.set_offsets(0, index) #(track_offset, scene_offset)

    def _on_selected_scene_changed(self):
        """This is an override, to add special functionality (we want to move the session to the selected scene, when it changes)"""
        """When making changes to this function on the fly, it is sometimes necessary to reload Live (not just the script)..."""
        ControlSurface._on_selected_scene_changed(self) # This will run component.on_selected_scene_changed() for all components
        """Here we set the mixer and session to the selected track, when the selected track changes"""
        selected_scene = self.song().view.selected_scene #this is how we get the currently selected scene, using the Live API
        all_scenes = self.song().scenes #then get all of the scenes
        index = list(all_scenes).index(selected_scene) #then identify where the selected scene sits in relation to the full list
        session.set_offsets(session._track_offset, index) #(track_offset, scene_offset) Set the session's scene offset to match the selected track (but make no change to the track offset)

    def disconnect(self):
        """clean things up on disconnect"""
        self.log_message(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()) + "--------------= ProjectY log closed =--------------") #Create entry in log file
        ControlSurface.disconnect(self)
        return None
