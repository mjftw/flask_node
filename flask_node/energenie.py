"""
Energenie Smart Plug Raspberry Pi Hat Driver
"""

import platform

if platform.node() != 'raspberrypi':
    raise RuntimeError("This module only works on a Raspberry Pi!")

import time
import RPi.GPIO as GPIO


help_str = """
Guidance copied from Energenie sample program:

    OUT OF THE BOX: Plug the Pi Transmitter board into the Raspberry Pi
    GPIO pin-header ensuring correct polarity and pin alignment.

    The sockets will need to be inserted into separate mains wall sockets.
    with a physical separation of at least 2 metres to ensure they don't
    interfere with each other. Do not put into a single extension lead.

    For proper set up the sockets should be in their factory state with
    the red led flashing at 1 second intervals. If this is not the case for
    either socket, press and hold the green button on the front of the unit
    for 5 seconds or more until the red light flashes slowly.

    A socket in learning mode will be listening for a control code to be
    sent from a transmitter. A socket can pair with up to 2 transmitters
    and will accept the following code pairs

    0011 and 1011 all sockets ON and OFF
    1111 and 0111 socket 1 ON and OFF
    1110 and 0110 socket 2 ON and OFF
    1101 and 0101 socket 3 ON and OFF
    1100 and 0100 socket 4 ON and OFF

    A socket in learning mode should accept the first code it receives
    If you wish the sockets to react to different codes, plug in and
    program first one socket then the other using this program.

    When the code is accepted you will see the red lamp on the socket
    flash quickly then extinguish
"""

class SmartPlug():
    pinmap = {
        'k3': 11, 'k2': 15, 'k1': 16, 'k0': 13,
        'mod_sel': 18, 'mod_en': 22
    }
    socket_map = {
        'all': {'on': '1011', 'off': '0011'},
        '1':   {'on': '1111', 'off': '0111'},
        '2':   {'on': '1110', 'off': '0110'},
        '3':   {'on': '1101', 'off': '0101'},
        '4':   {'on': '1100', 'off': '0100'}
    }

    def __init__(self):
        self._gpio_init()

    def train_socket(self, socket):
        self._check_socket(socket)
        print("================================================")
        print(" Beginning manual socket training on socket: {}".format(socket))
        print("================================================")
        print(help_str)
        print('')

        input('Put socket in training mode and press enter')
        for i in range(0, 4):
            self.set_socket(socket, 'on')
            time.sleep(0.25)

        print('Socket should now be trained')
        input('Press enter to test training by toggling socket twice')
        self.set_socket(socket, 'off')
        time.sleep(0.5)
        self.set_socket(socket, 'on')
        time.sleep(0.5)
        self.set_socket(socket, 'off')
        time.sleep(0.5)
        self.set_socket(socket, 'on')
        time.sleep(0.5)


    def set_socket(self, socket, state):
        self._check_socket(socket)

        if isinstance(socket, int):
            socket = str(socket)

        for k, v in enumerate(self.socket_map[socket][state]):
            # Set K0-K3
            GPIO.output(self.pinmap['k{}'.format(k)], bool(int(v)))

        # Let these settle (required for encoder)
        time.sleep(0.1)

        # Enable modulator
        GPIO.output(self.pinmap['mod_en'], True)

        # Wait a period
        time.sleep(0.25)

        # Disable modulator
        GPIO.output(self.pinmap['mod_en'], False)


    def _check_socket(self, socket):
        if socket != 'all' and (int(socket) < 1 or int(socket) > 4):
            raise RuntimeError("Socket number must be 1-4 or 'all'")

    def _gpio_init(self):
        # set the pins numbering mode
        GPIO.setmode(GPIO.BOARD)

        # Select the GPIO pins used for the encoder K0-K3 data inputs
        GPIO.setup(self.pinmap['k3'], GPIO.OUT)
        GPIO.setup(self.pinmap['k2'], GPIO.OUT)
        GPIO.setup(self.pinmap['k1'], GPIO.OUT)
        GPIO.setup(self.pinmap['k0'], GPIO.OUT)

        # Select the signal to select ASK/FSK
        GPIO.setup(self.pinmap['mod_sel'], GPIO.OUT)

        # Select the signal used to enable/disable the modulator
        GPIO.setup(self.pinmap['mod_en'], GPIO.OUT)

        # Disable the modulator by setting CE pin lo
        GPIO.output(self.pinmap['mod_en'], False)

        # Set the modulator to ASK for On Off Keying
        # by setting MODSEL pin lo
        GPIO.output(self.pinmap['mod_sel'], False)

        # Initialise K0-K3 inputs of the encoder to 0000
        GPIO.output(self.pinmap['k3'], False)
        GPIO.output(self.pinmap['k2'], False)
        GPIO.output(self.pinmap['k1'], False)
        GPIO.output(self.pinmap['k0'], False)
