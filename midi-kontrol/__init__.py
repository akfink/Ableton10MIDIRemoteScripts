import Live
from MidiKontrol import MidiKontrol
#from MidiKontrolScript import MidiKontrolScript
from Tracing import Traced

def create_instance(c_instance):
    file = open("/tmp/foo", "a")
    file.write("midikontrol\n")
    file.close()
    
    return MidiKontrol(c_instance)
    return false
