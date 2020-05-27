#Embedded file name: ButtonElement.py
""" (c) 2014-20 Sigabort, Lee Huddleston, Isotonik Studios; admin@sigabort.co, http://sigabort.co, http://www.isotonikstudios.com """
from _Framework.ButtonElement import ON_VALUE, OFF_VALUE, ButtonValue, ButtonElement as ButtonElementBase
import inspect
import traceback
import logging
logger = logging.getLogger(__name__)

class DoubleClickContext(object):
    control_state = None
    click_count = 0

    def set_new_context(self, control_state):
        self.control_state = control_state
        self.click_count = 0


class ButtonElement(ButtonElementBase):
    _on_value_out = None
    _off_value_out = None
    _on_value = ON_VALUE
    _off_value = OFF_VALUE
    _real_value = 0
    _flash_rate = 2
    _is_flashing = False
    _is_on = False
    _flash_on_out = 127
    _flash_off_out = 0
    _strip = None

    def __init(self, *a, **k):
        ButtonElementBase.__init__(a, k)

    @property
    def in_use(self):
        if self._strip == None:
            return True
        return self._strip._valid_track

    def __str__(self):
        return self.name + ': is_on: ' + str(self._is_on) + ', is_flashing: ' + str(self._is_flashing) + ', strip: ' + str(self._strip != None) + ', in_use: ' + str(self.in_use) + ', real_val: ' + str(int(self._real_value))

    def reset(self):
        self._on_value_out = None
        self._off_value_out = None
        super(ButtonElement, self).reset()

    def set_on_off_values(self, on_value, off_value):
        self._on_value_out = on_value
        self._off_value_out = off_value

    def do_flash(self, state, state_2, state_3):
        if self._is_flashing and self._is_on and self.in_use:
            if self._flash_rate == 1:
                super(ButtonElement, self).send_value(self._flash_on_out if state else self._flash_off_out)
            elif self._flash_rate == 2:
                super(ButtonElement, self).send_value(self._flash_on_out if state_2 else self._flash_off_out)
            else:
                super(ButtonElement, self).send_value(self._flash_on_out if state_3 else self._flash_off_out)

    def send_value(self, value, **k):
        log = False
        if log:
            logger.info('send_value: ' + str(self) + ': ' + str(int(value)))
        self._is_on = value == self._on_value
        if self._real_value == 125 or self._real_value == 124 or self._real_value == 123:
            self._is_flashing = False
        self._real_value = value
        if value == 126:
            value = 127 if self.in_use else 0
        elif value == 125 or value == 124 or value == 123:
            self._is_flashing = True
            self._is_on = True
            self._flash_rate = 1 if value == 124 else (2 if value == 125 else 3)
            value = 127
        if value is ON_VALUE and self._on_value_out is not None:
            if self.in_use:
                self._skin[self._on_value_out].draw(self)
            else:
                if log:
                    logger.info('send_value: sent: 0')
                super(ButtonElement, self).send_value(0)
        elif value is OFF_VALUE and self._off_value_out is not None:
            if self.in_use:
                self._skin[self._off_value_out].draw(self)
            else:
                if log:
                    logger.info('send_value: sent: 0')
                super(ButtonElement, self).send_value(0)
        else:
            if log:
                logger.info('send_value: sent: ' + str(int(value)))
            super(ButtonElement, self).send_value((value if self.in_use else 0), **k)
