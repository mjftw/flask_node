import os
import time


class SensorError(Exception):
    pass


class TempSensor():
    w1_bus_path = '/sys/bus/w1/devices'
    # Known Sensors:
    #   28-02029245757f
    def __init__(self, serialno=None):
        self.serialno = serialno or '28-02029245757f'
        self.read_path = os.path.join(self.w1_bus_path, self.serialno, 'w1_slave')

    def get_value(self):
        attempts = 0
        data = self.raw_data()
        while 'YES' not in data[0] and attempts < 10:
            time.sleep(0.1)
            attempts += 1
            data = self.raw_data()

        if 'YES' not in data[0]:
            raise SensorError('CRC error reading sensor')

        idx = data[1].find('t=') + 2
        if idx == -1:
            raise SensorError('Error reading sensor')

        return (float)(data[1][idx:].strip())/1000

    def raw_data(self):
        with open(self.read_path, 'r') as f:
            return f.readlines()
