import time

from .remoteobj import RxClass

class SnapshotSensors():
    def __init__(self, database, watches=None):
        '''
        Pulls data from flask sensor nodes and logs it to a database.
        @watches is a dicting listing the address and
        variables of the sensor nodes to read and logged
        Expected format:
        {
            'name_of_sensor_1': {
                'host': xx.xx.xx.xx,
                'port': xxxx,
                'values': {
                    'name_of_read_method1': 'name_to_log_for_quantity1',
                    'name_of_read_method2': 'name_to_log_for_quantity2',
                    ...
                }
            'name_of_sensor_2': {
                'host': xx.xx.xx.xx,
                'port': xxxx,
                'values': {
                    'name_of_read_method1': 'name_to_log_for_quantity1',
                    'name_of_read_method2': 'name_to_log_for_quantity2',
                    ...
                }
            ...
            }
        }
        '''
        self.database = database
        self.watches = watches

        self._initialised = False

        for node in watches:
            if ('host' not in watches[node] or
                'port' not in watches[node] or
                'values' not in watches[node]):
                raise TypeError('Invalid watches: {}'.format(watches))

            watches[node]['rxclass'] = RxClass(
                host=watches[node]['host'],
                port=watches[node]['port'])

    def record_data(self):
       if not self._initialised:
            self._init_nodes()
            self._initialised = True

        for node in watches:
            for val in watches[node]['values']:
                read_method = getattr(watches[node]['rxclass'], val, None)
                if read_method:
                    data = {watches[node]['rxclass'][val]: read_method()}
                    print(data)

    def simplify_dataset(self):
        '''
        Smooths dataset to remove duplicate values in order to minimise
        the data stored for a given value, reducing transfer times etc.
        '''
        raise NotImplementedError()

    def _init_nodes(self):
        for node in self.watches:
            self.watches[node]['rxclass'].pull_methods()
        time.sleep(1)