#APC40plus
# http://remotescripts.blogspot.com
#FOR CODING STUDY ONLY
from APC40.APC40 import *

class APC40plus1(APC40):
    __module__ = __name__
    __doc__ = ' Main class derived from APC40 '
    def __init__(self, c_instance):
        APC40.__init__(self, c_instance)
        self.show_message("APC40plus1 script loaded")

    def _setup_device_and_transport_control(self): #overriden so that we can to reassign the metronome button to device lock
        is_momentary = True
        device_bank_buttons = []
        device_param_controls = []
        bank_button_labels = ('Clip_Track_Button', 'Device_On_Off_Button', 'Previous_Device_Button', 'Next_Device_Button', 'Detail_View_Button', 'Rec_Quantization_Button', 'Midi_Overdub_Button', 'Device_Lock_Button')
        for index in range(8):
            device_bank_buttons.append(ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 58 + index))
            device_bank_buttons[-1].name = bank_button_labels[index]
            ring_mode_button = ButtonElement(not is_momentary, MIDI_CC_TYPE, 0, 24 + index)
            ringed_encoder = RingedEncoderElement(MIDI_CC_TYPE, 0, 16 + index, Live.MidiMap.MapMode.absolute)
            ringed_encoder.set_ring_mode_button(ring_mode_button)
            ringed_encoder.name = 'Device_Control_' + str(index)
            ring_mode_button.name = ringed_encoder.name + '_Ring_Mode_Button'
            device_param_controls.append(ringed_encoder)
        device = ShiftableDeviceComponent()
        device.name = 'Device_Component'
        device.set_bank_buttons(tuple(device_bank_buttons))
        device.set_shift_button(self._shift_button)
        device.set_parameter_controls(tuple(device_param_controls))
        device.set_on_off_button(device_bank_buttons[1])
        device.set_lock_button(device_bank_buttons[7]) #assign device lock to bank_button 8 (in place of metronome)...
        self.set_device_component(device)
        detail_view_toggler = DetailViewControllerComponent()
        detail_view_toggler.name = 'Detail_View_Control'
        detail_view_toggler.set_shift_button(self._shift_button)
        detail_view_toggler.set_device_clip_toggle_button(device_bank_buttons[0])
        detail_view_toggler.set_detail_toggle_button(device_bank_buttons[4])
        detail_view_toggler.set_device_nav_buttons(device_bank_buttons[2], device_bank_buttons[3])
        transport = ShiftableTransportComponent()
        transport.name = 'Transport'
        play_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 91)
        stop_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 92)
        record_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 93)
        nudge_up_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 100)
        nudge_down_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 101)
        tap_tempo_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 99)
        play_button.name = 'Play_Button'
        stop_button.name = 'Stop_Button'
        record_button.name = 'Record_Button'
        nudge_up_button.name = 'Nudge_Up_Button'
        nudge_down_button.name = 'Nudge_Down_Button'
        tap_tempo_button.name = 'Tap_Tempo_Button'
        transport.set_shift_button(self._shift_button)
        transport.set_play_button(play_button)
        transport.set_stop_button(stop_button)
        transport.set_record_button(record_button)
        transport.set_nudge_buttons(nudge_up_button, nudge_down_button)
        transport.set_tap_tempo_button(tap_tempo_button)
        transport.set_quant_toggle_button(device_bank_buttons[5])
        transport.set_overdub_button(device_bank_buttons[6])
        #transport.set_metronome_button(device_bank_buttons[7]) #using this button for lock to device instead...
        bank_button_translator = ShiftableTranslatorComponent()
        bank_button_translator.set_controls_to_translate(tuple(device_bank_buttons))
        bank_button_translator.set_shift_button(self._shift_button)
