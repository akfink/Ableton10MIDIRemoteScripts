#Embedded file name: BCRXL.py
""" (c) 2015-2020 Sigabort, Lee Huddleston, Isotonik Studios; admin@sigabort.co, http://sigabort.co, http://www.isotonikstudios.com """
from __future__ import with_statement
from functools import partial
from itertools import chain
import Live
import math
from os import path
import datetime
from _Framework.ControlSurface import ControlSurface
from _Framework.TransportComponent import TransportComponent
from _Framework.EncoderElement import EncoderElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE
from _Framework.Layer import Layer
from _Framework.ModesComponent import ModesComponent, LayerMode, AddLayerMode
from _Framework.Util import nop
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.SubjectSlot import subject_slot, subject_slot_group, Subject
from .SkinDefault import make_default_skin
from _Framework import Task
from _Framework.Util import const
from _Framework.Dependency import inject
from _Framework.ButtonElement import ButtonElement
import logging
logger = logging.getLogger(__name__)
from _Isotonik.DeviceComponent import DeviceModeComponent
from _Isotonik.SessionComponent import SessionComponent
from _Isotonik.IsotonikCommon import IsotonikCommon
from MixerComponent import MixerComponent
from DeviceComponent import DeviceComponent
from DeviceComponent_Strip import DeviceComponent_Strip
from BCL import BCL
BCR_SYSEX = (240, 0, 32, 50, 1, 21, 33)
NUM_TRACKS = 8
MIXER_MODE = 8
DEVICE_MODE = 2
USER_MODE = 3
AMBER_FULL = 127
pad_identifiers = [65,
 66,
 67,
 68,
 69,
 70,
 71,
 72,
 73,
 74,
 75,
 76,
 77,
 78,
 79,
 80]

