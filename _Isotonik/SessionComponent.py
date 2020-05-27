#Embedded file name: SessionComponent.py
""" (c) 2014-20 Sigabort, Lee Huddleston, Isotonik Studios; admin@sigabort.co, http://sigabort.co, http://www.isotonikstudios.com """
import Live
import math
from _Framework.SessionComponent import SessionComponent as SessionComponentBase
from _Framework.EncoderElement import EncoderElement
from _Framework.InputControlElement import MIDI_CC_TYPE

class SessionComponent(SessionComponentBase):

    def __init__(self, controller, num_tracks = 0, num_scenes = 0, track_bank_size = 1, auto_name = False, enable_skinning = False, *a, **k):
        self._track_bank_size = 1
        super(SessionComponent, self).__init__(num_tracks, num_scenes, auto_name, enable_skinning, *a, **k)
        self._controller = controller
        self._scene = 0
        self._track_bank_size = track_bank_size

    def log(self, msg, force = False):
        if hasattr(self, '_controller'):
            self._controller.log('session: ' + msg, force)

    def _setup_callback_controls(self):
        self._setup_controls()

    def _setup_controls(self):
        self.log('_setup_controls')
        self._track_offset_control = EncoderElement(MIDI_CC_TYPE, 15, 120, Live.MidiMap.MapMode.absolute)
        self._track_offset_control.value = 0
        self._track_offset_control.name = 'Track_Offset'
        self._scene_offset_control = EncoderElement(MIDI_CC_TYPE, 15, 121, Live.MidiMap.MapMode.absolute)
        self._scene_offset_control.value = 0
        self._scene_offset_control.name = 'Scene_Offset'

    def set_offsets(self, track_offset, scene_offset, force = False, update_controller = True):
        self.log('set_offsets: ' + str(track_offset) + ',' + str(scene_offset))
        if track_offset != -1 and scene_offset != -1:
            if hasattr(self, '_track_offset_control') and (self._track_offset_control.value != track_offset or force):
                self.log('Sending track offset: ' + str(track_offset))
                self._track_offset_control.receive_value(track_offset)
                self._track_offset_control.value = track_offset
            if hasattr(self, '_scene_offset_control') and (self._scene_offset_control.value != scene_offset or force):
                self.log('Sending scene offset: ' + str(scene_offset))
                self._scene_offset_control.receive_value(scene_offset)
                self._scene_offset_control.value = scene_offset
                self._scene = scene_offset
        if update_controller and hasattr(self, '_controller') and hasattr(self._controller, '_set_offsets'):
            self._controller._set_offsets(track_offset, scene_offset)
        super(SessionComponent, self).set_offsets(track_offset, scene_offset)

    def set_session_offsets(self, x, y):
        self.log('session: set_session_offsets: ' + str(x) + ',' + str(y))
        if hasattr(self, '_controller'):
            self._controller.set_session_offsets(x, y)

    def _change_offsets(self, track_increment, scene_increment):
        super(SessionComponent, self)._change_offsets(track_increment, scene_increment)

    def _can_bank_left(self):
        res = self._get_minimal_track_offset() > 0
        return res

    def _bank_left(self):
        self.log('_bank_left')
        return self.set_offsets(max(self.track_offset() - self._track_bank_size, 0), self.scene_offset())

    def _can_bank_right(self):
        res = len(self.tracks_to_use()) > self._get_minimal_track_offset() + self._track_bank_size
        return res

    def _bank_right(self):
        self.log('_bank_right')
        return self.set_offsets(self.track_offset() + self._track_bank_size, self.scene_offset())

    def _can_bank_up(self):
        res = super(SessionComponent, self)._can_bank_up()
        return res

    def _bank_up(self):
        res = super(SessionComponent, self)._bank_up()
        self.log('_bank_up: ' + str(res))
        return res

    def _can_bank_down(self):
        res = super(SessionComponent, self)._can_bank_down()
        return res

    def _bank_down(self):
        res = super(SessionComponent, self)._bank_down()
        self.log('_bank_down: ' + str(res))
        return res
