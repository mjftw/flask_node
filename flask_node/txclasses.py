from .remoteobj import TxClass, TxClassLooping
from .tempsensor import TempSensor
from .smartplug import SmartPlug
from .tempcontroller import TempController

class TempSensorTx(TempSensor, TxClass):
    def __init__(self, name=None, host=None, port=None, debug=None):
        TempSensor.__init__(self)
        TxClass.__init__(self, name, host, port, debug)

class SmartPlugTx(SmartPlug, TxClass):
    def __init__(self, *args, name=None, host=None, port=None, debug=None, **kwargs):
        SmartPlug.__init__(self, *args, **kwargs)
        TxClass.__init__(self, name, host, port, debug)

class TempControllerTx(TempController, TxClassLooping):
    def __init__(self, *args, loop_sleep=None, pause_sleep=None,
            name=None, host=None, port=None, debug=None, **kwargs):
        TempController.__init__(self, *args, **kwargs)
        TxClassLooping.__init__(self, 'update', loop_sleep, pause_sleep,
            name, host, port, debug)