class BCRXL(ControlSurface, IsotonikCommon):

    def __init__(self, c_instance):
        self._dynamic = True
        self._LOG_BCL = False
        self._preset = 0
        self._use_32 = False
        self._enable_function = False
        self._track_navigation = False
        self._swap_arm = False
        self._direct_bank = False
        self._relative = False
        self._bit_14 = False
        self._fold_enabled = True
        self._can_fold = False
        self._show_returns = 0
        self._max_returns = -1
        self._returns_toggled = False
        self._has_pans = False
        self._track_bank_size = 1
        self._show_master = 0
        self._show_selected = 0
        self._button_row_1 = 'select'
        self._button_row_2 = 'mute'
        self._button_row_3 = 'solo'
        self._button_reselect_track = 'fold'
        self._channel_strip = False
        self._toggle_1 = False
        self._toggle_2 = False
        self._toggle_3 = False
        self._toggle_4 = False
        self._has_strip_device_enable = True
        self._USB = True
        self._has_transport = False
        self._showing_selected = False
        self._x_offset = 0
        self._y_offset = 0
        self._track_left = 113
        self._track_right = 114
        self._device_toggle = 109
        self._track_fold = 110
        self._refresh = 111
        self._device_lock = 110
        self._bank_up = 111
        self._bank_down = 112
        self._toggle_returns = False
        self._user_custom = False
        IsotonikCommon.__init__(self, parent=self, c_instance=c_instance)
        self._init(path.dirname(path.realpath(__file__)), 'BCR_XL', 24)
        super(BCRXL, self).__init__(c_instance)
        with self.component_guard():
            self._startup()

    def disconnect(self):
        if self._dynamic:
            pass
        self._shutdown()
        super(BCRXL, self).disconnect()

    def _sigabort_create(self):
        if self._show_returns == 3 or self._show_returns == 4:
            self._fold_enabled = False
            self._toggle_returns = True
        if not self._enable_function:
            self._direct_bank = False
            self._has_transport = False
        if self._channel_strip:
            self._fold_enabled = False
        self._user_custom = self._enable_function and not self._direct_bank and not self._has_transport
        self._bcr_controls = BCL(self, self._preset, self._relative, self._bit_14)
        self._device_selection_follows_track_selection = True
        self._default_skin = make_default_skin()
        with inject(skin=const(self._default_skin)).everywhere():
            self._create_controls()
        self._set_offsets_task = self._tasks.add(Task.sequence(Task.wait(0), Task.run(self._set_session_offsets)))
        self._set_offsets_task.kill()
        if self._show_selected:
            self._show_selected_task = self._tasks.add(Task.sequence(Task.wait(1), Task.run(self._show_selected_track)))
        return False

    def _enable_components(self):
        with self.component_guard():
            for component in self.components:
                self.log('Enable: ' + component.name)
                component.set_enabled(True)

    def set_session_offsets(self, x, y):
        self.log('bcrxl: set_session_offsets: ' + str(x) + ',' + str(y))
        self._scene = y
        self._x_offset = x
        self._y_offset = y
        self._set_offsets_task.restart()

    def _set_session_offsets(self):
        self._set_offsets_task.kill()
        self.log('_set_session_offsets')
        self._session.set_offsets(self._x_offset, self._y_offset)

    def _show_controlled_tracks_message(self, session):
        track_offset = session.track_offset()
        self.log('_show_controlled_tracks_message: ' + str(track_offset) + ', ' + str(self._scene))
        self._set_session_highlight(track_offset, self._scene, 8, 1, False)

    def _set_session_highlight(self, track_offset, scene_offset, width, height, include_return_tracks):
        self.log('_set_session_highlight: ' + str(track_offset) + ', ' + str(scene_offset) + ', ' + str(width) + ', ' + str(height) + ', ' + str(include_return_tracks))
        super(BCRXL, self)._set_session_highlight(track_offset, scene_offset, width, height, include_return_tracks)

    def _on_selected_scene_changed(self):
        if self._box_follows_scene:
            self._scene = list(self.song().scenes).index(self.song().view.selected_scene)
            self._show_controlled_tracks_message(self._on_session_offset_changed.subject)
            self.log('_on_selected_scene_changed: index: ' + str(self._scene))
        super(BCRXL, self)._on_selected_scene_changed()

    def _show_selected_track(self):
        self.log('_show_selected_track: ' + str(self._showing_selected) + ', index: ' + str(self._mixer._selected_track_index))
        self._showing_selected = not self._showing_selected
        volume_cc = 0 if self._bit_14 else 1
        if self._mixer._selected_track_index != -1:
            curr_val = self._mixer._channel_strips[self._mixer._selected_track_index]._track.mixer_device.volume.value
            self._do_send_midi((176 + MIXER_MODE, volume_cc + self._mixer._selected_track_index, int(math.floor(curr_val * 127.0)) if self._showing_selected else 0))
        self._show_selected_task = self._tasks.add(Task.sequence(Task.delay(2), Task.run(self._show_selected_track)))

    def on_identified(self):
        self.log('on_identified')
        self._identified = True
        if hasattr(self, 'default_session'):
            self.default_session.set_show_highlight(True)
            self._set_session_highlight(0, 0, 8, 1, False)
        super(BCRXL, self).on_identified()

    def _create_controls(self):
        self.log('_create_controls: dynamic: ' + str(self._dynamic) + ', function: ' + str(self._enable_function), True)
        if not self._dynamic:
            self._track_left = 105
            self._track_right = 106
            self._device_toggle = 107
        elif not self._enable_function:
            self._device_toggle = 105
            self._track_fold = 106
            self._device_lock = 106
            self._bank_up = 107
            self._bank_down = 108
        self.log('left: ' + str(self._track_left) + ', right: ' + str(self._track_right) + ', toggle: ' + str(self._device_toggle) + ', user_custom: ' + str(self._user_custom))
        if self._dynamic:
            if self._user_custom:
                self._bcr_controls.connect(self._toggle_1, self._toggle_2, self._toggle_3, self._toggle_4)
            else:
                self._bcr_controls.connect()
        self._modes = ModesComponent()
        self._create_our_controls()
        self._create_mixer()
        self._create_session()
        self._create_device()
        self._create_transport()

    def log(self, msg, force = False):
        if self._LOG or force:
            if isinstance(msg, str):
                logger.info(msg)
            else:
                logger.error('**++** Invalid log msg: ' + str(type(msg)) + ': ' + IsotonikCommon.repr3(msg))

    def _create_our_controls(self):
        self.log('_create_our_controls')

        def make_button(identifier, name, midi_type = MIDI_CC_TYPE, skin = self._default_skin):
            control = ButtonElement(False, midi_type, MIXER_MODE, identifier, name=name, skin=skin)
            return control

        def make_button_list(identifiers, name, midi_type = MIDI_NOTE_TYPE):
            return [ make_button(identifier, name % (i + 1), midi_type, self._default_skin) for i, identifier in enumerate(identifiers) ]

        def make_encoder(identifier, name, bit_14 = True):
            if self._bit_14:
                self.log('make_encoder: ' + name + ', CC: ' + str(identifier) + ', 14_bit: ' + str(bit_14))
                control = EncoderElement(MIDI_CC_TYPE, MIXER_MODE, identifier, Live.MidiMap.MapMode.absolute_14_bit if bit_14 else Live.MidiMap.MapMode.absolute, name=name)
            else:
                control = EncoderElement(MIDI_CC_TYPE, MIXER_MODE, identifier, Live.MidiMap.MapMode.absolute if not self._relative else Live.MidiMap.MapMode.relative_two_compliment, name=name)
            return control

        self._top_buttons = ButtonMatrixElement(rows=[make_button_list(chain(xrange(65, 73)), 'BCR_Top_Buttons_%d', MIDI_CC_TYPE)])
        self._bottom_buttons = ButtonMatrixElement(rows=[make_button_list(chain(xrange(73, 81)), 'BCR_Bottom_Buttons_%d', MIDI_CC_TYPE)])
        self._strip_enable_buttons = ButtonMatrixElement(rows=[make_button_list(chain(xrange(73, 81)), 'BCR_Bottom_Buttons_%d', MIDI_CC_TYPE)])
        if self._direct_bank or self._has_transport:
            self._direct_bank_buttons = ButtonMatrixElement(rows=[make_button_list(chain(xrange(105, 109)), 'BCR_User_Buttons_%d', MIDI_CC_TYPE)])
        self._left_button = make_button(self._track_left, 'Track_Left', MIDI_CC_TYPE)
        self._right_button = make_button(self._track_right, 'Track_Right', MIDI_CC_TYPE)
        self._device_engage_button = make_button(self._device_toggle, 'XXL_Pan_Device_Mode')
        self._track_fold_button = make_button(self._track_fold, 'Track_Fold', MIDI_CC_TYPE)
        if self._fold_enabled or self._toggle_returns or self._channel_strip:
            self._on_track_fold.subject = self._track_fold_button
            self._track_fold_button.enabled = False
        self._bank_up_button = make_button(self._bank_up, 'Device_Bank_Up', MIDI_CC_TYPE)
        self._bank_down_button = make_button(self._bank_down, 'Device_Bank_Down', MIDI_CC_TYPE)
        if self._bit_14:
            volume_cc = 0
            sends_cc = 8
            pans_cc = 81
            select_cc = 89
        else:
            volume_cc = 1
            sends_cc = 81
            pans_cc = 9
            select_cc = 33
        self._volume_encoders = ButtonMatrixElement(rows=[[ make_encoder(volume_cc + i, 'Volume_%d' % (i + 1)) for i in xrange(8) ]])
        if self._has_pans:
            self._pan_encoders = ButtonMatrixElement(rows=[[ make_encoder(pans_cc + i, 'Pan_%d' % (i + 1), bit_14=False) for i in xrange(8) ]])
        self._send_encoders = ButtonMatrixElement(rows=[[ make_encoder(sends_cc + i, 'Send_0_%d' % (i + 1)) for i in xrange(8) ], [ make_encoder(sends_cc + 8 + i, 'Send_1_%d' % (i + 1)) for i in xrange(8) ], [ make_encoder(sends_cc + 16 + i, 'Send_2_%d' % (i + 1)) for i in xrange(8) ]])
        self._push_buttons = ButtonMatrixElement(rows=[make_button_list(chain(xrange(select_cc, select_cc + 8)), 'BCR_Track_Select_%d', MIDI_CC_TYPE)])

    def _do_send_midi(self, midi_bytes):
        is_sysex = midi_bytes[0] == 240
        if self._LOG_MIDI and not is_sysex:
            self.log('_do_send_midi: ' + str(midi_bytes))
        if self._LOG_SYSEX and is_sysex:
            self.log('_do_send_midi: ' + str(midi_bytes))
        super(BCRXL, self)._do_send_midi(midi_bytes)

    def receive_midi(self, midi_bytes):
        is_sysex = midi_bytes[0] == 240
        send_off = False
        midi_id = 176 + MIXER_MODE
        adjusted = False
        if self._LOG_MIDI and not is_sysex:
            self.log('receive_midi: ' + str(midi_bytes) + ', id: ' + str(midi_id))
        if self._LOG_SYSEX and is_sysex:
            self.log('receive_midi: ' + str(midi_bytes))
        if midi_bytes[0] == midi_id:
            if midi_bytes[2] == 0:
                if self._has_transport:
                    if midi_bytes[1] in (107, 108):
                        midi_bytes = (midi_id, midi_bytes[1], 127)
                        adjusted = True
                    elif midi_bytes[1] == 106:
                        midi_bytes = (midi_id, midi_bytes[1], 127)
                        self._do_send_midi(midi_bytes)
                        adjusted = True
                if not self._device_mode:
                    if midi_bytes[1] in pad_identifiers:
                        midi_bytes = (midi_id, midi_bytes[1], 127)
                        adjusted = True
                if midi_bytes[1] in [self._track_left, self._track_right]:
                    midi_bytes = (midi_id, midi_bytes[1], 127)
                    adjusted = True
        if self._LOG_MIDI and adjusted:
            self.log('receive_midi(adjusted): ' + str(midi_bytes) + ', send_off: ' + str(send_off))
        if send_off:
            midi_bytes_new = (midi_id, midi_bytes[1], 0)
            if self._LOG_MIDI:
                self.log('send_off:receive_midi: ' + str(midi_bytes_new), True)
            super(BCRXL, self).receive_midi(midi_bytes_new)
        super(BCRXL, self).receive_midi(midi_bytes)

    def _create_user(self):

        def make_control_button(identifier, name, channel = 0, is_pad = False):
            button = ButtonElement(True, MIDI_NOTE_TYPE if is_pad else MIDI_CC_TYPE, channel, identifier)
            button.name = name
            button.set_on_off_values(127, 0)
            return button

        def make_control_encoder(identifier, name, channel = 0):
            encoder = EncoderElement(MIDI_CC_TYPE, channel, identifier, Live.MidiMap.MapMode.absolute if not self._relative else Live.MidiMap.MapMode.relative_two_compliment)
            encoder.reset = nop
            encoder.set_feedback_delay(-1)
            encoder.name = name
            return encoder

        def make_all_encoders(name_prefix = '', make_encoder = make_control_encoder):
            return ([ make_encoder(13 + index, name_prefix + '_' + str(index) + '_0') for index in xrange(8) ],
             [ make_encoder(80 + index, name_prefix + '_' + str(index) + '_1') for index in xrange(8) ],
             [ make_encoder(88 + index, name_prefix + '_' + str(index) + '_2') for index in xrange(8) ],
             [ make_encoder(96 + index, name_prefix + '_' + str(index) + '_3') for index in xrange(8) ])

        make_button = partial(make_control_button, channel=USER_MODE)
        make_encoder = partial(make_control_encoder, channel=USER_MODE)
        encoders_row_1, encoders_row_2, encoders_row_3, encoders_row_4 = make_all_encoders('User_Encoder', make_encoder)
        buttons_0 = [ make_button(pad_identifiers[i], 'User_Button_Matrix_' + str(i) + '_0', is_pad=True) for i in xrange(8) ]
        buttons_1 = [ make_button(pad_identifiers[i + 8], 'User_Button_Matrix_' + str(i) + '_1', is_pad=True) for i in xrange(8) ]
        self._matrix = ButtonMatrixElement()
        self._matrix.name = 'User_Button_Matrix'
        self._matrix.add_row(tuple(buttons_0))
        self._matrix.add_row(tuple(buttons_1))
        self.request_rebuild_midi_map()

    def on_selected_track_changed(self):
        self._selected_track = self.song().view.selected_track
        if hasattr(self, '_mixer'):
            if self._show_selected and self._mixer._last_selected_track_index != -1:
                volume_cc = 0 if self._bit_14 else 1
                curr_val = self._mixer._channel_strips[self._mixer._last_selected_track_index]._track.mixer_device.volume.value
                self.log('reset value for track: ' + str(self._mixer._last_selected_track_index) + ' to ' + str(curr_val), True)
                self._do_send_midi((176 + MIXER_MODE, volume_cc + self._mixer._last_selected_track_index, int(math.floor(curr_val * 127.0))))
        if self._fold_enabled:
            can_fold = False
            if self._selected_track != None:
                can_fold = self._selected_track.is_foldable
            self._can_fold = can_fold
            self.log('on_selected_track_changed: can_fold: ' + str(can_fold))
            self._track_fold_button.enabled = can_fold
            self._track_fold_button.send_value(127 if can_fold else 0)
        if hasattr(self, '_device'):
            self._device.on_selected_track_changed()

    @subject_slot('value')
    def _on_track_fold(self, value):
        self.log('_on_track_fold: ' + str(value) + ', fold_enabled: ' + str(self._fold_enabled) + ', can_fold: ' + str(self._can_fold) + ', toggle_returns: ' + str(self._toggle_returns) + ', channel_strip: ' + str(self._channel_strip))
        if self._channel_strip and self._modes.selected_mode != 'device':
            self.log('process channel_strip')
            if value:
                self.device_mode.layer = None
                self._on_device_engage(127, True)
                self._device.enable_channel_strip(True, True)
                self._on_strip_up.subject = self._bank_down_button
                self._on_strip_down.subject = self._bank_up_button
                if self._has_strip_device_enable:
                    self._on_strip_enable.replace_subjects(self._strip_enable_buttons)
                self._update_strip_bank_buttons()
                self._update_strip_enable_buttons()
            else:
                self.device_mode.layer = Layer(device_mode_button=self._device_engage_button)
                self._device.enable_channel_strip(False, True)
                self._on_device_engage(0, True)
                self._on_strip_up.subject = None
                self._on_strip_down.subject = None
                if self._has_strip_device_enable:
                    self._on_strip_enable.replace_subjects([])
        elif self._fold_enabled:
            self.log('process fold')
            self._track_fold_button.send_value(127 if self._can_fold else 0)
            if self._selected_track:
                self.log('can_fold: ' + str(self._selected_track.is_foldable))
                if self._selected_track.is_foldable:
                    self.log('currently folded: ' + str(self._selected_track.fold_state))
                    self._selected_track.fold_state = not self._selected_track.fold_state
        elif self._toggle_returns:
            self.log('process toggle returns')
            self._returns_toggled = value == 127
            self.log('returns_toggled: ' + str(self._returns_toggled))
            self._mixer._reassign_tracks(1 if self._returns_toggled else 0)

    @subject_slot('value')
    def _on_strip_up(self, value):
        self.log('_on_strip_up', True)
        self._device._do_strip_up()
        self._update_strip_bank_buttons()

    @subject_slot('value')
    def _on_strip_down(self, value):
        self.log('_on_strip_down', True)
        self._device._do_strip_down()
        self._update_strip_bank_buttons()

    @subject_slot_group('value')
    def _on_strip_enable(self, value, button):
        index = list(self._strip_enable_buttons).index(button)
        self.log('_on_strip_enable: ' + str(index) + ', ' + str(value), True)
        self._device._do_strip_enable(index)

    def _update_strip_bank_buttons(self):
        self._bank_up_button.send_value(127 if self._device._channel_strip_bank != 0 else 0)
        self._bank_down_button.send_value(127 if self._device._channel_strip_bank != 2 else 0)

    def _update_strip_enable_buttons(self):
        for i in range(0, len(self._device._iso_rack_enable)):
            if self._strip_enable_buttons[i] is not None:
                on = self._device._iso_rack_enable[i] and self._device._iso_rack_enable[i].value
                self._strip_enable_buttons[i].send_value(127 if on else 0)

    @subject_slot('value')
    def _on_skip_racks(self, value):
        if value == 127:
            self._device.toggle_enable_or_select()

    def _release_parameters(self, controls):
        if controls != None:
            for control in controls:
                if control != None:
                    control.release_parameter()

    def _create_transport(self):
        self.log('_create_transport: ' + str(self._has_transport), True)
        if not self._has_transport:
            return
        self._transport = TransportComponent()
        self._transport.set_stop_button(self._direct_bank_buttons[0])
        self._transport.set_play_button(self._direct_bank_buttons[1])
        self._transport.set_record_button(self._direct_bank_buttons[2])
        self._transport.set_overdub_button(self._direct_bank_buttons[3])

    def _create_session(self):
        self.log('_create_session', True)
        self._session = SessionComponent(self, name='BCR2K_Session', num_tracks=NUM_TRACKS, track_bank_size=self._track_bank_size, is_enabled=True, auto_name=True)
        self._session.layer = Layer(track_bank_left_button=self._left_button, track_bank_right_button=self._right_button)
        self._session.set_mixer(self._mixer)
        self._session._setup_controls()
        self._on_session_offset_changed.subject = self._session
        self._session.set_show_highlight(True)
        self._set_session_highlight(0, 0, 8, 1, False)

    @subject_slot('offset')
    def _on_session_offset_changed(self):
        self.log('_on_session_offset_changed')
        session = self._on_session_offset_changed.subject
        self._show_controlled_tracks_message(session)
        if hasattr(self._device, '_assign_channel_strip') and self._device._assign_channel_strip:
            self._device._on_session_offset_changed()

    def _create_mixer(self):
        self.log('_create_mixer', True)
        mixer = MixerComponent(self, NUM_TRACKS, 3, show_returns=self._show_returns, max_returns=self._max_returns, show_master=self._show_master, delayed_update=True, is_enabled=True, auto_name=True)
        layer = Layer(volume_controls=self._volume_encoders, send_controls=self._send_encoders, next_sends_button=self._bank_down_button, prev_sends_button=self._bank_up_button)
        valid_opts = self._get_button_options()
        layer += Layer(**valid_opts)
        mixer.layer = layer
        self._mixer = mixer
        self._bcr_controls.setup_mixer_controls()
        self._modes.add_mode('mixer', [AddLayerMode(self._mixer, layer)])
        self._modes.selected_mode = 'mixer'

    def _get_button_options(self, channel_strip = False):
        opts = {}
        use_bottom_row_for_channel_strip = self._has_strip_device_enable
        if not use_bottom_row_for_channel_strip:
            channel_strip = False
        if self._has_pans:
            opts['pan_controls'] = self._pan_encoders
        opts['track_select_buttons'] = self._push_buttons if self._button_row_1 == 'select' else (self._top_buttons if self._button_row_2 == 'select' else (self._bottom_buttons if self._button_row_3 == 'select' and not channel_strip else None))
        opts['mute_buttons'] = self._push_buttons if self._button_row_1 == 'mute' else (self._top_buttons if self._button_row_2 == 'mute' else (self._bottom_buttons if self._button_row_3 == 'mute' and not channel_strip else None))
        opts['solo_buttons'] = self._push_buttons if self._button_row_1 == 'solo' else (self._top_buttons if self._button_row_2 == 'solo' else (self._bottom_buttons if self._button_row_3 == 'solo' and not channel_strip else None))
        opts['arm_buttons'] = self._push_buttons if self._button_row_1 == 'arm' else (self._top_buttons if self._button_row_2 == 'arm' else (self._bottom_buttons if self._button_row_3 == 'arm' and not channel_strip else None))
        valid_opts = {}
        for k, v in opts.iteritems():
            if v is not None:
                valid_opts[k] = v

        return valid_opts

    def _on_device_engage(self, value, channel_strip = False):
        self.log('_on_device_engage: ' + str(value) + ', channel_strip: ' + str(channel_strip))
        if value == 127:
            if not channel_strip:
                self._session.set_mixer(None)
                self._session.layer = None
            self.set_device_component(self._device)
            self._device_mode = True
            self._bcr_controls._mode = 1
            self._modes.selected_mode = 'device_strip' if channel_strip else 'device'
            if self._use_32:
                self._mixer.set_volume_controls(None)
        else:
            self._device_mode = False
            self._bcr_controls._mode = 0
            self._bcr_controls.setup_mixer_controls(-1, -1, True, -1)
            if not channel_strip:
                self._session.set_mixer(self._mixer)
                self._session.layer = Layer(track_bank_left_button=self._left_button, track_bank_right_button=self._right_button)
            if self._fold_enabled or self._toggle_returns:
                if self._fold_enabled:
                    self._can_fold = self._selected_track != None and self._selected_track.is_foldable
                self._on_track_fold.subject = self._track_fold_button
            self._modes.selected_mode = 'mixer'
            if self._use_32:
                self._mixer.set_volume_controls(self._volume_encoders)

    def _create_device(self):
        self.log('_create_device', True)

        def make_button(identifier, name, midi_type = MIDI_CC_TYPE, skin = self._default_skin):
            return ButtonElement(True, midi_type, MIXER_MODE, identifier, name=name, skin=skin)

        def make_encoder(identifier, name, bit_14 = True):
            if self._bit_14:
                self.log('make_encoder: ' + name + ', CC: ' + str(identifier) + ', 14_bit: ' + str(bit_14))
                control = EncoderElement(MIDI_CC_TYPE, MIXER_MODE, identifier, Live.MidiMap.MapMode.absolute_14_bit if bit_14 else Live.MidiMap.MapMode.absolute, name=name)
            else:
                control = EncoderElement(MIDI_CC_TYPE, MIXER_MODE, identifier, Live.MidiMap.MapMode.absolute if not self._relative else Live.MidiMap.MapMode.relative_two_compliment, name=name)
            return control

        if self._bit_14:
            volume_cc = 0
            sends_cc = 8
        else:
            volume_cc = 1
            sends_cc = 81
        if self._use_32:
            self._device_encoders = ButtonMatrixElement(rows=[[ make_encoder(volume_cc + i, 'Volume_%d' % (i + 1)) for i in xrange(8) ],
             [ make_encoder(sends_cc + i, 'BCR_Device_0_%d' % (i + 1)) for i in xrange(8) ],
             [ make_encoder(sends_cc + 8 + i, 'BCR_Device_1_%d' % (i + 1)) for i in xrange(8) ],
             [ make_encoder(sends_cc + 16 + i, 'BCR_Device_2_%d' % (i + 1)) for i in xrange(8) ]])
            self._send_encoders = self._device_encoders.submatrix[:8, 1:4]
        else:
            self._device_encoders = self._send_encoders
        if self._channel_strip:
            self._device = DeviceComponent_Strip(self, name='XL_Device', is_enabled=True, direct_bank=self._direct_bank, num_params=32 if self._use_32 else 24, path=self._my_path, delayed_update=True)
        else:
            self._device = DeviceComponent(self, name='XL_Device', is_enabled=True, direct_bank=self._direct_bank, num_params=32 if self._use_32 else 24, path=self._my_path, delayed_update=True)
        self.set_preditor_device_component(self._device)
        if self._direct_bank:
            device_layer = Layer(parameter_controls=self._device_encoders, device_select=self._top_buttons, device_enable=self._bottom_buttons, device_lock_button=self._track_fold_button, bank_up_button=self._bank_down_button, bank_down_button=self._bank_up_button, direct_bank=self._direct_bank_buttons)
        else:
            device_layer = Layer(parameter_controls=self._device_encoders, device_select=self._top_buttons, device_enable=self._bottom_buttons, device_lock_button=self._track_fold_button, bank_up_button=self._bank_down_button, bank_down_button=self._bank_up_button)
        device_settings_layer = Layer()
        self.device_mode = DeviceModeComponent(script=self, component=self._device, device_settings_mode=[AddLayerMode(self._device, device_settings_layer)], is_enabled=True)
        self.device_mode.layer = Layer(device_mode_button=self._device_engage_button)
        if self._has_pans:
            mixer_layer = Layer(volume_controls=self._volume_encoders, pan_controls=self._pan_encoders)
        else:
            mixer_layer = Layer(volume_controls=self._volume_encoders)
        self._modes.add_mode('device', [AddLayerMode(self._device, device_layer), AddLayerMode(self._mixer, mixer_layer)])
        if self._channel_strip:
            if hasattr(self._device, 'enable_channel_strip'):
                strip_layer = Layer(parameter_controls=self._device_encoders)
                valid_opts = self._get_button_options(True)
                mixer_layer += Layer(**valid_opts)
                self._modes.add_mode('device_strip', [AddLayerMode(self._device, strip_layer), AddLayerMode(self._mixer, mixer_layer), AddLayerMode(self._session, Layer(track_bank_left_button=self._left_button, track_bank_right_button=self._right_button))])
            else:
                self._channel_strip = False

    def update(self):
        self.log('update: device_mode: ' + str(self._device_mode))
        super(BCRXL, self).update()

    def refresh_state(self):
        self.log('refresh_state')
        super(BCRXL, self).refresh_state()

    def handle_sysex(self, midi_bytes):
        if self._LOG_SYSEX:
            self.log('handle_sysex: ' + str(midi_bytes))
        if midi_bytes[:4] == BCR_SYSEX[:4] and midi_bytes[5] == 21:
            if self._bcr_controls.receive_ack(midi_bytes):
                if self._device_mode:
                    self._device.map_controls()
                else:
                    self._mixer.map_controls()
            if midi_bytes[9:10] != (0,):
                self.log('Received sysex error code: ' + str(midi_bytes), True)

    @subject_slot_group('value')
    def _on_select_pressed(self, value, button):
        pass

    def same_track_selected(self):
        self.log('BCRXL: same_track_selected')
        selected_track = self.song().view.selected_track
        if selected_track != None:
            if self._device_mode:
                self.song().view.selected_track = self.song().master_track
            elif self._button_reselect_track == 'mute':
                selected_track.mute = not selected_track.mute
            elif self._button_reselect_track == 'solo':
                selected_track.solo = not selected_track.solo
            elif self._button_reselect_track == 'arm':
                if selected_track.can_be_armed:
                    selected_track.arm = not selected_track.arm
            elif self._button_reselect_track == 'fold':
                if self._selected_track.is_foldable:
                    self._selected_track.fold_state = not self._selected_track.fold_state
        return False
