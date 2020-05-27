#Embedded file name: BCL.py
""" (c) 2015 Sigabort, Lee Huddleston, Isotonik Studios; admin@sigabort.co, http://sigabort.co, http://www.isotonikstudios.com """
import math
MIDI_CH = 57
sysex_start = [240,
 0,
 32,
 50,
 127,
 127,
 32,
 0,
 0]
sysex_rev = [240,
 0,
 32,
 50,
 127,
 127,
 32,
 0,
 0,
 36,
 114,
 101,
 118,
 32,
 82,
 247]
sysex_rev_bcf = [240,
 0,
 32,
 50,
 127,
 127,
 32,
 0,
 0,
 36,
 114,
 101,
 118,
 32,
 70,
 247]
sysex_end = [240,
 0,
 32,
 50,
 127,
 127,
 32,
 0,
 3,
 36,
 101,
 110,
 100,
 247]
bcr_init = [[240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  1,
  36,
  112,
  114,
  101,
  115,
  101,
  116,
  247],
 [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  2,
  46,
  105,
  110,
  105,
  116,
  247],
 [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  3,
  46,
  101,
  103,
  114,
  111,
  117,
  112,
  115,
  32,
  50,
  247],
 [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  4,
  46,
  102,
  107,
  101,
  121,
  115,
  32,
  111,
  102,
  102,
  247]]
bcr_lock = [240,
 0,
 32,
 50,
 127,
 127,
 32,
 0,
 4,
 46,
 108,
 111,
 99,
 107,
 32,
 111,
 110,
 247]
bcr_preset_1 = [240,
 0,
 32,
 50,
 127,
 127,
 32,
 0,
 1,
 36,
 114,
 101,
 99,
 97,
 108,
 108,
 32,
 49,
 247]
bcr_recall = [[240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  1,
  36,
  114,
  101,
  99,
  97,
  108,
  108,
  32,
  -1,
  247], [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  1,
  36,
  114,
  101,
  99,
  97,
  108,
  108,
  32,
  -1,
  -1,
  247]]
bcr_store = [[240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  1,
  36,
  115,
  116,
  111,
  114,
  101,
  32,
  -1,
  247], [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  1,
  36,
  115,
  116,
  111,
  114,
  101,
  32,
  -1,
  -1,
  247]]
enable_encoder = [[240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  -1,
  36,
  101,
  110,
  99,
  111,
  100,
  101,
  114,
  32,
  -1,
  -1,
  247],
 [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  -1,
  46,
  101,
  97,
  115,
  121,
  112,
  97,
  114,
  32,
  67,
  67,
  32,
  MIDI_CH,
  32,
  -1,
  -1,
  32,
  48,
  32,
  49,
  50,
  55,
  32,
  97,
  98,
  115,
  111,
  108,
  117,
  116,
  101,
  247],
 [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  -1,
  46,
  109,
  111,
  100,
  101,
  32,
  49,
  100,
  111,
  116,
  247],
 [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  -1,
  46,
  101,
  97,
  115,
  121,
  112,
  97,
  114,
  32,
  67,
  67,
  32,
  MIDI_CH,
  32,
  49,
  48,
  -1,
  32,
  48,
  32,
  49,
  50,
  55,
  32,
  97,
  98,
  115,
  111,
  108,
  117,
  116,
  101,
  247],
 [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  -1,
  46,
  109,
  111,
  100,
  101,
  32,
  98,
  97,
  114,
  247],
 [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  -1,
  46,
  101,
  97,
  115,
  121,
  112,
  97,
  114,
  32,
  67,
  67,
  32,
  MIDI_CH,
  32,
  -1,
  -1,
  32,
  48,
  32,
  49,
  50,
  55,
  32,
  114,
  101,
  108,
  97,
  116,
  105,
  118,
  101,
  45,
  49,
  247],
 [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  -1,
  46,
  101,
  97,
  115,
  121,
  112,
  97,
  114,
  32,
  67,
  67,
  32,
  MIDI_CH,
  32,
  49,
  48,
  -1,
  32,
  48,
  32,
  49,
  50,
  55,
  32,
  114,
  101,
  108,
  97,
  116,
  105,
  118,
  101,
  45,
  49,
  247],
 [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  -1,
  46,
  114,
  101,
  115,
  111,
  108,
  117,
  116,
  105,
  111,
  110,
  32,
  54,
  49,
  52,
  52,
  247],
 [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  -1,
  46,
  109,
  111,
  100,
  101,
  32,
  112,
  97,
  110,
  247],
 [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  -1,
  46,
  101,
  97,
  115,
  121,
  112,
  97,
  114,
  32,
  67,
  67,
  32,
  MIDI_CH,
  32,
  -1,
  -1,
  32,
  48,
  32,
  49,
  54,
  51,
  56,
  51,
  32,
  97,
  98,
  115,
  111,
  108,
  117,
  116,
  101,
  47,
  49,
  52,
  247]]
