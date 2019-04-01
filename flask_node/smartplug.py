"""
Energenie Smart Plug Raspberry Pi Hat Driver
"""

import time
import platform
from energenie import switch_on, switch_off

class SmartPlug():
    def __init__(self, socket):
        if socket not in [1, 2, 3, 4]:
            raise AttributeError('Socket must be in range 1-4')
        self.socket = socket

        self._is_on = None

        # Start off in known state
        self.off()

    def is_on(self):
        return self._is_on

    def on(self):
        switch_on(self.socket)
        self._is_on = True

    def off(self):
        switch_off(self.socket)
        self._is_on = False

    def train_socket(self):
        print('''
        ================================================
         Beginning manual socket training on socket: {}
        ================================================

        Hold green button on plug until LED flashes rapidly
        Note: LED will flash slowly at first, hold until it flashes faster

        Training will start in 10 seconds...
        '''.format(self.socket))

        time.sleep(10)
        for i in range(0, 4):
            self.on()
            time.sleep(0.25)

        print('Socket should now be trained')