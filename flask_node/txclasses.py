from .remoteobj import TxClass, TxClassLooping
from .tempsensor import TempSensor
from .smartplug import SmartPlug
from .tempcontroller import TempController
from .samplesensors import SampleSensors

class TempSensorTx(TempSensor, TxClass):
    def __init__(self, *args, name=None, host=None, port=None, **kwargs):
        TempSensor.__init__(self, *args, **kwargs)
        TxClass.__init__(self, name, host, port)

class SmartPlugTx(SmartPlug, TxClass):
    def __init__(self, *args, name=None, host=None, port=None, **kwargs):
        SmartPlug.__init__(self, *args, **kwargs)
        TxClass.__init__(self, name, host, port)

class TempControllerTx(TempController, TxClassLooping):
    def __init__(self, *args, loop_sleep=None, pause_sleep=None,
            name=None, host=None, port=None, **kwargs):
        TempController.__init__(self, *args, **kwargs)
        TxClassLooping.__init__(self, 'update', loop_sleep, pause_sleep,
            name, host, port)

class DataLoggerTx(SampleSensors, TxClassLooping):
    def __init__(self, *args, loop_sleep=None, pause_sleep=None,
            name=None, host=None, port=None, **kwargs):
        SampleSensors.__init__(self, *args, **kwargs)
        TxClassLooping.__init__(self, 'save_data', loop_sleep, pause_sleep,
            name, host, port)