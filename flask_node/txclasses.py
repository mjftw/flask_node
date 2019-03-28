from .remoteobj import TxClass, TxClassLooping
from .tempsensor import TempSensor
from energenie import SmartPlug
from .tempcontroller import TempController

class TempSensorTx(TempSensor, TxClass):
    def __init__(self, name=None, host=None, port=None, debug=None):
        TempSensor.__init__(self)
        TxClass.__init__(self, name, host, port, debug)

class SmartPlugTx(SmartPlug, TxClass):
    def __init__(self, socket, name=None, host=None, port=None, debug=None):
        SmartPlug.__init__(self, socket)
        TxClass.__init__(self, name, host, port, debug)

class TempControllerTx(TempController, TxClassLooping):
    def __init__(self, temp_host, temp_port, plug_host, plug_port,
            target_temp, tolerance,
            loop_sleep=None, pause_sleep=None,
            name=None, host=None, port=None, debug=None):
        TempController.__init__(self, temp_host, temp_port,
            plug_host, plug_port, target_temp, tolerance)
        TxClassLooping.__init__(self, 'update', loop_sleep, pause_sleep,
            name, host, port, debug)