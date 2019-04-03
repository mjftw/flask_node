import time
from datetime import datetime

from .remoteobj import RxClass

class TempController():
    def __init__(self, setpoint, tolerance,
            sensor_host, sensor_port, hot_host, hot_port, cold_host, cold_port):
        self.sensor = RxClass(host=sensor_host, port=sensor_port)
        self.hot = RxClass(host=hot_host, port=hot_port)
        self.cold = RxClass(host=cold_host, port=cold_port)

        self.setpoint = setpoint
        self.tolerance = tolerance

        self._initialised = False

    def update(self):
        if not self._initialised:
            self._init_nodes()

        temperature = self.sensor.get_value()
        state = self.get_state()

        if state == 'Cooling':
            if temperature <= self.setpoint:
                # Cold enough, State->Idle
                self.cold.off()
                self.hot.off()
        elif state == 'Idle':
            if temperature >= self.tolerance:
                # Too hot, State->Cooling
                self.cold.on()
                self.hot.off()
            elif temperature <= self.tolerance:
                # Too cold, State->Heating
                self.cold.off()
                self.hot.on()
        elif state == 'Heating':
            if temperature >= self.setpoint:
                # Hot enough, State->Idle
                self.cold.off()
                self.hot.off()
        else:
            # This should not happen, but reset to Idle if it does
            self.hot.off()
            self.cold.off()

    def get_state(self):
        if not self._initialised:
            self._init_nodes()

        heating = self.hot.is_on()
        cooling = self.cold.is_on()

        if heating and not cooling:
            return 'Heating'
        elif cooling and not heating:
            return 'Cooling'
        elif heating and cooling:
            return 'ERROR: Heating & Cooling'
        else:
            return 'Idle'

    def get_temperature(self):
        if not self._initialised:
            self._init_nodes()

        return self.sensor.get_value()

    def set_setpoint(self, setpoint):
        self.setpoint = float(setpoint)

    def set_tolerance(self, tolerance):
        self.tolerance = float(tolerance)

    def _init_nodes(self):
        self.sensor.pull_methods()
        self.hot.pull_methods()
        self.cold.pull_methods()

        time.sleep(1)

        self._initialised = True
