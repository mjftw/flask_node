import time
from datetime import datetime

from .remoteobj import RxClass

class TempController():
    def __init__(self, temp_host, temp_port, plug_host, plug_port,
            target_temp, tolerance):
        self.temp = RxClass(host=temp_host, port=temp_port)
        self.plug = RxClass(host=plug_host, port=plug_port)
        self.target_temp = target_temp
        self.tolerance = tolerance

        self.heater_state = None

        self._initialised = False

    def update(self):
        if not self._initialised:
            self._init_nodes()
            self._initialised = True

        # self.plug.get_state()
        temp_value = float(self.temp.get_value())
        print('Temperature: {}, Target: {}'.format(temp_value, self.target_temp))
        print('Heater state: {}'.format(self.heater_state))
        with open('temperature.log', 'a') as f:
            f.write('date: {}, temp: {}, target: {}, heater: {}\n'.format(
                datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                temp_value, self.target_temp, self.heater_state))

        if temp_value < self.target_temp - self.tolerance:
            self.plug.set_socket('all', 'on')
            self.heater_state = 'on'
        elif temp_value > self.target_temp + self.tolerance:
            self.plug.set_socket('all', 'off')
            self.heater_state = 'off'

    def set_target(self, target):
        self.target_temp = float(target)

    def set_tolerance(self, tolerance):
        self.tolerance = float(tolerance)

    def get_target(self):
        return self.target_temp

    def get_tolerance(self):
        return self.tolerance

    def _init_nodes(self):
        self.temp.pull_methods()
        self.plug.pull_methods()
        time.sleep(1)

        self.plug.set_socket('all', 'off')
        self.heater_state = 'off'
