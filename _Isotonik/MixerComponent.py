#Embedded file name: MixerComponent.py
""" (c) 2014-20 Sigabort, Lee Huddleston, Isotonik Studios; admin@sigabort.co, http://sigabort.co, http://www.isotonikstudios.com """
import math
from os import path
g_path = path.dirname(path.realpath(__file__))
g_push = g_path.find('Push') != -1
g_v2_api = g_push and path.isdir(g_path + '/../ableton/v2')
from _Framework.Control import control_list, ButtonControl
from _Framework.ChannelStripComponent import ChannelStripComponent as ChannelStripComponentBase
from _Framework.MixerComponent import MixerComponent as MixerComponentBase
if g_v2_api:
    from ableton.v2.base import listens, Subject
else:
    from _Framework.SubjectSlot import subject_slot, Subject

def repr3(input_str):
    try:
        output_st = unicodedata.normalize('NFKD', input_str).encode('ascii', 'ignore')
        if output_st != None:
            return output_st
        return ''
    except:
        x = repr(input_str)
        return x[2:-1]


class ChannelStripComponent(ChannelStripComponentBase):
    send_lights = control_list(ButtonControl, control_count=3, color='Mixer.Sends', disabled_color='Mixer.NoTrack')
    pan_light = ButtonControl(color='Mixer.Pans', disabled_color='Mixer.NoTrack')

    def __init__(self, parent, mixer):
        self._parent = parent
        self._mixer = mixer
        self._is_return = False
        self._num_sends_to_display = 0
        self._valid_track = False
        self._track = None
        self._index = -1
        super(ChannelStripComponent, self).__init__()

    def log(self, msg):
        self._mixer.log(msg)

    def set_track(self, track, index = -1, num_sends_to_display = 0, is_return = False, is_master = False):
        self._valid_track = bool(track)
        super(ChannelStripComponent, self).set_track(track)
        self._track = track
        self._index = index
        self.log('set_track: ' + ('Empty' if track == None else repr3(track.name)) + ', index: ' + str(index))
        if index != -1:
            col = 'Mixer.ArmSelected' if is_return else (63 if is_master else 'Mixer.Sends')
            self.send_lights[0].color = col
            self.send_lights[1].color = col
            self.send_lights[2].color = col
        self.log('select: ' + str(self._select_button) + ', ' + str(bool(track)))
        self._set_send_lights(num_sends_to_display)
        self.pan_light.enabled = bool(track)

    def set_num_sends_to_display(self, num_sends_to_display):
        self._set_send_lights(num_sends_to_display)

    def _set_send_lights(self, num_sends_to_display):
        self._num_sends_to_display = num_sends_to_display
        send_num = 0
        for light in self.send_lights:
            if send_num < num_sends_to_display:
                light.enabled = self._valid_track
            else:
                light.enabled = False
            send_num += 1

    def _connect_parameters(self):
        if self._parent._LOG_PARAMS:
            self.log('strip:_connect_parameters: vol: ' + repr3(self._track.name) + ', ' + str(self._track.mixer_device.volume) + ', ' + str(self._track.mixer_device.volume.value))
        i = 0
        for control in self._send_controls:
            if control != None:
                if i < len(self._track.mixer_device.sends):
                    if self._parent._LOG_PARAMS:
                        self.log('strip:_connect_parameters: send: ' + str(i) + ': ' + str(self._track.mixer_device.sends[i]) + ', ' + str(self._track.mixer_device.sends[i].value))
                    i += 1

        super(ChannelStripComponent, self)._connect_parameters()

    def set_select_button(self, button):
        super(ChannelStripComponent, self).set_select_button(button)
        self._on_select.subject = button

    if g_v2_api:

        @listens('value')
        def _on_select(self, value):
            self.__on_select(value)

    else:

        @subject_slot('value')
        def _on_select(self, value):
            self.__on_select(value)

    def __on_select(self, value):
        if self._mixer._select_track_on_0_val:
            if value == 127:
                self.log('strip:_on_select: ' + str(value) + ', select_track_on_0_val: ' + str(self._mixer._select_track_on_0_val) + ', process: False')
                self._mixer._track_changed = False
                return
            changed = self._mixer._track_changed
        else:
            changed = self._mixer._selected_track != self._parent.song().view.selected_track
        self._parent.log('strip:_on_select: ' + str(value) + ', select_track_on_0_val: ' + str(self._mixer._select_track_on_0_val) + ', process: True, selected: ' + repr3(self._parent.song().view.selected_track.name) + ', changed: ' + str(changed))
        if self._parent.song().view.selected_track != None and not changed:
            if self._mixer._select_track_on_0_val and value == 0 or not self._mixer._select_track_on_0_val:
                if self._valid_track:
                    self._mixer.same_track_selected()


