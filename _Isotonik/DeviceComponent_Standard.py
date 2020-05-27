#Embedded file name: /Applications/Ableton Live 10 Beta.app/Contents/App-Resources/MIDI Remote Scripts/_Isotonik/DeviceComponent_Standard.py
""" (c) 2014-16 Sigabort, Lee Huddleston, Isotonik Studios; admin@sigabort.co, http://sigabort.co, http://www.isotonikstudios.com """
import Live
import math
from itertools import repeat
from globals import *
if g_mapper:
    from PrEditor.DeviceComponent_Mapping import DeviceComponent_Mapping as PrEditorMapper
else:

    class PrEditorMapper(object):
        pass


if g_hud:
    from _Framework.NotifyingControlElement import NotifyingControlElement
    from _Framework.ButtonMatrixElement import ButtonMatrixElement
    from .HUDControlElement import HUDControlElement
    from .OSCControlElement import OSCControlElement
from _Framework.SubjectSlot import subject_slot_group, Subject
from _Framework.DeviceComponent import DeviceComponent as Framework_DeviceComponentBase
from _Framework.Control import control_list, ButtonControl
from _Framework.ModesComponent import EnablingModesComponent, tomode
from DeviceComponent_Base import DeviceComponent as DeviceComponentBase
from PrEditor.DeviceComponent_Mapping_Standard import DeviceComponent_Mapping_Standard as PrEditorParameterProvider
AMBER_FULL = 127
bank_colours = ['DefaultButton.Green_Full',
 'DefaultButton.Red_Full',
 'DefaultButton.Amber_Full',
 'DefaultButton.Green_Half',
 'DefaultButton.Red_Half',
 'DefaultButton.Amber_Half',
 'DefaultButton.Yellow']

def repr3(input_str):
    try:
        output_st = unicodedata.normalize('NFKD', input_str).encode('ascii', 'ignore')
        if output_st != None:
            return output_st
        return ''
    except:
        x = repr(input_str)
        return x[2:-1]


