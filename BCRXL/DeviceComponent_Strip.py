#Embedded file name: DeviceComponent_Strip.py
""" (c) 2015 Sigabort, Lee Huddleston, Isotonik Studios; admin@sigabort.co, http://sigabort.co, http://www.isotonikstudios.com """
import Live
from _Isotonik.globals import *
if g_strip:
    from _Isotonik.DeviceComponent_Strip import DeviceComponent_Strip as DeviceComponentBase
else:
    from _Isotonik.DeviceComponent import DeviceComponent as DeviceComponentBase

class DeviceComponent_Strip(DeviceComponentBase):

    def __init__(self, controller, *a, **k):
        self._parent = controller
        super(DeviceComponent_Strip, self).__init__(controller, *a, **k)

    def _setup_device_controls(self, active, update_top_encoders = False):
        self.log('BCR: _setup_device_controls: active: ' + str(active))
        return self._parent._bcr_controls.setup_device_controls(active, update_top_encoders)

    def _setup_num_device_controls(self, num_devices):
        self.log('BCR: _setup_num_device_controls: num: ' + str(num_devices))
        self._parent._bcr_controls.setup_num_device_controls(num_devices)
