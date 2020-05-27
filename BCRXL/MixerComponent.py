#Embedded file name: MixerComponent.py
""" (c) 2015 Sigabort, Lee Huddleston, Isotonik Studios; admin@sigabort.co, http://sigabort.co, http://www.isotonikstudios.com """
import Live
from _Isotonik.MixerComponent import MixerComponent as MixerComponentBase

class MixerComponent(MixerComponentBase):

    def __init__(self, controller, num_tracks, sends_rows = 2, show_returns = 0, *a, **k):
        self._parent = controller
        super(MixerComponent, self).__init__(controller, num_tracks, sends_rows, show_returns, fold_on_reselect=False, select_track_on_0_val=False, *a, **k)

    def _setup_mixer_controls(self, num_vis_tracks = -1, num_vis_returns = -1, num_sends_rows = -1, num_sends_to_display = -1, toggled_returns_action = -1):
        self._parent.log('BCR: _setup_mixer_controls: vis_tracks: ' + str(num_vis_tracks) + ', num_vis_returns: ' + str(num_vis_returns) + ', num_sends_rows: ' + str(num_sends_rows) + ', num_sends_to_display: ' + str(num_sends_to_display))
        if hasattr(self._parent, '_bcr_controls'):
            self._parent._bcr_controls.setup_mixer_controls(num_vis_tracks, num_sends_to_display, False, -1, toggled_returns_action)

    def show_selected_track(self, toggle):
        pass