class DeviceComponent(Framework_DeviceComponentBase, PrEditorMapper, DeviceComponentBase, PrEditorParameterProvider):
    encoder_rings = control_list(ButtonControl, control_count=32, enabled=False)
    parameter_lights = control_list(ButtonControl, control_count=32, enabled=True, color='Device.Parameters', disabled_color='Device.NoDevice')
    device_select = control_list(ButtonControl, control_count=8, enabled=False, color='DefaultButton.On', disabled_color='DefaultButton.Off')
    device_enable = control_list(ButtonControl, control_count=8, enabled=False, color='DefaultButton.On', disabled_color='DefaultButton.Off')
    direct_bank = control_list(ButtonControl, control_count=4, enabled=False, color='DefaultButton.Off', disabled_color='DefaultButton.Off')
    prev_device_button = ButtonControl(color='DefaultButton.Off')
    next_device_button = ButtonControl(color='DefaultButton.Off')
    bank_up_button = ButtonControl(color='DefaultButton.Off')
    bank_down_button = ButtonControl(color='DefaultButton.Off')
    device_button = ButtonControl(color='DefaultButton.Off', enabled=True)
    device_lock_button = ButtonControl(color='DefaultButton.Off', enabled=True)
    strip_button = ButtonControl(color='DefaultButton.Off', enabled=True)

    @staticmethod
    def _get_version():
        return '0' + ('p' if g_mapper else '')

    def __init__(self, parent, num_params = 8, direct_bank = False, mono = True, shared = False, path = None, delayed_update = False, new_skin = False, *a, **k):
        self._parent = parent
        self._use_new_skin = new_skin
        self._mapper = None
        Framework_DeviceComponentBase.__init__(self, *a, **k)
        self._is_osc = hasattr(self._parent, '_osc_control') and self._parent._osc_control
        if not self._is_osc:
            g_hud = False
        self.log('DeviceComponent(STANDARD): num: ' + str(num_params) + ', path: ' + str(path) + ', HUD: ' + str(g_hud) + ', OSC: ' + str(self._is_osc), True)
        if g_mapper:
            PrEditorParameterProvider.__init__(self, parent)
            self.log('****** create mapper(STANDARD): path: ' + str(path), True)
            PrEditorMapper.__init__(self, PrEditorParameterProvider, path, num_params)
        DeviceComponentBase.__init__(self, parent, PrEditorMapper if g_mapper else None, False, num_params, direct_bank, mono, shared, path, delayed_update, new_skin)
        k.pop('feedback_mode', None)
        k.pop('lock_button', None)

        def make_hud_encoder(index, name):
            control = HUDControlElement(self, self._hud_state_control, i)
            control.name = name + '_' + str(i)
            return control

        def make_osc_encoder(index, name, osc_msg):
            control = OSCControlElement(self, self._parent.oscServer, i, osc_msg)
            control.name = name + '_' + str(i)
            return control

        if g_hud:
            self.log('Creating HUD notification', True)
            self._hud_state_control = NotifyingControlElement()
            self._hud_state_control.name = 'HUD_State'
            self._hud_controls = ButtonMatrixElement(rows=[[ make_osc_encoder(i, 'HUD_Control', '/hud') for i in xrange(8) ]])
            self._hud_cs_controls = ButtonMatrixElement(rows=[[ make_osc_encoder(i, 'HUD_CS_Control', '/hudcs') for i in xrange(8) ]])
        self._mono = mono
        for light in self.encoder_rings:
            light.enabled = True

        for light in self.device_select:
            light.enabled = False
            light.color = 'DefaultButton.Off' if self._mono else 'Device.NoDevice'
            light.disabled_color = 'DefaultButton.Off' if self._mono else 'Device.NoDevice'

        for light in self.device_enable:
            light.enabled = False
            light.color = 'DefaultButton.Off' if self._mono else 'Device.NoDevice'
            light.disabled_color = 'DefaultButton.Off' if self._mono else 'Device.NoDevice'

        for light in self.parameter_lights:
            light.enabled = False

    def log(self, msg, force = False):
        if hasattr(self, '_parent'):
            self._parent.log('device: ' + msg, force)

    def msg(self, msg):
        if hasattr(self, '_parent'):
            self._parent.show_message(msg)

    def _shutdown(self):
        if self._mapper:
            PrEditorMapper._shutdown(self)

    def set_num_devices(self, val):
        DeviceComponentBase.set_num_devices(self, val)

    def toggle_skip_racks(self):
        DeviceComponentBase.toggle_skip_racks(self)

    def get_song(self):
        return self.song()

    def enable(self, flag):
        return DeviceComponentBase.enable(self, flag)

    def set_device_lock(self, val, refresh = True, leaving = False):
        DeviceComponentBase.set_device_lock(self, val, refresh, leaving)

    def toggle_device_lock(self):
        DeviceComponentBase.toggle_device_lock(self)

    @direct_bank.pressed
    def direct_bank_button(self, button):
        DeviceComponentBase.do_direct_bank_button(self, button)

    @device_enable.pressed
    def device_enable_button(self, button):
        DeviceComponentBase.do_device_enable_button(self, button)

    @device_select.pressed
    def device_select_button(self, button):
        DeviceComponentBase.dodevice_select_button(self, button)

    @device_lock_button.pressed
    def device_lock_button(self, button):
        DeviceComponentBase.do_device_lock_button(self, button)

    @prev_device_button.pressed
    def prev_device_button(self, button):
        DeviceComponentBase.do_prev_device_button(self, button)

    @next_device_button.pressed
    def next_device_button(self, button):
        DeviceComponentBase.do_next_device_button(self, button)

    @bank_up_button.pressed
    def bank_up_button(self, button):
        DeviceComponentBase.do_bank_up_button(self, button)

    @bank_down_button.pressed
    def bank_down_button(self, button):
        DeviceComponentBase.do_bank_down_button(self, button)

    def set_device_bank(self, bank):
        DeviceComponentBase.set_device_bank(self, bank)

    def _update_direct_bank(self):
        DeviceComponentBase._update_direct_bank(self)

    def _scroll_device_view(self, direction):
        DeviceComponentBase._scroll_device_view(self, direction)

    def select_device(self, index):
        device = self._selected_track.devices[index]
        if self._mapper:
            device, updated = self._mapper._get_real_device(self, device)
        self.get_song().view.select_device(device)
        self.device_num = index

    def calling(self, msg):
        self.log('CALLLLLLLIIIIIINNNNNGGG: ' + msg, True)

    def set_device(self, device):
        super(DeviceComponent, self).set_device(device)
        DeviceComponentBase.set_device(self, device)

    def _notify_device(self, device = None, force = False, clear = False):
        DeviceComponentBase._notify_device(self, device, force, clear)

    def _on_parameters_changed(self):
        super(DeviceComponent, self)._on_parameters_changed()
        self.log('_on_parameters_changed')
        if self._mapper:
            self._mapper._on_parameters_changed(self)

    def _set_current_bank(self):
        DeviceComponentBase._set_current_bank(self)

    def _get_param_details(self):
        if self._mapper:
            self._mapper._get_param_details(self)
            return
        DeviceComponentBase._get_param_details(self)

    def _my_assign_parameters(self, bank_num = -1, is_push = False):
        if self._mapper:
            return self._mapper._my_assign_parameters(self, bank_num, is_push)
        return DeviceComponentBase._my_assign_parameters(self, bank_num, is_push)

    def map_controls(self, is_push = False):
        if self._mapper:
            self._mapper.map_controls(self, is_push)
            return
        DeviceComponentBase.map_controls(self, is_push)

    def refresh(self):
        DeviceComponentBase.refresh(self)

    def on_selected_track_changed(self):
        DeviceComponentBase.on_selected_track_changed(self)

    def update_track_state(self):
        DeviceComponentBase.update_track_state(self)

    @subject_slot_group('value')
    def _on_device_enable(self, param):
        DeviceComponentBase.do_on_device_enable(self, param)

    def set_device_on_off(self, index):
        DeviceComponentBase.set_device_on_off(self, index)

    def _update_select_enable_lights(self, num_devices, selected_device):
        DeviceComponentBase._update_select_enable_lights(self, num_devices, selected_device)

    def _show_strip_state(self, index, track_present, iso_present, state):
        DeviceComponentBase._update_select_enable_lights(self, index, track_present, iso_present, state)

    def _show_device_state(self, index, selected, enabled):
        DeviceComponentBase._show_device_state(self, index, selected, enabled)

    def _show_device_enabled(self, index, flag):
        DeviceComponentBase._show_device_enabled(self, index, flag)

    def _show_device_selected(self, index, flag):
        DeviceComponentBase._show_device_selected(self, index, flag)

    def _get_top_device(self):
        return DeviceComponentBase._get_top_device(self)

    def _update_bank_buttons(self, disable = False):
        DeviceComponentBase._update_bank_buttons(self, disable)

    def set_bank_buttons(self, buttons):
        super(DeviceComponent, self).set_bank_buttons(buttons)
        DeviceComponentBase.set_bank_buttons(self, buttons)

    def _is_banking_enabled(self):
        return True

    def _setup_device_controls(self, active):
        self.log('_setup_device_controls: nop')
        return False

    def _setup_num_device_controls(self, num_devices):
        self.log('_setup_num_device_controls: nop')

    def sub_notify(self, msg, val):
        super(DeviceComponent, self).sub_notify(msg, val)


