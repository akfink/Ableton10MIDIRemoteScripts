#Embedded file name: HUDControlElement.py
from __future__ import absolute_import
import Live
from _Framework.NotifyingControlElement import NotifyingControlElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE

class HUDControlElement(NotifyingControlElement):

    def __init__(self, parent, osc_sender, index, *a, **k):
        super(NotifyingControlElement, self).__init__(*a, **k)
        self._parent = parent
        self._index = index
        self._parameter_to_map_to = None

    def log(self, msg, force = False):
        if hasattr(self, '_parent'):
            self._parent.log('HUDControlElement::' + msg, force)

    def connect_to(self, parameter):
        self.log('connect_to: ' + str(parameter.name))
        if self._parameter_to_map_to != None:
            self.release_parameter()
        parameter.add_value_listener(self._update_value)
        self._parameter_to_map_to = parameter

    def _update_value(self):
        self.log('_update_value: ' + str(self._parameter_to_map_to.value), True)
        vals = [self._index, self._parameter_to_map_to.value]
        self._parent._hud_state_control.notify_value(vals)

    def release_parameter(self):
        if self._parameter_to_map_to != None:
            self.log('release_parameter: ' + str(self._parameter_to_map_to.name))
            self._parameter_to_map_to.remove_value_listener(self._update_value)
            self._parameter_to_map_to = None

    def reset(self):
        pass
