import time
from datetime import datetime

from .remoteobj import RxClass

class TempController():
    def __init__(self, target, tolerance,
            sensor_host, sensor_port, hot_host, hot_port, cold_host, cold_port):
        self.sensor = RxClass(host=sensor_host, port=sensor_port)
        self.hot = RxClass(host=hot_host, port=hot_port)
        self.cold = RxClass(host=cold_host, port=cold_port)

        self.target = target
        self.tolerance = tolerance

        self._initialised = False

    def update(self):
        if not self._initialised:
            self._init_nodes()

        # self.hot.get_state()
        temp_value = float(self.sensor.get_value())
        print('Temperature: {}, Target: {}'.format(temp_value, self.target))
        print('Hot on?: {}'.format(self.hot.is_on()))
        print('Cold on?: {}'.format(self.cold.is_on()))

        if temp_value < self.target - self.tolerance:
            self.hot.on()
            self.cold.off()
        elif temp_value > self.target + self.tolerance:
            self.hot.off()
            self.cold_on()
        else:
            self.hot.off()
            self.cold.off()

    def set_target(self, target):
        self.target = float(target)

    def set_tolerance(self, tolerance):
        self.tolerance = float(tolerance)

    def _init_nodes(self):
        self.sensor.pull_methods()
        self.hot.pull_methods()
        self.cold.pull_methods()

        time.sleep(1)

        self._initialised = True
