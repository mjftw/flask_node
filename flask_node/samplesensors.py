import time
import json

from .remoteobj import RxClass

class SampleSensors():
    def __init__(self, watches, save_func):
        '''
        Pulls data from flask sensor nodes and logs it to a database.
        @watches is a dicting listing the address and
        variables of the sensor nodes to read and logged
        Expected format:
        {
            [{
                "host": xx.xx.xx.xx,
                "port": xxxx,
                "methods": {
                    "name_of_read_method1": "name_to_log_for_quantity1",
                    "name_of_read_method2": "name_to_log_for_quantity2",
                    ...
                }
            },
            {
                "name": "unique_name"
                "host": xx.xx.xx.xx,
                "port": xxxx,
                "methods": {
                    "name_of_read_method1": "name_to_log_for_quantity1",
                    "name_of_read_method2": "name_to_log_for_quantity2",
                    ...
                }
            }]
        }
        '''
        self.watches = json.loads(watches)
        self.save_func = save_func

        self._initialised = False

        for node in self.watches:
            if ('host' not in node or
                'port' not in node or
                'methods' not in node):
                raise TypeError('Invalid watches: {}'.format(self.watches))

            node['rxclass'] = RxClass(
                host=node['host'],
                port=node['port']
            )

    def read_data(self):
        if not self._initialised:
            self._init_nodes()

        timestamp = time.time()
        data = {}
        for node in self.watches:
            if 'name' not in node:
                node['name'] = node['rxclass'].remote_name

            data[node['name']] = {}
            for method_name, save_name in node['methods'].items():
                method = getattr(node['rxclass'], method_name, None)
                if method:
                    data[node['name']][save_name] = method()
                else:
                    raise RuntimeWarning('{} has no method [{}]'.format(
                        data[node['name']], method_name))

        return (timestamp, data)

    def save_data(self):
        data = self.read_data()
        self.save_func(data)

    def simplify_dataset(self):
        '''
        Smooths dataset to remove duplicate methods in order to minimise
        the data stored for a given value, reducing transfer times etc.
        '''
        raise NotImplementedError()

    def _init_nodes(self):
        for node in self.watches:
            node['rxclass'].pull_methods()
        time.sleep(1)
        self._initialised = True