disable_encoder = [240,
 0,
 32,
 50,
 127,
 127,
 32,
 0,
 -1,
 36,
 101,
 110,
 99,
 111,
 100,
 101,
 114,
 32,
 -1,
 -1,
 247]
enable_fader = [[240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  -1,
  36,
  102,
  97,
  100,
  101,
  114,
  32,
  -1,
  247],
 [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  -1,
  46,
  101,
  97,
  115,
  121,
  112,
  97,
  114,
  32,
  67,
  67,
  32,
  MIDI_CH,
  32,
  -1,
  -1,
  32,
  48,
  32,
  49,
  50,
  55,
  32,
  97,
  98,
  115,
  111,
  108,
  117,
  116,
  101,
  247],
 [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  -1,
  46,
  109,
  111,
  116,
  111,
  114,
  32,
  111,
  110,
  247],
 [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  -1,
  46,
  109,
  111,
  116,
  111,
  114,
  32,
  111,
  102,
  102,
  247],
 [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  -1,
  46,
  100,
  101,
  102,
  97,
  117,
  108,
  116,
  32,
  48,
  247]]
disable_fader = [240,
 0,
 32,
 50,
 127,
 127,
 32,
 0,
 -1,
 46,
 101,
 97,
 115,
 121,
 112,
 97,
 114,
 32,
 67,
 67,
 32,
 49,
 54,
 32,
 49,
 50,
 55,
 32,
 48,
 32,
 49,
 50,
 55,
 32,
 97,
 98,
 115,
 111,
 108,
 117,
 116,
 101,
 247]
enable_button = [[240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  -1,
  36,
  98,
  117,
  116,
  116,
  111,
  110,
  32,
  -1,
  -1,
  247],
 [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  -1,
  46,
  101,
  97,
  115,
  121,
  112,
  97,
  114,
  32,
  67,
  67,
  32,
  MIDI_CH,
  32,
  -1,
  -1,
  32,
  49,
  50,
  55,
  32,
  48,
  32,
  116,
  111,
  103,
  103,
  108,
  101,
  111,
  110,
  247],
 [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  -1,
  46,
  101,
  97,
  115,
  121,
  112,
  97,
  114,
  32,
  67,
  67,
  32,
  MIDI_CH,
  32,
  49,
  -1,
  -1,
  32,
  49,
  50,
  55,
  32,
  48,
  32,
  116,
  111,
  103,
  103,
  108,
  101,
  111,
  110,
  247],
 [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  -1,
  46,
  101,
  97,
  115,
  121,
  112,
  97,
  114,
  32,
  67,
  67,
  32,
  MIDI_CH,
  32,
  -1,
  -1,
  32,
  49,
  50,
  55,
  32,
  48,
  32,
  116,
  111,
  103,
  103,
  108,
  101,
  111,
  102,
  102,
  247],
 [240,
  0,
  32,
  50,
  127,
  127,
  32,
  0,
  -1,
  46,
  101,
  97,
  115,
  121,
  112,
  97,
  114,
  32,
  67,
  67,
  32,
  MIDI_CH,
  32,
  49,
  -1,
  -1,
  32,
  49,
  50,
  55,
  32,
  48,
  32,
  116,
  111,
  103,
  103,
  108,
  101,
  111,
  102,
  102,
  247]]
