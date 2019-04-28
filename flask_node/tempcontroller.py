import time
from datetime import datetime
import os

from .remoteobj import RxClass
from .logging import Logging

class TempController(Logging):
    def __init__(self, setpoint, tolerance,
            sensor_host, sensor_port, hot_host, hot_port, cold_host, cold_port):
        self.sensor = RxClass(host=sensor_host, port=sensor_port)
        self.hot = RxClass(host=hot_host, port=hot_port)
        self.cold = RxClass(host=cold_host, port=cold_port)

        self.setpoint = setpoint
        self.tolerance = tolerance

        self._initialised = False

        self.logfile = './TempController.log'
        if not os.path.exists(self.logfile):
            with open(self.logfile, 'w') as f:
                f.write('Time,Temperature,Setpoint,Tolerance,State,StateNext\n')

    def update(self):
        if not self._initialised:
            self._init_nodes()

        now = int(time.time())
        temperature = self.sensor.get_value()
        state = self.get_state()
        state_next = state

        self.log('State = {}'.format(state))
        self.log('Temperature = {}'.format(temperature))
        self.log('Setpoint = {}'.format(self.setpoint))
        self.log('Tolerance = {}'.format(self.tolerance))

        if state == 'Cooling':
            if temperature <= self.setpoint:
                self.log('Cold enough, State->Idle')
                state_next = 'Idle'

                self.set_idle_state()
        elif state == 'Idle':
            if temperature >= self.setpoint + self.tolerance:
                self.log('Too hot, State->Cooling')
                state_next = 'Cooling'

                self.set_cooling_state()
            elif temperature <= self.setpoint - self.tolerance:
                self.log('Too cold, State->Heating')
                state_next = 'Heating'

                self.set_heating_state()
        elif state == 'Heating':
            if temperature >= self.setpoint:
                self.log('Hot enough, State->Idle')
                state_next = 'Idle'

                self.set_idle_state()
        else:
            self.log('In Error state! State->Idle')
            state_next = 'Idle'

            self.set_idle_state()

        self.log(','.join(
            [str(now), str(temperature), str(self.setpoint), str(self.tolerance),
                state, state_next]),
            file=self.logfile)

    def set_cooling_state(self):
        self.cold.on()
        self.hot.off()

    def set_idle_state(self):
        self.hot.off()
        self.cold.off()

    def set_heating_state(self):
        self.cold.off()
        self.hot.on()

    def get_state_enum(self)
        state = self.get_state()

        if(state == 'Heating'):
            return 2
        if(state == 'Cooling'):
            return 1
        if(state == 'Idle'):
            return 0

        # Error state
        return -1


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
