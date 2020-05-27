#Embedded file name: ControlElementUtils.py
""" (c) 2014-20 Sigabort, Lee Huddleston, Isotonik Studios; admin@sigabort.co, http://sigabort.co, http://www.isotonikstudios.com """
import Live
from _Framework.Dependency import depends
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.SliderElement import SliderElement
from _Framework.EncoderElement import EncoderElement
from .ButtonElement import ButtonElement
import logging
logger = logging.getLogger(__name__)

@depends(skin=None)
def make_note_button(identifier, name, ch = 0, skin = None, double_click = False):
    if skin != None:
        return ButtonElement(True, MIDI_NOTE_TYPE, ch, identifier, name=name, skin=skin)
    return ButtonElement(True, MIDI_NOTE_TYPE, ch, identifier, name=name)


@depends(skin=None)
def make_mom_cc_button(identifier, name, ch = 0, skin = None):
    if skin != None:
        return ButtonElement(False, MIDI_CC_TYPE, ch, identifier, name=name, skin=skin)
    return ButtonElement(False, MIDI_CC_TYPE, ch, identifier, name=name)


@depends(skin=None)
def make_cc_button(identifier, name, ch = 0, skin = None):
    if skin != None:
        return ButtonElement(True, MIDI_CC_TYPE, ch, identifier, name=name, skin=skin)
    return ButtonElement(True, MIDI_CC_TYPE, ch, identifier, name=name)


def make_slider(identifier, name, ch = 0, skin = None):
    return SliderElement(MIDI_CC_TYPE, ch, identifier, name=name)


def make_abs_encoder(identifier, name, ch = 0, skin = None):
    return EncoderElement(MIDI_CC_TYPE, ch, identifier, map_mode=Live.MidiMap.MapMode.absolute, name=name)


def make_rel_encoder(identifier, name, ch = 0, skin = None):
    return EncoderElement(MIDI_CC_TYPE, ch, identifier, map_mode=Live.MidiMap.MapMode.relative_two_compliment, name=name)


def make_button_row(identifier_sequence, element_factory, name, ch = 0, skin = None):
    if skin != None:
        return ButtonMatrixElement(rows=[ [element_factory(identifier, name + '_%d' % index, ch=ch, skin=skin)] for index, identifier in enumerate(identifier_sequence) ])
    return ButtonMatrixElement(rows=[ [element_factory(identifier, name + '_%d' % index, ch=ch)] for index, identifier in enumerate(identifier_sequence) ])


def make_button_list(identifiers, element_factory, name, ch = 0, skin = None):
    if skin == None:
        return [ element_factory(identifier, name % (i + 1), ch) for i, identifier in enumerate(identifiers) ]
    return [ element_factory(identifier, name % (i + 1), ch, skin) for i, identifier in enumerate(identifiers) ]
