#Embedded file name: OSCControlElement_v2.py
""" (c) 2014-20 Sigabort, Lee Huddleston, Isotonik Studios; admin@sigabort.co, http://sigabort.co, http://www.isotonikstudios.com """
from __future__ import absolute_import
from ableton.v2.control_surface.control_element import NotifyingControlElement

def repr3(input_str):
    try:
        output_st = unicodedata.normalize('NFKD', input_str).encode('ascii', 'ignore')
        if output_st != None:
            return output_st
        return ''
    except:
        x = repr(input_str)
        return x[2:-1]


class OSCControlElement(NotifyingControlElement):
    last_updated = -1

    def __init__(self, parent, osc_sender, index, osc_msg = None, selected_parameter = False, *a, **k):
        super(NotifyingControlElement, self).__init__(*a, **k)
        self._log = False
        self._parent = parent
        self._osc_sender = osc_sender
        self._osc_msg = '/selected_device' if not osc_msg else osc_msg
        self._index = index
        self._selected_parameter = selected_parameter
        self._current_val = -1
        self._parameter_to_map_to = None

    def log(self, msg, force = False):
        if hasattr(self, '_parent'):
            self._parent.log('OSCControlElement::' + msg, force)

    def set_osc_msg(self, msg):
        self._osc_msg = msg

    def send_midi(self, message):
        self.log('send_midi: ' + str(message), self._log)
        super(OSCControlElement, self).send_midi(message)

    def send_osc(self, osc, vals):
        vals = [self._index] + vals
        self.log('send_osc: ' + str(vals), self._log)
        self._osc_sender.sendOSC(self._osc_msg + osc, vals)

    def connect_to(self, parameter):
        self.log('connect_to: ' + repr3(parameter.name))
        if self._parameter_to_map_to != None:
            self.release_parameter()
        identify_sender = True
        parameter.add_value_listener(self._update_value)
        self._parameter_to_map_to = parameter

    def _update_value(self):
        if self._selected_parameter:
            if not self._parent._preditor._is_live_mapping:
                return
            device = self._parameter_to_map_to.canonical_parent
            is_nested, is_macros, rack_name, real_device = self._parent._device_component._is_nested(device, '_update_value')
            is_live, is_vst, is_m4l, is_au = self._parent._device_component._get_device_type(real_device)
            device_name = self._parent._device_component._get_device_name(real_device)
            device_type = 'vst' if is_vst else ('m4l' if is_m4l else ('au' if is_au else ''))
            vals = [device_name,
             device_type,
             rack_name if rack_name else '',
             self._index + 1]
            self.log(self._osc_msg + '/selected_parameter' + ': ' + str(vals), self._log)
            if self._parent._preditor._is_live_mapping:
                self._osc_sender.sendOSC(self._osc_msg + '/selected_parameter', vals)
                OSCControlElement.last_updated = self._index
        else:
            vals = [self._index, self._parameter_to_map_to.value]
            self.log('_update_value: ' + self._osc_msg + '/value' + ': ' + str(vals), self._log)
            self._osc_sender.sendOSC(self._osc_msg + '/value', vals)

    def release_parameter(self):
        if self._parameter_to_map_to != None:
            self.log('release_parameter: ' + repr3(self._parameter_to_map_to.name))
            self._parameter_to_map_to.remove_value_listener(self._update_value)
            self._parameter_to_map_to = None

    def reset(self):
        pass
