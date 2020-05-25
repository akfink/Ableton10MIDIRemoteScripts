import Live # This allows us (and the Framework methods) to use the Live API on occasion
import time # We will be using time functions for time-stamping our log file outputs

""" All of the Framework files are listed below, but we are only using using some of them in this script (the rest are commented out) """
from _Framework.ButtonElement import ButtonElement # Class representing a button a the controller
#from _Framework.ButtonMatrixElement import ButtonMatrixElement # Class representing a 2-dimensional set of buttons
#from _Framework.ButtonSliderElement import ButtonSliderElement # Class representing a set of buttons used as a slider
from _Framework.ChannelStripComponent import ChannelStripComponent # Class attaching to the mixer of a given track
#from _Framework.ChannelTranslationSelector import ChannelTranslationSelector # Class switches modes by translating the given controls' message channel
from _Framework.ClipSlotComponent import ClipSlotComponent # Class representing a ClipSlot within Live
from _Framework.CompoundComponent import CompoundComponent # Base class for classes encompasing other components to form complex components
from _Framework.ControlElement import ControlElement # Base class for all classes representing control elements on a controller
from _Framework.ControlSurface import ControlSurface # Central base class for scripts based on the new Framework
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent # Base class for all classes encapsulating functions in Live
#from _Framework.DeviceComponent import DeviceComponent # Class representing a device in Live
#from _Framework.DisplayDataSource import DisplayDataSource # Data object that is fed with a specific string and notifies its observers
#from _Framework.EncoderElement import EncoderElement # Class representing a continuous control on the controller
from _Framework.InputControlElement import * # Base class for all classes representing control elements on a controller
#from _Framework.LogicalDisplaySegment import LogicalDisplaySegment # Class representing a specific segment of a display on the controller
from _Framework.MixerComponent import MixerComponent # Class encompassing several channel strips to form a mixer
#from _Framework.ModeSelectorComponent import ModeSelectorComponent # Class for switching between modes, handle several functions with few controls
#from _Framework.NotifyingControlElement import NotifyingControlElement # Class representing control elements that can send values
#from _Framework.PhysicalDisplayElement import PhysicalDisplayElement # Class representing a display on the controller
from _Framework.SceneComponent import SceneComponent # Class representing a scene in Live
from _Framework.SessionComponent import SessionComponent # Class encompassing several scene to cover a defined section of Live's session
from _Framework.SessionZoomingComponent import SessionZoomingComponent # Class using a matrix of buttons to choose blocks of clips in the session
from _Framework.SliderElement import SliderElement # Class representing a slider on the controller
#from _Framework.TrackEQComponent import TrackEQComponent # Class representing a track's EQ, it attaches to the last EQ device in the track
#from _Framework.TrackFilterComponent import TrackFilterComponent # Class representing a track's filter, attaches to the last filter in the track
from _Framework.TransportComponent import TransportComponent # Class encapsulating all functions in Live's transport section

""" Here we define some global variables """
CHANNEL = 0 # Channels are numbered 0 through 15, this script only makes use of one MIDI Channel (Channel 1)
session = None #Global session object - global so that we can manipulate the same session object from within any of our methods
mixer = None #Global mixer object - global so that we can manipulate the same mixer object from within any of our methods