class DeviceModeComponent(EnablingModesComponent):
    device_mode_button = ButtonControl()

    def __init__(self, parent = None, component = None, direct_bank = False, device_settings_mode = None, *a, **k):
        super(DeviceModeComponent, self).__init__(component, *a, **k)
        self._device_settings_mode = tomode(device_settings_mode)
        self._parent = parent
        self._component = component
        self._direct_bank = direct_bank

    def log(self, msg):
        if hasattr(self, '_parent'):
            self._parent.log(msg)

    @device_mode_button.released_immediately
    def device_mode_button(self, button):
        self.cycle_mode()
        self.log('DeviceModeComponent:released_immediately: mode: ' + str(self.selected_mode))
        if hasattr(self, '_parent'):
            self._parent._on_device_engage(127 if self.selected_mode == 'enabled' else 0)
            self._component.msg('Enter device control mode' if self.selected_mode == 'enabled' else 'Enter mixer mode')
        self._component.enable(True if self.selected_mode == 'enabled' else False)

    @device_mode_button.pressed_delayed
    def device_mode_button(self, button):
        self.log('DeviceModeComponent:pressed_delayed')
        if hasattr(self, '_parent') and hasattr(self._parent, 'device_mode_pressed_delayed'):
            self._parent.device_mode_pressed_delayed()

    @device_mode_button.released_delayed
    def device_mode_button(self, button):
        self.log('DeviceModeComponent:released_delayed')
        if hasattr(self, '_parent') and hasattr(self._parent, 'device_mode_released_delayed'):
            self._parent.device_mode_released_delayed()

    def _update_buttons(self, selected_mode):
        self.log('DeviceModeComponent:_update_buttons: mode: ' + str(selected_mode))
        self.device_mode_button.color = 'DefaultButton.On' if selected_mode == 'enabled' else 'DefaultButton.Off'
        super(DeviceModeComponent, self)._update_buttons(selected_mode)

    def select_master_track(self):
        self.log('select_master_track')
        self.get_song().view.selected_track = self.get_song().master_track
