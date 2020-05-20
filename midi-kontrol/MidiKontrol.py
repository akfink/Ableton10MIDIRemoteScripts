import Live
from MidiKontrolScript import MidiKontrolScript
from MidiKontrolMixerController import MidiKontrolMixerController
from MidiKontrolDeviceController import MidiKontrolDeviceController
from consts import *

class MidiKontrol(MidiKontrolScript):
    __module__ = __name__
    __doc__ = 'Automap script for MidiKontrol controllers'
    __name__ = "MidiKontrol Remote Script"
    
    def __init__(self, c_instance):
        self.suffix = ""
	MidiKontrol.realinit(self, c_instance)

    def realinit(self, c_instance):
	MidiKontrolScript.realinit(self, c_instance)
	self.mixer_controller = MidiKontrolMixerController(self)
	self.device_controller = MidiKontrolDeviceController(self)
        self.components = [ self.mixer_controller, self.device_controller ]

    def suggest_map_mode(self, cc_no):
        return Live.MidiMap.MapMode.absolute
