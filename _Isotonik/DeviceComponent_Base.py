#Embedded file name: DeviceComponent_Base.py
""" (c) 2014-20 Sigabort, Lee Huddleston, Isotonik Studios; admin@sigabort.co, http://sigabort.co, http://www.isotonikstudios.com """
import Live
import math
from itertools import repeat
from os import path as os_path
from globals import *
if g_hud:
    from _Framework.NotifyingControlElement import NotifyingControlElement
    from _Framework.ButtonMatrixElement import ButtonMatrixElement
    from .HUDControlElement import HUDControlElement
    from .OSCControlElement import OSCControlElement
from _Generic.Devices import device_parameters_to_map, number_of_parameter_banks, parameter_banks, parameter_bank_names, best_of_parameter_bank
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


class DeviceComponent(object):

    def __init__(self, script, mapper = None, is_push = False, num_params = 8, direct_bank = False, mono = True, shared = False, path = None, delayed_update = False, new_skin = False, *a, **k):
        self._script = script
        self._use_new_skin = new_skin
        self._mapper = mapper
        self._is_push = is_push
        self._is_osc = hasattr(self._script, '_osc_control') and self._script._osc_control
        if not self._is_osc:
            g_hud = False
        if is_push:
            self._bank_index = 0
        self.log('DeviceComponentBase: num: ' + str(num_params) + ', path: ' + str(path) + ', HUD: ' + str(g_hud) + ', OSC: ' + str(self._is_osc) + ', is_push: ' + str(is_push) + ', mapper: ' + str(mapper != None))
        self.bank_num = 0
        self.max_bank = 0
        self.num_devices = 0
        self.track_num = 0
        self.device_num = 0
        self._enabled = False
        self._selected_track = None
        self._selected_device = None
        self._skip_racks = True
        self._devices_enable = []
        self._device_locked = False
        self._locked_device = None
        self._allow_direct_select = True
        self._enable_or_select = True
        self._num_params = num_params
        self._direct_bank = direct_bank
        self._log_parameters = False
        self._current_device = None
        self._force_set_device = False
        self._delayed_update = delayed_update
        self._current_banks = {}
        self.my_parameters = []
        self._assign_channel_strip = False
        self._channel_strip_bank = 0
        self._channel_strip_rows = 3
        self._iso_rack_enable = []
        self._mono = mono
        self._shared_enable_select = shared

        def make_hud_encoder(index, name):
            control = HUDControlElement(self, self._hud_state_control, i)
            control.name = name + '_' + str(i)
            return control

        def make_osc_encoder(index, name, osc_msg):
            control = OSCControlElement(self, self._script.oscServer, i, osc_msg)
            control.name = name + '_' + str(i)
            return control

        if g_hud:
            self.log('Creating HUD notification', True)
            self._hud_state_control = self._script._create_notifying_control_element()
            self._hud_state_control.name = 'HUD_State'
            self._hud_controls = ButtonMatrixElement(rows=[[ make_osc_encoder(i, 'HUD_Control', '/hud') for i in xrange(8) ]])
            self._hud_cs_controls = ButtonMatrixElement(rows=[[ make_osc_encoder(i, 'HUD_CS_Control', '/hudcs') for i in xrange(8) ]])

    @staticmethod
    def _get_version():
        return str(DeviceComponent._version) + ('p' if g_mapper else '')

    def log(self, msg, force = False):
        if hasattr(self, '_script'):
            self._script.log('device: ' + msg, force)

    def msg(self, msg):
        if hasattr(self, '_script'):
            self._script.show_message(msg)

    def _shutdown(self):
        if self._mapper:
            self._mapper._shutdown(self)

    def set_num_devices(self, val):
        self.num_devices = val
        self._update_bank_buttons()

    def toggle_skip_racks(self):
        self._skip_racks = not self._skip_racks
        self.log('toggle_skip_racks: ' + str(self._skip_racks))

    def enable(self, flag):
        self.log('DeviceComponent_Base::enable: ' + str(flag))
        self._enabled = flag
        if flag:
            self._force_set_device = True
            self.update_track_state()
        else:
            self._current_device = None

    def set_device_lock(self, val, refresh = True, leaving = False):
        self.log('set_device_lock: ' + str(val) + ', refresh: ' + str(refresh) + ', leaving: ' + str(leaving))
        if self._device_locked == val:
            return
        if self._selected_device == None:
            self.log('set_device_lock: No device: locked: ' + str(self._device_locked))
            if not self._device_locked:
                return
            val = False
        self._device_locked = val
        if val:
            self._locked_device = self._selected_device
            self.log('locked_device: ' + repr3(self._locked_device.name))
        else:
            self.log('locked_device: None')
            self._locked_device = None
        self.set_lock_to_device(self._device_locked, self._selected_device)
        self.device_button.color = 'DefaultButton.On' if self._device_locked else 'DefaultButton.Off'
        if refresh and not self._device_locked:
            new_device = self.get_song().view.selected_track.view.selected_device
            new_name = repr3(new_device.name) if new_device != None else 'None'
            self.log('refresh to current device: ' + new_name)
            self.set_device(None)
            if new_device != None:
                self.get_song().view.select_device(self.get_song().view.selected_track.view.selected_device)
                self._get_param_details()
                self.notify_device()
        self._update_bank_buttons()
        self.device_lock_button.color = AMBER_FULL if self._device_locked else 'DefaultButton.Off'
        self.log('set_device_lock: LOCKED: ' + str(self._device_locked))

    def toggle_device_lock(self):
        self.set_device_lock(not self._device_locked)

    def do_direct_bank_button(self, button):
        index = list(self.direct_bank).index(button)
        self.log('direct_bank pressed: index: ' + str(index))
        self.set_device_bank(index)

    def do_device_enable_button(self, button):
        index = list(self.device_enable).index(button)
        self.log('device_enable pressed: index: ' + str(index))
        self.set_device_on_off(index)

    def do_device_select_button(self, button):
        index = list(self.device_select).index(button)
        self.log('device_select pressed: index: ' + str(index))
        self.select_device(index)

    def do_device_lock_button(self, button):
        self.toggle_device_lock()
        self.log('device_lock_button pressed: currently locked: ' + str(self._device_locked))
        self.device_lock_button.color = 'DefaultButton.On' if self._device_locked else 'DefaultButton.Off'

    def do_prev_device_button(self, button):
        self.log('prev_device: ' + str(self.prev_device_button.color) + ', ' + str(self._device_locked))
        if self.prev_device_button.color == 'DefaultButton.Off' or self._device_locked:
            return
        if self._skip_racks:
            if self._selected_track.view.selected_device in self._selected_track.devices:
                self.log('prev_device_1')
                index = list(self._selected_track.devices).index(self._selected_track.view.selected_device)
            elif self._allow_direct_select:
                self.log('prev_device_2')
                top_device = self._get_top_device()
                if top_device in self._selected_track.devices:
                    index = list(self._selected_track.devices).index(top_device)
                    self.log('top_device_index: ' + str(index))
            else:
                self.log('prev_device_3')
                index = 0
                self.device_num = 0
            self.log('index: ' + str(index))
            if index > 0:
                index -= 1
                self.log('prev_device: selecting: ' + str(index))
                device = self._selected_track.devices[index]
                if self._mapper:
                    device, updated = self._mapper._get_real_device(self, device)
                self.get_song().view.select_device(device)
                self.device_num = index
        else:
            self._scroll_device_view(Live.Application.Application.View.NavDirection.left)
        self.log('device_num: ' + str(self.device_num) + ', ' + str(self._selected_track.devices[index].name))

    def do_next_device_button(self, button):
        self.log('next_device: ' + str(self.next_device_button.color) + ', ' + str(self._device_locked))
        if self.next_device_button.color == 'DefaultButton.Off' or self._device_locked:
            return
        if self._skip_racks:
            if self._selected_track.view.selected_device in self._selected_track.devices:
                self.log('next_device_1')
                index = list(self._selected_track.devices).index(self._selected_track.view.selected_device)
            elif self._allow_direct_select:
                self.log('next_device_2')
                top_device = self._get_top_device()
                if top_device in self._selected_track.devices:
                    index = list(self._selected_track.devices).index(top_device)
                    self.log('top_device_index: ' + str(index))
            else:
                self.log('next_device_3')
                index = 0
                self.device_num = 0
            self.log('index: ' + str(index))
            if index < len(self._selected_track.devices) - 1:
                index += 1
                self.log('next_device: selecting: ' + str(index))
                device = self._selected_track.devices[index]
                if self._mapper:
                    device, updated = self._mapper._get_real_device(self, device)
                self.get_song().view.select_device(device)
                self.device_num = index
        else:
            self._scroll_device_view(Live.Application.Application.View.NavDirection.right)
        self.log('device_num: ' + str(self.device_num) + ', ' + str(self._selected_track.devices[index].name))

    def do_bank_up_button(self, button):
        self.log('do_bank_up_button')
        if self.bank_num < self.max_bank:
            self.bank_num += 1
            id = str(self.track_num) + '-' + str(self.device_num)
            self._current_banks[id] = self.bank_num
            self._my_assign_parameters()
            self._update_direct_bank()

    def do_bank_down_button(self, button):
        self.log('do_bank_down_button')
        if self.bank_num > 0:
            self.bank_num -= 1
            id = str(self.track_num) + '-' + str(self.device_num)
            self._current_banks[id] = self.bank_num
            self._my_assign_parameters()
            self._update_direct_bank()

    def set_device_bank(self, bank):
        self.log('set_device_bank: ' + str(bank) + ', curr: ' + str(self.bank_num) + ', max: ' + str(self.max_bank))
        if bank <= self.max_bank:
            self.bank_num = bank
            id = str(self.track_num) + '-' + str(self.device_num)
            self._current_banks[id] = self.bank_num
            self._my_assign_parameters()
            self._update_direct_bank()
        self.log('new_bank: ' + str(self.bank_num))

    def _update_direct_bank(self):
        if self._script._direct_bank:
            self.log('_update_direct_bank: ' + str(self.bank_num))
            for i in range(0, 4):
                self.direct_bank[i].color = 'DefaultButton.On' if i == self.bank_num else 'DefaultButton.Off'
                self.direct_bank[i].enabled = True

    def _scroll_device_view(self, direction):
        self.application().view.show_view('Detail')
        self.application().view.show_view('Detail/DeviceChain')
        self.application().view.scroll_view(direction, 'Detail/DeviceChain', False)

    def select_device(self, index):
        device = self._selected_track.devices[index]
        if self._mapper:
            device, updated = self._mapper._get_real_device(self, device)
        self.get_song().view.select_device(device)
        self.device_num = index

    def set_device(self, device):
        changed = device != self._current_device
        self.log('set_device: changed: ' + str(changed) + ', ' + (repr3(device.name) if device != None else 'None') + ', current: ' + (repr3(self._current_device.name) if self._current_device != None else 'None') + ', is_locked: ' + str(self._device_locked) + ', locked_device: ' + (repr3(self._locked_device.name) if self._locked_device != None else 'None'))
        if self._device_locked and self._locked_device == None:
            self.log('Unlocking device lock as locked device has been deleted')
            self.set_device_lock(False, False)
        if device != self._current_device or self._force_set_device or self._current_device == None:
            self._notify_device(device)
            self._current_device = device
            self._force_set_device = False

    def _notify_device(self, device = None, force = False, clear = False):
        self.log('DeviceComponentBase::_notify_device: ' + repr3(device.name) if device else 'None, enabled: ' + str(self._enabled) + ', locked: ' + str(self._device_locked) + ', force: ' + str(force) + ', clear: ' + str(clear) + ', mapper: ' + str(self._mapper != None))
        if self._mapper:
            self._mapper._notify_device(self, device, force, clear)
        if not self._enabled and g_mapper:
            self._snapshot_device(device)
            return
        if self._device_locked and not force:
            return
        if clear:
            self._selected_device = None
            for light in self.parameter_lights:
                light.enabled = False

        elif device == None:
            self._selected_track = self.get_song().view.selected_track
            if self._skip_racks and not self._allow_direct_select:
                self._selected_device = self._get_top_device()
            else:
                self._selected_device = self._selected_track.view.selected_device
        else:
            self._selected_device = device
        if self._mapper:
            self._selected_device, updated = self._mapper._get_real_device(self, self._selected_device)
            if updated:
                if not self._is_push:
                    self.get_song().view.select_device(self._selected_device)
            self._mapper._notify_device(self, self._selected_device, force, clear)
        self.log('_notify_device: selected: ' + 'None' if self._selected_device == None else repr3(self._selected_device.name))
        self._get_param_details()
        self.bank_num = 0
        self._my_assign_parameters(-1)
        self.update_track_state()
        self._set_current_bank()
        self._update_bank_buttons()

    def _on_parameters_changed(self):
        self.log('_on_parameters_changed')
        if self._mapper:
            self._mapper._on_parameters_changed(self)
            return

    def _set_current_bank(self):
        self.log('_set_current_bank: ' + ('None' if self._selected_device == None else repr3(self._selected_device.name)))
        id = str(self.track_num) + '-' + str(self.device_num)
        if id in self._current_banks:
            self.bank_num = self._current_banks[id]
            self.log('_set_current_bank: setting bank: ' + str(self.bank_num))
            self._my_assign_parameters()

    def _fetch_parameters(self, is_push = False):
        if self._mapper:
            self._mapper._fetch_parameters(self, is_push)
            return
        self.log('_fetch_parameters')
        if self._parameter_controls == None:
            return
        self.my_parameters = []
        banks = parameter_banks(self._selected_device)
        param_num = 0
        for i in range(0, len(banks)):
            bank = banks[i]
            for j in range(0, len(bank)):
                param = bank[j]
                if param != None:
                    param_num += 1
                    if self._script._LOG_PARAMS:
                        self.log('loading param: ' + str(param.name))
                    self.my_parameters.append(param)

        self.max_bank = int(math.floor((param_num - 1) / self._num_params))
        self.log('_fetch_parameters: num_params: ' + str(param_num) + ', per bank: ' + str(self._num_params) + ', num_banks: ' + str(self.max_bank))

    def _get_param_details(self):
        if self._mapper:
            self._mapper._get_param_details(self)
            return
        self.log('_get_param_details')
        if self._parameter_controls == None:
            return
        self.my_parameters = []
        banks = parameter_banks(self._selected_device)
        param_num = 0
        for i in range(0, len(banks)):
            bank = banks[i]
            for j in range(0, len(bank)):
                param = bank[j]
                if param != None:
                    param_num += 1
                    if self._script._LOG_PARAMS:
                        self.log('loading param: ' + str(param.name))
                    self.my_parameters.append(param)

        self.max_bank = int(math.floor((param_num - 1) / self._num_params))
        self.log('_get_param_details: num_params: ' + str(param_num) + ', per bank: ' + str(self._num_params) + ', num_banks: ' + str(self.max_bank))

    def _my_assign_parameters(self, bank_num = -1, is_push = False):
        if self._mapper:
            return self._mapper._my_assign_parameters(self, bank_num, self._is_push)
        name = self._selected_device.name if self._selected_device != None else 'None'
        if (self._parameter_controls == None or not hasattr(self, 'my_parameters')) and not self._is_osc:
            if self._enabled:
                self.log('ERROR: _my_assign_parameters: enabled: ' + str(self._enabled) + ', controls: ' + str(self._parameter_controls) + ', has_params: ' + str(hasattr(self, 'my_parameters')) + ', osc: ' + str(self._is_osc) + ', device: ' + repr3(name), True)
            return
        self.log('_my_assign_parameters: device: ' + str(name) + ', controls: ' + str(len(self.my_parameters)) + ', params: ' + str(len(self._parameter_controls)))
        if self._is_osc:
            if self._selected_device == None:
                active = list(repeat(0, self._num_params))
                self._active = active
                self._setup_device_controls(active)
                self.sub_notify('/selected_device', 'None')
            else:
                index = list(self._selected_track.devices).index(self._selected_track.view.selected_device)
                self.sub_notify('/selected_device', [index,
                 name,
                 self.bank_num,
                 self.max_bank + 1])
        param_start = self.bank_num * self._num_params
        leng = min(len(self.my_parameters) - param_start, self._num_params)
        active = list(repeat(1, leng))
        updated = self._setup_device_controls(active)
        self.log('active: ' + str(active) + ', updated: ' + str(updated))
        if not self._delayed_update or not updated:
            self.map_controls(is_push)

    def map_controls(self, is_push = False):
        if self._mapper:
            self._mapper.map_controls(self, is_push)
            return
        param_num = 0
        param_start = self.bank_num * self._num_params
        leng = min(len(self.my_parameters) - param_start, self._num_params)
        param_end = param_start + leng
        active = list(repeat(1, leng))
        hud = hasattr(self, '_hud_controls')
        self.log('DeviceComponent:map_controls: start ' + str(param_start) + ', len: ' + str(leng) + ', end: ' + str(param_end) + ', num_params: ' + str(len(self._parameter_controls)))
        for i in range(param_start, param_end):
            control = self._parameter_controls[param_num]
            index = i
            param = self.my_parameters[index]
            if self._script._LOG_PARAMS:
                self.log('connect: ' + param.name + ' to ' + control.name + ', i: ' + str(i) + ', param_num: ' + str(param_num) + ', index: ' + str(index) + ', val: ' + str(param.value))
            control.connect_to(param)
            if hud:
                self._hud_controls[param_num].connect_to(param)
            vals = [i,
             index,
             0,
             str(param.name),
             param.value,
             repr3(param.__str__()),
             param.min,
             param.max]
            self.sub_notify('/selected_device/parameter', vals)
            self.parameter_lights[param_num].color = bank_colours[self.bank_num % 6]
            self.parameter_lights[param_num].enabled = True
            param_num += 1

        for i in range(param_num, self._num_params):
            self.parameter_lights[i].enabled = False

        if self._parameter_controls != None:
            self._release_parameters(self._parameter_controls[param_num:])
        if hud:
            self._release_parameters(self._hud_controls[param_num:])
        for i in range(param_num, self._num_params):
            vals = [i, i, -1]
            self.sub_notify('/selected_device/parameter', vals)

        self._update_bank_buttons()
        if self._selected_device != None and self._selected_track != None and self._num_params != 8:
            msg = 'Controlling: ' + repr3(self._selected_device.name) + ' on ' + repr3(self._selected_track.name) + ': Bank ' + str(self.bank_num + 1) + '/' + str(self.max_bank + 1)
            self.msg(msg)

    def refresh(self):
        self._my_assign_parameters()
        self.update_track_state()
        self._update_bank_buttons()

    def on_selected_track_changed(self):
        changed = self._selected_track != self.get_song().view.selected_track
        self._selected_track = self.get_song().view.selected_track
        self.log('DeviceComponent:on_selected_track_changed: selected_track: ' + repr3(self._selected_track.name) + ', changed: ' + str(changed) + ', can_be_armed: ' + str(self._selected_track.can_be_armed) + ', can_fold: ' + str(self._selected_track.is_foldable) + ', enabled: ' + str(self._enabled))
        if not changed:
            return
        if self._enabled:
            self.update_track_state()
        selected_device = self.get_song().view.selected_track.view.selected_device
        if selected_device == None:
            self._notify_device(device=None, clear=True)
        else:
            self._notify_device(selected_device)

    def update_track_state(self):
        if self._selected_track:
            self.log('update_track_state(device): ' + repr3(self._selected_track.name))
            if repr3(self._selected_track.name) == 'Master':
                self.track_num = 3000
            elif self._selected_track in self.get_song().return_tracks:
                self.track_num = 1000 + list(self.get_song().return_tracks).index(self._selected_track)
            elif self._selected_track in self.get_song().tracks:
                if self._selected_track.is_foldable:
                    self.track_num = 2000 + list(self.get_song().tracks).index(self._selected_track)
                else:
                    self.track_num = list(self.get_song().tracks).index(self._selected_track)
            num_devices = len(self._selected_track.devices)
            selected_device = self._get_top_device()
            self.log('update_track_state: index: ' + str(self.track_num) + ', ' + repr3(self._selected_track.name) + ', num devices: ' + str(num_devices) + ', selected: ' + (repr3(selected_device.name) if selected_device != None else 'None'))
            self._devices_enable = []
            self._setup_num_device_controls(num_devices)
            self._update_select_enable_lights(num_devices, selected_device)
            self._on_device_enable.replace_subjects(self._devices_enable)
            self.set_num_devices(num_devices)
            self.log('update_track_state: selected_device: ' + str(self.device_num))

    def do_on_device_enable(self, param):
        index = list(self._devices_enable).index(param) if param in list(self._devices_enable) else -1
        self.log('_on_device_enable: ' + str(param) + ', index: ' + str(index))
        self.update_track_state()

    def set_device_on_off(self, index):
        self.log('set_device_on_off: ' + str(index) + ', ' + str(len(self._selected_track.devices)) + ', enable/disable: ' + str(self._enable_or_select))
        if self._selected_track == None or index >= len(self._selected_track.devices):
            return
        if self._enable_or_select:
            device_on_off = self._selected_track.devices[index].parameters[0].value
            selected_device = self._selected_track.devices[index] == self._selected_device
            self.log('state: ' + str(device_on_off))
            if device_on_off == 1:
                self._selected_track.devices[index].parameters[0].value = 0
            else:
                self._selected_track.devices[index].parameters[0].value = 1
            self._show_device_state(index, selected_device, self._selected_track.devices[index].parameters[0].value)
            self.log('new state: ' + str(self._selected_track.devices[index].parameters[0].value))
        else:
            self.get_song().view.select_device(self._selected_track.devices[index])

    def _update_select_enable_lights(self, num_devices, selected_device):
        if self._is_push:
            return
        for i in range(0, min(8, num_devices)):
            device = self._selected_track.devices[i]
            params = device.parameters
            param = params[0]
            self._show_device_state(i, selected_device == device, param.value)
            if selected_device == device:
                self.device_num = i
            self.device_select[i].enabled = True
            self.device_enable[i].enabled = True
            self._devices_enable.append(param)

        for i in range(num_devices, 8):
            self.device_select[i].enabled = False
            self.device_enable[i].enabled = False

    def _show_strip_state(self, index, track_present, iso_present, state):
        if not iso_present:
            state = 'ChannelStrip.Track_Present' if track_present else 'Device.Off'
        else:
            state = 'ChannelStrip.Rack_On' if state else 'ChannelStrip.Rack_Off'
        self.device_enable[index].color = state

    def _show_device_state(self, index, selected, enabled):
        self.log('_show_device_state: index: ' + str(index) + ', selected: ' + str(selected) + ', enabled: ' + str(enabled) + ', shared: ' + str(self._shared_enable_select))
        if self._shared_enable_select:
            if enabled:
                state = 'Device.On_Selected' if selected else 'Device.On'
            else:
                state = 'Device.Off_Selected' if selected else 'Device.Off'
            self.device_select[index].color = state
            self.device_enable[index].color = state
        else:
            self._show_device_selected(index, selected)
            self._show_device_enabled(index, enabled)

    def _show_device_enabled(self, index, flag):
        if flag:
            if self._mono:
                state = 'DefaultButton.On'
            else:
                state = 'Mixer.SoloOn' if not self._use_new_skin else 'Device.Enabled'
        elif self._mono:
            state = 'DefaultButton.Off'
        else:
            state = 'Mixer.ArmSelected' if not self._use_new_skin else 'Device.Disabled'
        self.device_enable[index].color = state
        self.log('_show_device_enabled: index: ' + str(index) + ', flag: ' + str(flag) + ', state: ' + str(state))

    def _show_device_selected(self, index, flag):
        if flag:
            if self._mono:
                state = 'DefaultButton.On'
            else:
                state = AMBER_FULL if not self._use_new_skin else 'Device.Selected'
        elif self._mono:
            state = 'DefaultButton.Off'
        else:
            state = 'Mixer.MuteOff' if not self._use_new_skin else 'Device.Unselected'
        self.device_select[index].color = state
        self.log('_show_device_selected: index: ' + str(index) + ', flag: ' + str(flag) + ', state: ' + str(state))

    def _get_top_device(self):
        if self._selected_track.view.selected_device == None or self._selected_track.view.selected_device in self._selected_track.devices:
            return self._selected_track.view.selected_device
        device = self._selected_track.view.selected_device
        while not isinstance(device.canonical_parent, (type(None), Live.Track.Track)):
            device = device.canonical_parent

        return device

    def _get_rack(self):
        device = self.get_song().view.selected_track.view.selected_device
        while device is not None:
            if isinstance(device, (type(None), Live.RackDevice.RackDevice)):
                return device
            device = device.canonical_parent

        return device

    def _update_bank_buttons(self, disable = False):
        if self._is_push:
            return
        self.log('_update_bank_buttons: current: ' + str(self.device_num) + ', num: ' + str(self.num_devices) + ', disable: ' + str(disable) + ', bank: ' + str(self.bank_num) + ', max: ' + str(self.max_bank) + ', ch_strip_bank: ' + str(self._channel_strip_bank))
        self.bank_down_button.color = 'DefaultButton.On' if self.max_bank > 0 and self.bank_num != 0 and not disable else 'DefaultButton.Off'
        self.bank_up_button.color = 'DefaultButton.On' if self.max_bank > 0 and self.bank_num != self.max_bank and not disable else 'DefaultButton.Off'
        self.prev_device_button.color = 'DefaultButton.On' if self.num_devices > 1 and self.device_num != 0 and not self._device_locked else 'DefaultButton.Off'
        self.next_device_button.color = 'DefaultButton.On' if self.num_devices > 1 and self.device_num != self.num_devices - 1 and not self._device_locked else 'DefaultButton.Off'
        self._update_direct_bank()

    def set_bank_buttons(self, buttons):
        for button in buttons or []:
            if button and hasattr(button, 'set_on_off_values'):
                button.set_on_off_values('Device.BankSelected', 'Device.BankUnselected')

    def _is_banking_enabled(self):
        return True

    def _setup_device_controls(self, active):
        self.log('_setup_device_controls: nop')
        return False

    def _setup_num_device_controls(self, num_devices):
        self.log('_setup_num_device_controls: nop')

    def sub_notify(self, msg, val):
        if hasattr(self._script, '_osc_control') and self._script._osc_control:
            self._script.oscServer.sendOSC(msg, val)
        if hasattr(self, '_hud_controls'):
            self._hud_state_control.notify_value(msg, val)