class MixerComponent(MixerComponentBase):
    encoder_rings = control_list(ButtonControl, control_count=24, enabled=False)
    next_sends_button = ButtonControl()
    prev_sends_button = ButtonControl()

    def __init__(self, parent, num_tracks, sends_rows = 1, show_returns = False, fold_on_reselect = False, select_track_on_0_val = True, max_returns = -1, show_master = False, delayed_update = False, *a, **k):
        self._parent = parent
        self._sends_rows = sends_rows
        self._show_returns = show_returns
        self._max_returns = max_returns
        self._num_sends_to_display = 0
        self._track_changed = False
        self._fold_on_reselect = fold_on_reselect
        self._select_track_on_0_val = select_track_on_0_val
        self._show_master = show_master
        self._delayed_update = delayed_update
        self._skip_delayed = False
        self._selected_track_index = 0
        self._last_selected_track_index = 0
        self._show_send_buttons = True
        super(MixerComponent, self).__init__(num_tracks, *a, **k)
        self._update_send_buttons()
        self._encoder_state = []
        self._button_state = []
        for i in range(32):
            if i < 24:
                self._button_state.append(False)
            self._encoder_state.append(False)

    def log(self, msg, force = False):
        if hasattr(self, '_parent'):
            self._parent.log(msg, force)

    def debug(self, msg, force = False):
        if hasattr(self, '_parent') and hasattr(self._parent, 'debug'):
            self._parent.debug(msg, force)

    def msg(self, msg):
        if hasattr(self, '_parent'):
            self._parent.show_message(msg)

    def on_selected_track_changed(self):
        self.log('MixerComponent:on_selected_track_changed')
        self._track_changed = True
        self._selected_track = self._parent.song().view.selected_track
        self._last_selected_track_index = self._selected_track_index
        self._selected_track_index = 0
        for index, channel_strip in enumerate(self._channel_strips):
            if self._selected_track == channel_strip._track:
                self._selected_track_index = index
                break

        self.log('MixerComponent:on_selected_track_changed: index: ' + str(self._selected_track_index) + ', last: ' + str(self._last_selected_track_index))
        if hasattr(self, '_parent'):
            self._parent.on_selected_track_changed()

    def _create_strip(self):
        self.log('_create_strip')
        return ChannelStripComponent(self._parent, self)

    def same_track_selected(self):
        self.log('same_track_selected: fold: ' + str(self._fold_on_reselect))
        cont = True
        if hasattr(self, '_parent') and hasattr(self._parent, 'same_track_selected'):
            cont = self._parent.same_track_selected()
        if cont and self._fold_on_reselect:
            selected = self._parent.song().view.selected_track
            if selected.is_foldable:
                selected.fold_state = not selected.fold_state

    def set_send_controls(self, controls):
        self._send_controls = controls
        for index, channel_strip in enumerate(self._channel_strips):
            if self.send_index is None:
                channel_strip.set_send_controls([None])
            else:
                send_controls = [ controls.get_button(index, i) for i in xrange(self._sends_rows) ] if controls else [None]
                skipped_sends = [ None for _ in xrange(self.send_index) ]
                channel_strip.set_send_controls(skipped_sends + send_controls)

    def set_volume_controls(self, controls):
        for strip, control in map(None, self._channel_strips, controls or []):
            strip.set_volume_control(control)

    def set_send_lights(self, lights):
        for index, channel_strip in enumerate(self._channel_strips):
            elements = None
            if lights is not None:
                lights.reset()
                elements = None if self.send_index is None else [ lights.get_button(index, i) for i in xrange(self._sends_rows) ]
            channel_strip.send_lights.set_control_element(elements)

    def set_pan_lights(self, lights):
        for strip, light in map(None, self._channel_strips, lights or []):
            strip.pan_light.set_control_element(light)

    def _get_send_index(self):
        return super(MixerComponent, self)._get_send_index()

    def _set_send_index(self, index):
        self.log('mixer:_set_send_index: ' + str(index))
        if index is not None and index % self._sends_rows > 0:
            index -= index % self._sends_rows
        self.log('mixer:_set_send_index: real_index: ' + str(index))
        super(MixerComponent, self)._set_send_index(index)
        self._update_send_buttons()

    send_index = property(_get_send_index, _set_send_index)

    def _update_send_buttons(self):
        self.log('_update_send_buttons')
        self.next_sends_button.enabled = self._show_send_buttons and self.send_index is not None and self.send_index < self.num_sends - self._sends_rows
        self.prev_sends_button.enabled = self._show_send_buttons and self.send_index is not None and self.send_index > 0
        num_to_display = min(self._sends_rows, self.num_sends - (self.send_index if self.send_index != None else 0))
        self._num_sends_to_display = num_to_display
        self.log('_update_send_buttons: up: ' + str(self.next_sends_button.enabled) + ', down: ' + str(self.prev_sends_button.enabled) + ', to_display: ' + str(num_to_display))
        if self.send_index != None:
            self.msg('Controlling sends ' + str(self.send_index + 1) + ' to ' + str(self.send_index + num_to_display))
        for index in range(len(self._channel_strips)):
            self._channel_strips[index].set_num_sends_to_display(num_to_display)

        updated = self._setup_mixer_controls(self._num_vis_tracks, self._num_vis_returns, self._sends_rows, num_to_display)

    @next_sends_button.pressed
    def next_sends_button(self, button):
        self.log('next_sends_button: ' + str(button))
        self.send_index = min(self.send_index + self._sends_rows, self.num_sends - 1)

    @prev_sends_button.pressed
    def prev_sends_button(self, button):
        self.log('prev_sends_button: ' + str(button))
        self.send_index = max(self.send_index - self._sends_rows, 0)

    def set_track_select_buttons(self, buttons):
        for strip, button in map(None, self._channel_strips, buttons or []):
            if button:
                if hasattr(button, 'set_on_off_values'):
                    button.set_on_off_values('Mixer.TrackSelected', 'Mixer.TrackUnselected')
                button._strip = strip
            strip.set_select_button(button)

    def set_solo_buttons(self, buttons):
        for strip, button in map(None, self._channel_strips, buttons or []):
            if button:
                if hasattr(button, 'set_on_off_values'):
                    button.set_on_off_values('Mixer.SoloOn', 'Mixer.SoloOff')
                button._strip = strip
            strip.set_solo_button(button)

    def set_mute_buttons(self, buttons):
        for strip, button in map(None, self._channel_strips, buttons or []):
            if button:
                if hasattr(button, 'set_on_off_values'):
                    button.set_on_off_values('Mixer.MuteOn', 'Mixer.MuteOff')
                button._strip = strip
            strip.set_mute_button(button)

    def set_arm_buttons(self, buttons):
        for strip, button in map(None, self._channel_strips, buttons or []):
            if button:
                if hasattr(button, 'set_on_off_values'):
                    button.set_on_off_values('Mixer.ArmSelected', 'Mixer.ArmUnselected')
                button._strip = strip
            strip.set_arm_button(button)

    def set_track_offset(self, new_offset):
        self.log('set_track_offset: ' + str(new_offset))
        super(MixerComponent, self).set_track_offset(new_offset)

    def _is_track_enabled(self, x, num_vis_tracks, num_vis_returns, toggle_returns = False):
        if self._show_returns:
            if self._show_returns == 3:
                enabled = toggle_returns == False and x < num_vis_tracks or toggle_returns == True and (x < num_vis_returns or self._show_master and x == 7)
            elif self._show_returns == 4:
                enabled = toggle_returns == False and x < num_vis_tracks or toggle_returns == True and (x < num_vis_tracks or x >= (8 if not self._show_master else 7) - num_vis_returns)
            else:
                enabled = x < num_vis_tracks or x >= (8 if not self._show_master else 7) - num_vis_returns
        else:
            enabled = x < num_vis_tracks
        self.debug('_is_track_enabled: x: ' + str(x) + ', tracks: ' + str(num_vis_tracks) + ', returns: ' + str(num_vis_returns) + ', returns_toggled: ' + str(toggle_returns) + ', enabled: ' + str(enabled))
        return enabled

    def _is_return_track(self, x, num_vis_tracks, num_vis_returns, toggle_returns = False):
        if self._show_returns:
            if self._show_returns == 3:
                ret = toggle_returns and x < num_vis_returns
            elif self._show_master and self._master_visible:
                ret = x >= 7 - num_vis_returns and x != 7
            else:
                ret = x >= 8 - num_vis_returns
        else:
            ret = False
        self.debug('_is_return_track: x: ' + str(x) + ', tracks: ' + str(num_vis_tracks) + ', returns: ' + str(num_vis_returns) + ', return: ' + str(ret))
        return ret

    def _is_master_track(self, x, toggle_returns = False):
        if self._show_returns and self._show_master:
            if self._show_returns == 3:
                ret = toggle_returns and self._master_visible and x == 7
            else:
                ret = self._master_visible and x == 7
        else:
            ret = False
        self.debug('_is_master_track: x: ' + str(x) + ', master: ' + str(ret))
        return ret

    def dump_state(self):
        self.log('DUMP: _reassign_tracks: show_returns: ' + str(self._show_returns) + ', vis_tracks: ' + str(self._num_vis_tracks) + ', vis_returns: ' + str(self._num_vis_returns) + ', empty: ' + str(self._num_empty_tracks) + ', offset: ' + str(self._track_offset))

    def _reassign_tracks(self, toggled_returns_action = -1):
        self.log('_reassign_tracks: toggled: ' + str(toggled_returns_action) + ', skip_delayed: ' + str(self._skip_delayed))
        tracks = self.tracks_to_use()
        returns = self.song().return_tracks
        track_offset = 0
        show_returns = self._show_returns
        toggled_returns = self._parent._returns_toggled
        if hasattr(self._parent, '_session'):
            track_offset = self._parent._session.track_offset()
        else:
            track_offset = self._track_offset
        self._num_empty_tracks = max(0, len(self._channel_strips) + self._track_offset - len(tracks))
        if show_returns == 0 or show_returns == 1:
            self._num_vis_tracks = min(8, len(tracks) - track_offset)
            self._num_empty_tracks = max(0, 8 - self._num_vis_tracks)
            self._num_vis_returns = min(len(returns), self._num_empty_tracks)
            if self._max_returns != -1:
                self._num_vis_returns = min(self._num_vis_returns, self._max_returns)
            self._num_empty_tracks -= self._num_vis_returns
            self._master_visible = self._show_master and show_returns == 1 and self._num_empty_tracks
        elif show_returns == 2:
            self._num_vis_returns = min(8, len(returns))
            if self._max_returns != -1:
                self._num_vis_returns = min(self._num_vis_returns, self._max_returns)
            self._num_vis_tracks = min(8 - self._num_vis_returns, len(tracks) - track_offset)
            self._num_empty_tracks = max(0, self._num_vis_returns + self._num_vis_tracks)
            self._master_visible = self._show_master
        elif show_returns == 3:
            self._num_vis_tracks = min(8, len(tracks) - track_offset) if toggled_returns == False else 0
            self._num_vis_returns = min(8, len(returns)) if toggled_returns == True else 0
            self._num_empty_tracks = 8 - self._num_vis_tracks - self._num_vis_returns
            self._master_visible = self._show_master
        elif show_returns == 4:
            self._num_vis_returns = min(8, len(returns)) if toggled_returns == True else 0
            if self._max_returns != -1:
                self._num_vis_returns = min(self._num_vis_returns, self._max_returns)
            self._num_vis_tracks = min(8 - self._num_vis_returns, len(tracks) - track_offset)
            self._num_empty_tracks = max(0, self._num_vis_returns + self._num_vis_tracks)
            self._master_visible = self._show_master
        self._num_empty_tracks -= 1 if self._master_visible else 0
        self.log('_reassign_tracks: show_returns: ' + str(show_returns) + ', vis_tracks: ' + str(self._num_vis_tracks) + ', vis_returns: ' + str(self._num_vis_returns) + ', empty: ' + str(self._num_empty_tracks) + ', toggled_returns: ' + str(toggled_returns) + ', offset: ' + str(self._track_offset) + ', master_vis: ' + str(self._master_visible))
        if self._delayed_update and self._skip_delayed:
            self._skip_delayed = False
            self.map_controls()
        else:
            if self._show_returns:
                updated = self._setup_mixer_controls(self._num_vis_tracks, self._num_vis_returns, self._sends_rows, self._num_sends_to_display, toggled_returns_action)
            else:
                updated = self._setup_mixer_controls(self._num_vis_tracks, 0, self._sends_rows, self._num_sends_to_display)
            if not self._delayed_update or not updated:
                self.map_controls()

    def map_controls(self):
        self.log('MixerComponent:map_controls')
        ret_index = 0
        tracks = self.tracks_to_use()
        if self._show_returns:
            returns = self.song().return_tracks
            toggled_returns = self._parent._returns_toggled
            for index in range(len(self._channel_strips)):
                track = None
                if self._is_return_track(index, self._num_vis_tracks, self._num_vis_returns, toggled_returns):
                    track = returns[ret_index]
                    self._channel_strips[index].set_track(track, index, self._num_sends_to_display, True)
                    ret_index += 1
                elif self._is_master_track(index, toggled_returns):
                    track = self._parent.song().master_track
                    self._channel_strips[index].set_track(track, index, self._num_sends_to_display, False, True)
                elif index < self._num_vis_tracks:
                    track = tracks[self._track_offset + index]
                    self._channel_strips[index].set_track(track, index, self._num_sends_to_display)
                else:
                    self._channel_strips[index].set_track(None)
                if track != None:
                    self.log('MixerComponent:map_controls: Assigned track: ' + repr3(track.name) + ', index: ' + str(index))

        else:
            self.log('MixerComponent:map_controls: num_tracks: ' + str(len(tracks)) + ', num_strips: ' + str(len(self._channel_strips)) + ', offset: ' + str(self._track_offset) + ', num_vis: ' + str(self._num_vis_tracks), False)
            for index in range(min(len(tracks), len(self._channel_strips))):
                self.log('track: ' + str(index) + ': ' + repr3(tracks[index].name))
                track = None
                if index < self._num_vis_tracks:
                    track = tracks[self._track_offset + index]
                    self._channel_strips[index].set_track(track, index, self._num_sends_to_display)
                else:
                    self._channel_strips[index].set_track(None)
                if track != None:
                    self.log('MixerComponent:map_controls: Assigned track: ' + repr3(track.name) + ', index: ' + str(index))

    def on_num_sends_changed(self):
        self.log('on_num_sends_changed: ' + str(self.num_sends))
        super(MixerComponent, self).on_num_sends_changed()

    def _setup_mixer_controls(self, num_vis_tracks = -1, num_vis_returns = -1, num_sends_rows = -1, num_sends_to_display = -1, toggled_returns_action = -1):
        pass