class ProjectX(ControlSurface):
    __module__ = __name__
    __doc__ = " ProjectX keyboard controller script "

    def __init__(self, c_instance):
        """everything except the '_on_selected_track_changed' override and 'disconnect' runs from here"""
        ControlSurface.__init__(self, c_instance)
        self.log_message(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()) + "--------------= ProjectX log opened =--------------") # Writes message into Live's main log file. This is a ControlSurface method.
        self.set_suppress_rebuild_requests(True) # Turn off rebuild MIDI map until after we're done setting up
        self._setup_transport_control() # Run the transport setup part of the script
        self._setup_mixer_control() # Setup the mixer object
        self._setup_session_control()  # Setup the session object

        """ Here is some Live API stuff just for fun """
        app = Live.Application.get_application() # get a handle to the App
        maj = app.get_major_version() # get the major version from the App
        min = app.get_minor_version() # get the minor version from the App
        bug = app.get_bugfix_version() # get the bugfix version from the App
        self.show_message(str(maj) + "." + str(min) + "." + str(bug)) #put them together and use the ControlSurface show_message method to output version info to console

        self.set_suppress_rebuild_requests(False) #Turn rebuild back on, now that we're done setting up

    def _setup_transport_control(self):
        is_momentary = True # We'll only be using momentary buttons here
        transport = TransportComponent() #Instantiate a Transport Component
        """set up the buttons"""
        transport.set_play_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 61)) #ButtonElement(is_momentary, msg_type, channel, identifier) Note that the MIDI_NOTE_TYPE constant is defined in the InputControlElement module
        transport.set_stop_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 63))
        transport.set_record_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 66))
        transport.set_overdub_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 68))
        transport.set_nudge_buttons(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 75), ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 73)) #(up_button, down_button)
        transport.set_tap_tempo_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 78))
        transport.set_metronome_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 80)) #For some reason, in Ver 7.x.x this method's name has no trailing "e" , and must be called as "set_metronom_button()"...
        transport.set_loop_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 82))
        transport.set_punch_buttons(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 85), ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 87)) #(in_button, out_button)
        transport.set_seek_buttons(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 90), ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 92)) # (ffwd_button, rwd_button)
        """set up the sliders"""
        transport.set_tempo_control(SliderElement(MIDI_CC_TYPE, CHANNEL, 26), SliderElement(MIDI_CC_TYPE, CHANNEL, 25)) #(control, fine_control)
        transport.set_song_position_control(SliderElement(MIDI_CC_TYPE, CHANNEL, 24))

    def _setup_mixer_control(self):
        is_momentary = True
        num_tracks = 7 #A mixer is one-dimensional; here we define the width in tracks - seven columns, which we will map to seven "white" notes
        """Here we set up the global mixer""" #Note that it is possible to have more than one mixer...
        global mixer #We want to instantiate the global mixer as a MixerComponent object (it was a global "None" type up until now...)
        mixer = MixerComponent(num_tracks, 2, with_eqs=True, with_filters=True) #(num_tracks, num_returns, with_eqs, with_filters)
        mixer.set_track_offset(0) #Sets start point for mixer strip (offset from left)
        self.song().view.selected_track = mixer.channel_strip(0)._track #set the selected strip to the first track, so that we don't, for example, try to assign a button to arm the master track, which would cause an assertion error
        """set up the mixer buttons"""
        mixer.set_select_buttons(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 56),ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 54)) #left, right track select
        mixer.master_strip().set_select_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 94)) #jump to the master track
        mixer.selected_strip().set_mute_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 42)) #sets the mute ("activate") button
        mixer.selected_strip().set_solo_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 44)) #sets the solo button
        mixer.selected_strip().set_arm_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 46)) #sets the record arm button
        """set up the mixer sliders"""
        mixer.selected_strip().set_volume_control(SliderElement(MIDI_CC_TYPE, CHANNEL, 14)) #sets the continuous controller for volume
        """note that we have split the mixer functions across two scripts, in order to have two session highlight boxes (one red, one yellow), so there are a few things which we are not doing here..."""

    def _setup_session_control(self):
        is_momentary = True
        num_tracks = 1 #single column
        num_scenes = 7 #seven rows, which will be mapped to seven "white" notes
        global session #We want to instantiate the global session as a SessionComponent object (it was a global "None" type up until now...)
        session = SessionComponent(num_tracks, num_scenes) #(num_tracks, num_scenes) A session highlight ("red box") will appear with any two non-zero values
        session.set_offsets(0, 0) #(track_offset, scene_offset) Sets the initial offset of the "red box" from top left
        """set up the session navigation buttons"""
        session.set_select_buttons(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 25), ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 27)) # (next_button, prev_button) Scene select buttons - up &amp; down - we'll also use a second ControlComponent for this (yellow box)
        session.set_scene_bank_buttons(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 51), ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 49)) # (up_button, down_button) This is to move the "red box" up or down (increment track up or down, not screen up or down, so they are inversed)
        #session.set_track_bank_buttons(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 56), ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 54)) # (right_button, left_button) This moves the "red box" selection set left &amp; right. We'll put our track selection in Part B of the script, rather than here...
        session.set_stop_all_clips_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 70))
        session.selected_scene().set_launch_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 30))
        """Here we set up the scene launch assignments for the session"""
        launch_notes = [60, 62, 64, 65, 67, 69, 71] #this is our set of seven "white" notes, starting at C4
        for index in range(num_scenes): #launch_button assignment must match number of scenes
            session.scene(index).set_launch_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, launch_notes[index])) #step through the scenes (in the session) and assign corresponding note from the launch_notes array
        """Here we set up the track stop launch assignment(s) for the session""" #The following code is set up for a longer array (we only have one track, so it's over-complicated, but good for future adaptation)..
        stop_track_buttons = []
        for index in range(num_tracks):
            stop_track_buttons.append(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 58 + index))   #this would need to be adjusted for a longer array (because we've already used the next note numbers elsewhere)
        session.set_stop_track_clip_buttons(tuple(stop_track_buttons)) #array size needs to match num_tracks
        """Here we set up the clip launch assignments for the session"""
        clip_launch_notes = [48, 50, 52, 53, 55, 57, 59] #this is a set of seven "white" notes, starting at C3
        for index in range(num_scenes):
            session.scene(index).clip_slot(0).set_launch_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, clip_launch_notes[index])) #step through scenes and assign a note to first slot of each
        """Here we set up a mixer and channel strip(s) which move with the session"""
        session.set_mixer(mixer) #Bind the mixer to the session so that they move together

    def _on_selected_track_changed(self):
        """This is an override, to add special functionality (we want to move the session to the selected track, when it changes)
        Note that it is sometimes necessary to reload Live (not just the script) when making changes to this function"""
        ControlSurface._on_selected_track_changed(self) # This will run component.on_selected_track_changed() for all components
        """here we set the mixer and session to the selected track, when the selected track changes"""
        selected_track = self.song().view.selected_track #this is how to get the currently selected track, using the Live API
        mixer.channel_strip(0).set_track(selected_track)
        all_tracks = ((self.song().tracks + self.song().return_tracks) + (self.song().master_track,)) #this is from the MixerComponent's _next_track_value method
        index = list(all_tracks).index(selected_track) #and so is this
        session.set_offsets(index, session._scene_offset) #(track_offset, scene_offset); we leave scene_offset unchanged, but set track_offset to the selected track. This allows us to jump the red box to the selected track.

    def disconnect(self):
        """clean things up on disconnect"""
        self.log_message(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()) + "--------------= ProjectX log closed =--------------") #Create entry in log file
        ControlSurface.disconnect(self)
        return None
