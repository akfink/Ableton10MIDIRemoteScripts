#Embedded file name: IsotonikCommon.py
""" (c) 2014-20 Sigabort, Lee Huddleston, Isotonik Studios; admin@sigabort.co, http://sigabort.co, http://www.isotonikstudios.com """
from os import path
from functools import partial, wraps
import datetime
import logging
logger = logging.getLogger(__name__)
from globals import *
from _Framework import Task as task
from _Framework.NotifyingControlElement import NotifyingControlElement
from OSCControlElement import OSCControlElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
if g_10:
    from _MxDCore.MxDControlSurfaceAPI import MxDControlSurfaceAPI as M4LInterfaceComponent
else:
    from _Framework.M4LInterfaceComponent import M4LInterfaceComponent
from _Framework.InputControlElement import InputControlElement
if g_mapper:
    from PrEditor.PrEditor import PrEditor
if g_strip:
    from DeviceComponent_Strip import DeviceComponent_Strip
from DeviceComponent import DeviceComponent
FLASH_RATE = 0.2

class IsotonikCommon(object):
    _processing_UDP = False
    _version = -1

    def __init__(self, *a, **k):
        parent = k.pop('parent', None)
        if parent != None:
            self._LOG = False
            self._LOG_PARAMS = False
            self._LOG_MIDI = False
            self._LOG_SYSEX = False
            self._returns_toggled = 0
            self._box_follows_scene = True
            self._flash_state = False
            self._flash_state_2 = False
            self._flash_state_3 = False
            self._config = {}
            self._osc_control = False
            self._preditor_osc = None
            self._parent = parent
            self._device_component = None
            self._c_instance = k.pop('c_instance', None)
        if IsotonikCommon._version == -1:
            version_file = path.join(g_path, 'version.txt')
            if path.isfile(version_file):
                f = open(version_file, 'r')
                line = f.readline()
                IsotonikCommon._version = line.strip()
                f.close()
            else:
                IsotonikCommon._version = 0

    def log(self, msg, force = False):
        if hasattr(self, '_parent'):
            self._parent.log(msg, force)

    @staticmethod
    def repr3(input_str):
        try:
            output_st = unicodedata.normalize('NFKD', input_str).encode('ascii', 'ignore')
            if output_st != None:
                return output_st
            return ''
        except:
            x = repr(input_str)
            return x[1:-1]

    def _init(self, script_path, name, num_controls, has_flash = False, use_v2 = False):
        self._my_path = script_path
        self._script_name = name
        self._num_controls = num_controls
        self._has_flash = has_flash
        self._use_v2 = use_v2
        version_file = path.join(script_path, 'version.txt')
        build_file = path.join(script_path, 'build.txt')
        if path.isfile(version_file):
            f = open(version_file, 'r')
            line = f.readline()
            self._script_version = line.strip() + '.' + str(IsotonikCommon._version).strip()
            f.close()
        else:
            self._script_version = 'Unknown.' + str(IsotonikCommon._version).strip()
        if path.isfile(build_file):
            f = open(build_file, 'r')
            line = f.readline()
            self._build_time = line.strip()
            f.close()
        else:
            self._build_time = 'Unknown'
        user_path = path.expanduser('~')
        self._isotonik_data_path = path.join(user_path, 'Documents/Isotonik/PrEditor')
        self.log('-==- ' + str(self._script_name) + ' ' + str(self._script_version) + ' log opened -==-', True)
        self.log('User path: ' + IsotonikCommon.repr3(user_path) + ', Isotonik data: ' + IsotonikCommon.repr3(self._isotonik_data_path), True)
        self.log('Build: ' + str(self._build_time), True)
        self._preset = 0
        self._use_32 = 0
        self._direct_bank = False
        self._device_mode = False
        self._buffer = 0
        self._identified = False
        self._scene = 0
        self._read_config(True)

    def _startup(self):
        self.log('_startup', True)
        if self._osc_control or g_mapper:
            if not IsotonikCommon._processing_UDP:
                self.log('Start UDP monitor')
                self._process_upd_task = self._create_task(0.1, self._process_udp)
                IsotonikCommon._processing_UDP = True
        if self._osc_control:
            self.log('Creating HUD OSC ports: inbound: 27282, outbound: 27281', True)
            self.oscServer = RemixNet.OSCServer(self, '127.0.0.1', 27281, None, 27282)
            self.oscServer.sendOSC('/isotonik/HUD/', 1)
        if g_mapper:
            self._preditor = PrEditor(self._parent, self._script_name, self._script_version, self._num_controls)
        if self._sigabort_create():
            self._create_m4l_interface()
        if self._has_flash:
            self._flash_buttons_task = self._create_task(FLASH_RATE, self._flash_buttons)
        self.log('-==- ' + self._script_name + ' startup complete -==-', True)
        self.show_message(self._script_name + ' ' + self._script_version + '; (C) 2014-2020 Sigabort, Isotonik Studios; www.sigabort.co; www.isotonikstudios.com')

    def _shutdown(self):
        self.log('-==- ' + str(self._script_name) + ' ' + str(self._script_version) + ' log closed -==-', True)
        if g_mapper:
            self._preditor.shutdown()
            self._preditor = None
            IsotonikCommon._processing_UDP = False

    def _dump_config(self):
        for i in self._config:
            self.log('config: ' + i + ': ' + str(self._config[i]), True)

    def set_preditor_device_component(self, device_component, is_push = False):
        if hasattr(self, '_preditor') and self._preditor:
            self.log('set_preditor_device_component(1): push: ' + str(is_push))
            self._preditor.set_preditor_device_component(device_component, is_push)
        else:
            self.log('**** set_preditor_device_component(1): No PrEditor component', True)

    def send_preditor(self, msg, args):
        if hasattr(self, '_preditor') and self._preditor:
            self._preditor.send_osc(msg, args)

    def _process_udp(self):
        self._preditor._process_udp()
        self._process_upd_task = self._create_task(0.1, self._process_udp)

    def _read_config(self, dump_config = False):
        user_path = path.expanduser('~')
        config_file = path.join(user_path, 'Documents/Isotonik/Scripts/Config/' + self._script_name + '_config.txt')
        if not path.isfile(config_file):
            self.log(IsotonikCommon.repr3(config_file) + ' does not exist - checking for PrEditor config', True)
            config_file = path.join(self._isotonik_data_path, self._script_name + '_config.txt')
            if not path.isfile(config_file):
                self.log(IsotonikCommon.repr3(config_file) + ' does not exist - checking for local config', True)
                config_file = path.join(self._my_path, 'config.txt')
        self.log('Reading config(common): ' + IsotonikCommon.repr3(config_file), True)
        if not path.isfile(config_file):
            self.log('No config file', True)
            return
        f = open(config_file, 'r')
        line = f.readline()
        while line != '':
            if line[0] == '#':
                line = f.readLine()
                continue
            spl = line.split('=')
            if len(spl) == 2:
                valid = False
                opt = spl[0].lower()
                val = spl[1].strip()
                if opt == 'button_row_1':
                    self._button_row_1 = val
                    valid = True
                elif opt == 'button_row_2':
                    self._button_row_2 = val
                    valid = True
                elif opt == 'button_row_3':
                    self._button_row_3 = val
                    valid = True
                elif opt == 'button_reselect_track':
                    self._button_reselect_track = val
                    valid = True
                else:
                    val = int(spl[1])
                    if opt == 'log':
                        self._LOG = val
                        valid = True
                    elif opt == 'in_port':
                        self._in_port = val
                        valid = True
                    elif opt == 'out_port':
                        self._out_port = val
                        valid = True
                    elif opt == 'pans_enabled':
                        self._has_pans = val
                        valid = True
                    elif opt == 'pans':
                        self._has_pans = val
                        valid = True
                    elif opt == 'channel_strip':
                        self._channel_strip = val
                        valid = True
                    elif opt == 'toggle_1':
                        self._toggle_1 = val
                        valid = True
                    elif opt == 'toggle_2':
                        self._toggle_2 = val
                        valid = True
                    elif opt == 'toggle_3':
                        self._toggle_3 = val
                        valid = True
                    elif opt == 'toggle_4':
                        self._toggle_4 = val
                        valid = True
                    elif opt == 'box_follows_scene':
                        self._box_follows_scene = val
                        valid = True
                    elif opt == 'returns_mode':
                        self._show_returns = val
                        valid = True
                    elif opt == 'max_returns':
                        self._max_returns = val
                        valid = True
                    elif opt == 'track_bank':
                        self._track_bank_size = val
                        valid = True
                    elif opt == 'show_master':
                        self._show_master = val
                        valid = True
                    elif opt == 'custom_param_display':
                        self._custom_param_display = val
                        valid = True
                    elif opt == 'show_send_names':
                        self._show_send_names = val
                        valid = True
                    elif opt == 'show_macro_names':
                        self._show_macro_names = val
                        valid = True
                    elif opt == 'returns_fixed':
                        self._fixed_returns = val
                        valid = True
                    elif opt == 'swap_mixer_select':
                        self._swap_arm = val
                        valid = True
                    elif opt == 'swap_device_enable':
                        self._swap_select = val
                        valid = True
                    elif opt == 'preset':
                        self._preset = val
                        valid = True
                    elif opt == 'device_32':
                        self._use_32 = val
                        if val:
                            self._num_controls = 32
                        valid = True
                    elif opt == 'enable_function':
                        self._enable_function = val
                        valid = True
                    elif opt == 'track_navigation':
                        self._track_navigation = val
                        valid = True
                    elif opt == 'swap_arm':
                        self._swap_arm = val
                        valid = True
                    elif opt == 'direct_bank':
                        self._direct_bank = val
                        valid = True
                    elif opt == 'dynamic':
                        self._dynamic = val
                        valid = True
                    elif opt == 'transport':
                        self._has_transport = val
                        valid = True
                    elif opt == '14_bit':
                        self._bit_14 = val
                        valid = True
                    elif opt == 'log_bcl':
                        self._LOG_BCL = val
                        valid = True
                    elif opt == 'multi_map_devices':
                        self._multi_map_devices = spl[1]
                        valid = True
                    elif opt == 'log_param':
                        self._LOG_PARAMS = val
                        valid = True
                    elif opt == 'log_midi':
                        self._LOG_MIDI = val
                        self._LOG_SYSEX = val
                        valid = True
                if valid:
                    self._config[spl[0]] = spl[1].strip()
            line = f.readline()

        f.close()
        if dump_config:
            self._dump_config()

    def _create_m4l_interface(self):
        self.log('_create_m4l_interface', True)
        self._m4l_interface = M4LInterfaceComponent(controls=self.controls, component_guard=self.component_guard, priority=1)
        self.get_control_names = self._m4l_interface.get_control_names
        self.get_control = self._m4l_interface.get_control
        self.grab_control = self._m4l_interface.grab_control
        self.release_control = self._m4l_interface.release_control

    def _flash_buttons(self):
        self._flash_state = not self._flash_state
        if self._flash_state:
            self._flash_state_2 = not self._flash_state_2
            if self._flash_state_2:
                self._flash_state_3 = not self._flash_state_3
        self._do_flash()
        self._flash_buttons_task = self._create_task(FLASH_RATE, self._flash_buttons)

    def _do_flash(self):
        pass

    def dump_stack(self, levels = 5):
        frame = 0
        for i in inspect.stack():
            filename = str(i[1])
            self.log('frame: ' + str(frame) + ': ' + filename + ': ' + str(i[2]) + ': ' + str(i[4]), True)
            frame += 1
            if frame > levels:
                break

    def dump_live_controls(self):
        for control in self.controls:
            self.dump_live_control(control)

    def dump_live_control(self, control):
        if isinstance(control, InputControlElement):
            self.log('build_midi_map: ' + control.name + ', ' + str(control) + ', type: ' + str(control.message_type()) + ', ch: ' + str(control.message_channel()) + ', id: ' + str(control.message_identifier()), True)
        else:
            self.log('build_midi_map: ' + control.name + ', ' + str(control))

    @staticmethod
    def build_midi_map(self, midi_map_handle, dump = False):
        with self._in_build_midi_map():
            self._forwarding_registry.clear()
            self._forwarding_long_identifier_registry.clear()
            for control in self.controls:
                if isinstance(control, InputControlElement):
                    if dump:
                        self.dump_live_control(control)
                    control.install_connections(self._translate_message, partial(self._install_mapping, midi_map_handle), partial(self._install_forwarding, midi_map_handle))

            if self._pad_translations != None:
                self._c_instance.set_pad_translation(self._pad_translations)

    def get_device_component(self, num_params = 8, direct_bank = False, mono = True, shared = False, path = None, delayed_update = False, new_skin = False, *a, **k):
        self.log('get_device_component: num_params: ' + str(num_params))
        if g_strip:
            self._device_component = DeviceComponent_Strip(self, num_params, direct_bank, mono, shared, path, delayed_update, new_skin, *a, **k)
        else:
            self._device_component = DeviceComponent(self, num_params, direct_bank, mono, shared, path, delayed_update, new_skin, *a, **k)
        return self._device_component

    def _create_task(self, time, callback):
        return self._tasks.add(task.sequence(task.wait(time), task.run(callback)))

    def _create_osc_control_element(self, parent, osc_server, index, name, osc_msg, selected_parameter):
        control = OSCControlElement(parent, osc_server, index, osc_msg, selected_parameter)
        control.name = name + '_' + str(index)
        return control

    def _create_notifying_control_element(self, name):

        class MyNotifyingControlElement(NotifyingControlElement):

            def reset(self):
                pass

        control = MyNotifyingControlElement()
        control.name = name
        return control

    def _create_matrix(self, rows):
        return ButtonMatrixElement(rows)
