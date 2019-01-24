from flask import Flask, request, jsonify
import inspect
import requests
from requests.exceptions import ConnectionError
from copy import copy
from threading import Thread, Event
import time

class TxClass():
    def __init__(self, name=None, host=None, port=None, debug=None):
        self.name = name or '{}_api'.format(self.__class__.__name__)
        self.app = Flask(name)
        self.host = host or 'localhost'
        self.port = port or '5000'
        self.debug = debug or False

        self.start_time = None
        if not hasattr(self, 'methods'):
            self.methods = ['GET']

        def get_method_call(m):
            return {m: inspect.getargspec(getattr(self, m)).args[1:]}

        def get_methods():
            method_names = [m[0] for m in inspect.getmembers(self, predicate=inspect.ismethod)]
            method_names = filter(lambda m: not (m.startswith('_') or m == 'run_api'), method_names)
            methods = {}
            for m in method_names:
                methods = ({**methods, **get_method_call(m)})
            return methods

        def get_api_info():
            api_info = {
                'name': self.name,
                'methods': get_methods(),
            }

            return jsonify(api_info)


        self.app.add_url_rule(
            '/',
            '/',
            view_func=get_api_info,
            methods=['GET'])

        @self.app.route('/<m>', methods=['GET'])
        def api_discover(m):
            func = getattr(self, m, None)
            if not func:
                return '', 404

            al = inspect.getargspec(func).args[1:] or []
            return jsonify(get_method_call(m))

        @self.app.route('/<m>', methods=['POST'])
        def api_call(m):
            func = getattr(self, m, None)
            if not func:
                return '', 404

            al = inspect.getargspec(func).args[1:] or []
            dl = inspect.getargspec(func).defaults or []
            args_defs = [l for l in al[:len(al)-len(dl)]] + list(zip(al[::-1], dl[::-1]))[::-1]

            args = []
            for a in args_defs:
                if isinstance(a, tuple):
                    args.append(request.args.get(a[0], default=a[1]))
                else:
                    args.append(request.args.get(a))

            return str(func(*args))

    def run_api(self):
        self.app.run(host=self.host, port=self.port, debug=self.debug)


class TxClassLooping(TxClass):
    def __init__(self, loop_method_name, loop_sleep=1, pause_sleep=None,
            name=None, host=None, port=None, debug=None):
        if not hasattr(self, loop_method_name):
            raise TypeError('Class is does not have loop method {}'.format(
                loop_method))
        self._loop_method_name = loop_method_name

        self._loop_sleep = loop_sleep
        self._pause_sleep = pause_sleep
        self._stop_event = Event()
        self._pause_event = Event()

        self._loop_thread = None

        super().__init__(name, host, port, debug)

    def run_api(self):
        self.start()
        super().run_api()

    def pause(self):
        self._pause_event.set()

    def resume(self):
        self._pause_event.clear()

    def stop(self):
        print("STOP")
        if self._loop_thread and self._loop_thread.isAlive():
            self._stop_event.set()
            self._loop_thread.join()
            self._loop_thread = None
            print("STOPPED")

    def start(self):
        print("START")
        if not self._loop_thread or not self._loop_thread.isAlive():
            self._loop_thread = self._thread_factory()
            self._loop_thread.start()
            print("STARTED")

    def get_running_state(self):
        if self._stop_event.is_set():
            return 'stopped'
        elif self._pause_event.is_set():
            return 'paused'
        else:
            return 'running'

    def _thread_factory(self):
        return TxClassLoopThread(
            txclass=self,
            loop_method_name=self._loop_method_name,
            stop_event=self._stop_event,
            pause_event=self._pause_event,
            loop_sleep=self._loop_sleep,
            pause_sleep=self._pause_sleep
        )

class TxClassLoopThread(Thread):
    def __init__(self, txclass, loop_method_name, stop_event, pause_event,
            loop_sleep=None, pause_sleep=None):
        self.txclass = txclass
        self.loop_method_name = loop_method_name
        self.stop_event = stop_event
        self.pause_event = pause_event
        self.loop_sleep = loop_sleep
        self.pause_sleep = pause_sleep or 0.1

        Thread.__init__(self)

    def run(self):
        loop_method = getattr(self.txclass, self.loop_method_name)
        while not self.stop_event.is_set():
            if self.pause_event.is_set():
                time.sleep(self.pause_sleep)
            else:
                loop_method()
                time.sleep(self.loop_sleep or 0)


class RxClass():
    def __init__(self, host='localhost', port='5000'):
        self.host = host
        self.port = port
        self.remote_name = None

    @property
    def url(self):
        return 'http://{}{}'.format(
            self.host, ':{}'.format(self.port) if self.port else '')

    def pull_methods(self, timeout=0.5, max_tries=20):
        r = None
        for i in range(0, max_tries):
            try:
                r = requests.get(self.url, timeout=timeout)
                break
            except ConnectionError as e:
                if i >= max_tries-1:
                    raise e
                else:
                    time.sleep(0.1)

        api_info = r.json()
        methods = api_info['methods']
        self.remote_name = api_info['name']

        for name, arg_names in methods.items():
            setattr(self, name, self._method_factory(name, arg_names))

    def _method_factory(self, name, arg_names):
        def f(*args):
                params = dict(zip(arg_names, args))
                method_url = '{}/{}'.format(self.url, name)
                r = requests.post(method_url, params=params)
                return r.text

        f.__name__ = name
        return f