disable_button = [240,
 0,
 32,
 50,
 127,
 127,
 32,
 0,
 -1,
 36,
 98,
 117,
 116,
 116,
 111,
 110,
 32,
 -1,
 -1,
 247]

class BCL(object):

    def __init__(self, parent, preset, relative, absolute, bcf = False, *a, **k):
        self._parent = parent
        self._preset = preset
        self._encoder_state = []
        self._encoder_type = []
        self._fader_state = []
        self._button_state = []
        self._mode = 0
        self._bcf = bcf
        self._log_bcl = parent._LOG_BCL
        self._acked = -1
        self._debug = True
        self._optimise = preset != 0
        self._relative_encoder = relative
        self._bit_14 = absolute
        self._nav_is_toggle = -1
        for i in range(40):
            if i < 24:
                self._button_state.append(False)
            if i < 8:
                self._fader_state.append(False)
            self._encoder_state.append(False)
            self._encoder_type.append(-1)

    def log(self, msg):
        if hasattr(self, '_parent'):
            self._parent.log(msg)

    def debug(self, msg):
        if self._debug:
            self.log(msg)

    def _send_midi(self, midi_bytes, flush = True):
        if hasattr(self, '_parent'):
            self._parent._do_send_midi(midi_bytes)
            if self._log_bcl:
                index = midi_bytes[7] * 128 + midi_bytes[8]
                desc = '_send_midi: bcl: ' + str(index) + ': '
                for i in range(9, len(midi_bytes) - 1):
                    desc += chr(midi_bytes[i])

                self.log(desc)
            if flush:
                self._parent._flush_midi_messages()

    def _bcl_start(self):
        self._rev_sent = False
        self._bcl_index = 1

    def _bcl_end(self):
        if self._rev_sent:
            self._send_bcl(sysex_end)
            self._rev_sent = False
            if self._acked == -1 or self._bcl_index - 1 > self._acked:
                self._acked = self._bcl_index - 1
                if self._log_bcl:
                    self.log('Set ack count: ' + str(self._acked))

    def receive_ack(self, midi_bytes):
        res = False
        index = midi_bytes[7] * 128 + midi_bytes[8]
        if self._log_bcl:
            self.log('process ack: ' + str(index))
        if index == self._acked:
            if self._log_bcl:
                self.log('Send complete')
            self._acked = -1
            res = True
        return res

    def _send_bcl(self, msg, flush = True):
        if not self._rev_sent:
            if self._bcf:
                self._send_midi(tuple(sysex_rev_bcf), flush)
            else:
                self._send_midi(tuple(sysex_rev), flush)
            self._rev_sent = True
        out_msg = sysex_start[:]
        out_msg[7] = int(math.floor(self._bcl_index / 128))
        out_msg[8] = self._bcl_index % 128
        out_msg += msg[9:]
        self._bcl_index += 1
        self._send_midi(tuple(out_msg))

    def connect(self, toggle_1 = True, toggle_2 = True, toggle_3 = True, toggle_4 = True):
        self._bcl_start()
        self._send_bcl(bcr_init[0])
        self._send_bcl(bcr_init[1])
        if self._parent._track_navigation:
            self._send_bcl(bcr_init[2])
        if self._parent._enable_function:
            self._send_bcl(bcr_init[3])
        if self._preset == 0:
            self._send_bcl(bcr_lock)
        self._bcl_end()
        self._setup_static_controls(toggle_1, toggle_2, toggle_3, toggle_4)

    def disconnect(self):
        self._bcl_start()
        self._send_bcl(bcr_preset_1, False)
        self._bcl_end()

    def _recall(self):
        if self._preset == 0:
            return
        self.log('_recall: ' + str(self._preset))
        self._bcl_start()
        if self._preset < 10:
            bcr_recall[0][17] = 48 + self._preset
            self._send_bcl(bcr_recall[0])
        else:
            msd = int(math.floor(self._preset / 10))
            lsd = self._preset % 10
            bcr_recall[1][17] = 48 + msd
            bcr_recall[1][18] = 48 + lsd
            self._send_bcl(bcr_recall[1])
        self._bcl_end()

    def _store(self):
        if self._preset == 0:
            return
        self.log('_store: ' + str(self._preset))
        self._bcl_start()
        if self._preset < 10:
            bcr_store[0][16] = 48 + self._preset
            self._send_bcl(bcr_store[0])
        else:
            msd = int(math.floor(self._preset / 10))
            lsd = self._preset % 10
            self._send_midi(tuple(sysex_rev))
            bcr_store[1][16] = 48 + msd
            bcr_store[1][17] = 48 + lsd
            self._send_bcl(bcr_store[1])
        self._bcl_end()

    def _encoder_setup(self, index, enable, cc = 0, type = 0, check = True):
        if check:
            self.debug('checking encoder: index: ' + str(index) + ', enable: ' + str(enable) + ', curr: ' + str(self._encoder_state[index]) + ', curr_type: ' + str(self._encoder_type[index]) + ', type: ' + str(type))
        else:
            self.debug('checking encoder: index: ' + str(index) + ', enable: ' + str(enable) + ', type: ' + str(type))
        if check and (enable and self._encoder_state[index] == True and self._encoder_type[index] == type or not enable and self._encoder_state[index] == False):
            self.debug('Enable encoder: index: ' + str(index) + ', cc: ' + str(cc) + ', enabled: ' + str(self._encoder_state[index]) + ' - no update necessary')
            return False
        if not self._rev_sent:
            self._bcl_start()
        orig_index = index
        index += 1
        if index > 16:
            index += 16
        msd = int(math.floor(index / 10))
        lsd = index % 10
        two_digit = 1 if not self._relative_encoder else 5
        one_digit = 3 if not self._relative_encoder else 6
        is_pan = orig_index >= 8 and orig_index < 16
        change_type = type != self._encoder_type[orig_index]
        if self._bit_14 and not is_pan:
            two_digit = 9
        if enable:
            self.log('Enable encoder: orig_index: ' + str(orig_index) + ', index: ' + str(index) + ', cc: ' + str(cc) + ', enable: ' + str(enable) + ', is_pan: ' + str(is_pan) + ', change_type: ' + str(change_type))
            enable_encoder[0][18] = 48 + msd
            enable_encoder[0][19] = 48 + lsd
            msd = int(math.floor(cc / 10))
            lsd = cc % 10
            if cc >= 100:
                enable_encoder[one_digit][25] = 48 + lsd
            else:
                enable_encoder[two_digit][23] = 48 + msd
                enable_encoder[two_digit][24] = 48 + lsd
            self._send_bcl(enable_encoder[0])
            if cc >= 100:
                self._send_bcl(enable_encoder[one_digit])
            else:
                self._send_bcl(enable_encoder[two_digit])
            if type == 2:
                self._send_bcl(enable_encoder[8])
            elif type == 1:
                self._send_bcl(enable_encoder[4])
            else:
                self._send_bcl(enable_encoder[2])
            if self._bit_14 and not is_pan:
                self._send_bcl(enable_encoder[7])
        else:
            self.log('Disable encoder: ' + str(orig_index) + ', ' + str(index))
            disable_encoder[18] = 48 + msd
            disable_encoder[19] = 48 + lsd
            self._send_bcl(disable_encoder)
        if check:
            self._encoder_state[orig_index] = enable
            self._encoder_type[orig_index] = type
        return True

    def _fader_setup(self, index, enable, cc = 0, type = 0, check = True):
        if check and self._fader_state[index] == enable:
            return False
        if not self._rev_sent:
            self._bcl_start()
        orig_index = index
        index += 1
        if enable:
            self.log('Enable fader: orig_index: ' + str(orig_index) + ', index: ' + str(index) + ', cc: ' + str(cc) + ', enable: ' + str(enable))
            enable_fader[0][16] = 48 + index
            msd = int(math.floor(cc / 10))
            lsd = cc % 10
            enable_fader[1][23] = 48 + msd
            enable_fader[1][24] = 48 + lsd
            self._send_bcl(enable_fader[0])
            self._send_bcl(enable_fader[1])
            self._send_bcl(enable_fader[2])
        else:
            self.log('Disable fader: ' + str(orig_index) + ', ' + str(index))
            enable_fader[0][16] = 48 + index
            self._send_bcl(enable_fader[0])
            self._send_bcl(disable_fader)
            self._send_bcl(enable_fader[2])
            self._send_bcl(enable_fader[4])
        if check:
            self._fader_state[orig_index] = enable
        return True

    def _button_setup(self, index, enable, cc = 0, check = True, type = 1, toggleon = True):
        if check and self._button_state[index] == enable:
            return False
        if not self._rev_sent:
            self._bcl_start()
        orig_index = index
        index += 1
        if index > 8:
            index += 24
        elif index > 24:
            index += 24
        msd = int(math.floor(index / 10))
        lsd = index % 10
        if enable:
            self.log('Enable button: ' + str(orig_index) + ', ' + str(index) + ', ' + str(cc) + ', toggle: ' + str(toggleon) + ', enable: ' + str(enable))
            enable_button[0][17] = 48 + msd
            enable_button[0][18] = 48 + lsd
            msd = int(math.floor(cc / 10))
            lsd = cc % 10
            if cc >= 100:
                enable_button[2 if toggleon else 4][24] = 48 + (msd - 10)
                enable_button[2 if toggleon else 4][25] = 48 + lsd
            else:
                enable_button[1 if toggleon else 3][23] = 48 + msd
                enable_button[1 if toggleon else 3][24] = 48 + lsd
            self._send_bcl(enable_button[0])
            if cc >= 100:
                self._send_bcl(enable_button[2 if toggleon else 4])
            else:
                self._send_bcl(enable_button[1 if toggleon else 3])
        else:
            self.log('Disable button: ' + str(orig_index) + ', ' + str(index))
            disable_button[17] = 48 + msd
            disable_button[18] = 48 + lsd
            self._send_bcl(disable_button)
        if check:
            self._button_state[orig_index] = enable
        return True

    def _setup_static_controls(self, toggle_1, toggle_2, toggle_3, toggle_4):
        self.log('setup_static_controls: ' + str(toggle_1) + ', ' + str(toggle_2) + ', ' + str(toggle_3) + ', ' + str(toggle_4) + ', ')
        if not self._parent._dynamic:
            return
        self._bcl_start()
        self._button_setup(24, True, 105, False, 1, toggle_1)
        self._button_setup(25, True, 106, False, 1, toggle_2)
        self._button_setup(26, True, 107, False, 1, toggle_3)
        self._button_setup(27, True, 108, False, 1, toggle_4)
        if self._parent._enable_function:
            self._button_setup(28, True, 109, False)
            self._button_setup(29, True, 110, False)
            self._button_setup(30, True, 111, False)
            self._button_setup(31, True, 112, False)
        if not self._parent._has_pans:
            for i in range(8):
                self._encoder_setup(i + 8, True, i + 9, 1, False)

        self._bcl_end()

    def set_nav_buttons(self, toggleon):
        self.log('set_nav_buttons: toggle: ' + str(toggleon))
        if self._nav_is_toggle == -1 or self._nav_is_toggle != toggleon:
            self._button_setup(34, True, 113, False, 1, toggleon)
            self._button_setup(35, True, 114, False, 1, toggleon)
            self._nav_is_toggle = toggleon

    def setup_mixer_controls(self, num_tracks = -1, num_sends = -1, from_device = False, num_returns = -1, toggled_returns_action = -1):
        self.log('setup_mixer_controls: has_mixer: ' + str(hasattr(self._parent, '_mixer')) + ', from_device: ' + str(from_device) + ', toggled: ' + str(self._parent._returns_toggled) + ', toggled_returns_action: ' + str(toggled_returns_action) + ', opt: ' + str(self._optimise))
        if not self._parent._dynamic:
            return
        if self._mode != 0:
            return
        if hasattr(self._parent, '_mixer') == False:
            return
        num_tracks = self._parent._mixer._num_vis_tracks if num_tracks == -1 else num_tracks
        num_sends = self._parent._mixer.num_sends if num_sends == -1 else num_sends
        num_returns = self._parent._mixer._num_vis_returns if num_returns == -1 else num_returns
        self.log('setup_mixer_controls: mode: ' + str(self._mode) + ', tracks: ' + str(num_tracks) + ', sends: ' + str(num_sends) + ', from_device: ' + str(from_device) + ', num_returns: ' + str(num_returns))
        if not hasattr(self, '_encoder_state'):
            return
        opt = (from_device or toggled_returns_action == 0) and self._optimise
        updated = False
        if not opt:
            self._bcl_start()
        if self._parent._track_navigation:
            self.set_nav_buttons(True)
        enabled = range(8)
        is_master = range(8)
        is_ret = range(8)
        for x in range(8):
            enabled[x] = self._parent._mixer._is_track_enabled(x, num_tracks, num_returns, self._parent._returns_toggled)
            is_master[x] = self._parent._mixer._is_master_track(x, self._parent._returns_toggled)
            is_ret[x] = self._parent._mixer._is_return_track(x, num_tracks, num_returns)

        self.log('enabled: ' + str(enabled) + ', master: ' + str(is_master) + ', ret: ' + str(is_ret) + ', opt: ' + str(opt))
        for y in range(8):
            for x in range(8):
                master = is_master[x]
                if y == 0:
                    enable = enabled[x]
                    if self._bcf:
                        if opt:
                            self._fader_state[x] = enable
                        elif self._fader_setup(x, enable, x + (81 if not self._bit_14 else 0), 0):
                            updated = True
                    elif opt:
                        self._encoder_state[x] = enable
                        self._encoder_type[x] = 0 if is_ret[x] else 1
                    elif self._encoder_setup(x, enable, x + (1 if not self._bit_14 else 0), 0 if is_ret[x] else 1):
                        updated = True
                elif y == 1:
                    real_y = y - 1
                    enable = enabled[x]
                    i = real_y * 8 + x
                    if opt:
                        self._button_state[i] = enable
                    elif self._button_setup(i, enable, i + (33 if not self._bit_14 else 89)):
                        updated = True
                elif y == 2 or y == 3:
                    real_y = y - 2
                    enable = enabled[x] and not master
                    i = real_y * 8 + x
                    if opt:
                        self._button_state[i + 8] = enable
                    elif self._button_setup(i + 8, enable, i + 65):
                        updated = True
                elif y == 7:
                    enable = enabled[x]
                    if opt:
                        self._encoder_state[x + 8] = enable
                        self._encoder_type[x + 8] = 2
                    elif self._encoder_setup(x + 8, enable, x + (9 if not self._bit_14 else 81), 2):
                        updated = True
                elif self._bcf:
                    if y == 4:
                        enable = enabled[x] and not master
                        i = x
                        if opt:
                            self._encoder_state[i] = enable
                        elif self._encoder_setup(x, enable, x + (1 if not self._bit_14 else 8), 0):
                            updated = True
                else:
                    real_y = y - 4
                    enable = real_y < num_sends and enabled[x] and not master
                    i = real_y * 8 + x
                    if opt:
                        self._encoder_state[i + 16] = enable
                        self._encoder_type[i + 16] = 0
                    elif self._encoder_setup(i + 16, enable, i + (81 if not self._bit_14 else 8), 0):
                        updated = True

        if not opt:
            self._bcl_end()
            if updated and toggled_returns_action != 1:
                self._store()
        else:
            self._recall()
        self.log('setup_mixer_controls: completed, updated: ' + str(updated) + ', stored: ' + str(not opt and updated and toggled_returns_action != 1))
        self.log('setup_mixer_controls: encoders: ' + str(self._encoder_state) + ', types: ' + str(self._encoder_type))
        self.log('setup_mixer_controls: buttons: ' + str(self._button_state))
        return updated

    def setup_device_controls(self, active, channel_strip = False):
        num_params = len(active)
        self.log('setup_device_controls: ' + str(self._mode) + ', active: ' + str(active) + ', num: ' + str(num_params) + ', channel_strip: ' + str(channel_strip))
        if not self._parent._dynamic:
            return
        if self._mode != 1:
            return
        if not hasattr(self, '_encoder_state'):
            return
        if channel_strip:
            if hasattr(self._parent, '_mixer') == False:
                return
            num_tracks = self._parent._mixer._num_vis_tracks
            num_returns = self._parent._mixer._num_vis_returns
            enabled = range(8)
            is_ret = range(8)
            has_iso = range(8)
            for x in range(8):
                enabled[x] = self._parent._mixer._is_track_enabled(x, num_tracks, num_returns, self._parent._returns_toggled)
                is_ret[x] = self._parent._mixer._is_return_track(x, num_tracks, num_returns)
                has_iso[x] = self._parent._mixer._is_return_track(x, num_tracks, num_returns)

        updated = False
        opt = False
        self._bcl_start()
        if self._parent._track_navigation:
            self.set_nav_buttons(True if self._parent._channel_strip else False)
        num_rows = 1 if self._bcf else (4 if self._parent._use_32 else 3)
        for y in range(num_rows + (2 if channel_strip else 0)):
            for x in range(8):
                if y == num_rows:
                    enable = enabled[x]
                    if opt:
                        self._encoder_state[x] = enable
                        self._encoder_type[x] = 0 if is_ret[x] else 1
                    elif self._encoder_setup(x, enable, x + (1 if not self._bit_14 else 0), 0 if is_ret[x] else 1):
                        updated = True
                elif y == num_rows + 1:
                    enable = active[x]
                    i = 8 + x
                    if self._button_setup(i + 8, enable, i + 65):
                        updated = True
                else:
                    i = y * 8 + x
                    enable = i < num_params and active[i]
                    if self._parent._use_32 or self._bcf:
                        if y == 0:
                            if self._encoder_setup(x, enable, x + (1 if not self._bit_14 else 0), 1):
                                updated = True
                        elif self._encoder_setup(i + 8, enable, i + (73 if not self._bit_14 else 0), 0):
                            updated = True
                    elif self._encoder_setup(i + 16, enable, i + (81 if not self._bit_14 else 8), 0):
                        updated = True

        self._bcl_end()
        if not self._optimise and updated:
            self._store()
        self.log('setup_device_controls: completed, updated: ' + str(updated))
        self.log('setup_device_controls: encoders: ' + str(self._encoder_state) + ', types: ' + str(self._encoder_type))
        self.log('setup_device_controls: buttons: ' + str(self._button_state))
        return updated

    def setup_num_device_controls(self, num_devices):
        update = self._parent._dynamic and self._mode == 1
        self.log('setup_num_device_controls: ' + str(self._mode) + ', devices: ' + str(num_devices) + ', update: ' + str(update))
        if not update or not hasattr(self, '_encoder_state'):
            return
        updated = False
        self._bcl_start()
        for y in range(2):
            for x in range(8):
                enable = x < num_devices
                i = y * 8 + x
                if self._button_setup(i + 8, enable, i + 65):
                    updated = True

        self._bcl_end()
        self.log('setup_num_device_controls: completed, updated: ' + str(updated))
