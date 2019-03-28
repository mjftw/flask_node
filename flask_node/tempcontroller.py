import time
from datetime import datetime

from .remoteobj import RxClass

class TempController():
    def __init__(self, target_temp, tolerance,
            sensor_host, sensor_port, hot_host, hot_port, cold_host, cold_port):
        self.sensor = RxClass(host=sensor_host, port=sensor_port)
        self.hot = RxClass(host=hot_host, port=hot_port)
        self.cold = RxClass(host=cold_host, port=cold_port)

        self.target_temp = target_temp
        self.tolerance = tolerance

        self._initialised = False

    def update(self):
        if not self._initialised:
            self._init_nodes()
            self._initialised = True

        # self.hot.get_state()
        temp_value = float(self.sensor.get_value())
        print('Temperature: {}, Target: {}'.format(temp_value, self.target_temp))
        print('Heater state: {}'.format(self.heater_state))
        with open('temperature.log', 'a') as f:
            f.write('date: {}, sensor: {}, target: {}, heater: {}\n'.format(
                datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                temp_value, self.target_temp, self.heater_state))

        if temp_value < self.target_temp - self.tolerance:
            self.hot.on()
            self.cold.off()
        elif temp_value > self.target_temp + self.tolerance:
            self.hot.off()
            self.cold_on()
        else:
            self.hot.off()
            self.cold.off()

    def set_target(self, target):
        self.target_temp = float(target)

    def set_tolerance(self, tolerance):
        self.tolerance = float(tolerance)

    def _init_nodes(self):
        self.sensor.pull_methods()
        self.hot.pull_methods()
        time.sleep(1)

        self.hot.set_socket('all', 'off')
        self.heater_state = 'off'
