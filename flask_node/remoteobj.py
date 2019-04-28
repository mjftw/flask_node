from flask import Flask, request, jsonify
import inspect
import requests
from requests.exceptions import ConnectionError
from copy import copy
from threading import Thread, Event
import time
from ast import literal_eval
import atexit

class TxClass():
    def __init__(self, name=None, host=None, port=None):
        self.name = name or '{}_api'.format(self.__class__.__name__)
        self.app = Flask(name)
        self.host = host or 'localhost'
        self.port = port or '5000'

        if not hasattr(self, 'methods'):
            self.methods = ['GET']

        def get_method_call(m):
            return {m: inspect.getargspec(getattr(self, m)).args[1:]}

        def get_methods():
            method_names = [m[0] for m in inspect.getmembers(self,
                predicate=inspect.ismethod)]
            method_names = filter(lambda m: not (m.startswith('_') or m == 'run_api'),
                method_names)
            methods = {}
            for m in method_names:
                methods = ({**methods, **get_method_call(m)})
            return methods

        def get_variables():
            variable_names = [m[0] for m in inspect.getmembers(
                self, predicate=lambda x: not inspect.ismethod(x))]
            variable_names = filter(lambda m: not (m.startswith('_')),
                variable_names)

            variables = {}
            for v in variable_names:
                variables = ({v: str(getattr(self, v)) for v in variable_names})
            return variables


        def get_api_info():
            api_info = {
                'name': self.name,
                'methods': get_methods(),
                'variables': get_variables()
            }

            return jsonify(api_info)


        self.app.add_url_rule(
            '/',
            '/',
            view_func=get_api_info,
            methods=['GET'])

        @self.app.route('/<m>', methods=['GET'])
        def api_discover(m):
            attr = getattr(self, m, None)
            if not attr:
                return '', 404

            if not callable(attr):
                return str(attr)

            al = inspect.getargspec(attr).args[1:] or []
            return jsonify(get_method_call(m))

        @self.app.route('/<m>', methods=['POST'])
        def api_call(m):
            func = getattr(self, m, None)
            if not func:
                return 'Method not found', 404

            if not callable(func):
                return 'Forbidden: Cannot directly set variables', 403

            al = inspect.getargspec(func).args[1:] or []
            dl = inspect.getargspec(func).defaults or []
            args_defs = [l for l in al[:len(al)-len(dl)]] + list(zip(al[::-1], dl[::-1]))[::-1]

            args = []
            for a in args_defs:
                if isinstance(a, tuple):
                    args.append(request.args.get(a[0], default=a[1]))
                else:
                    args.append(request.args.get(a))

            # Check if arg shoulf be float, int etc, and convert
            args_typed = []
            for a in args:
                try:
                    a_typed = literal_eval(a)
                # arg not is just a string
                except ValueError:
                    a_typed = a

                args_typed.append(a_typed)

            return str(func(*args_typed))

    def run_api(self):
        self.app.run(host=self.host, port=self.port, threaded=True)


class TxClassLooping(TxClass):
    def __init__(self, loop_method_name, loop_sleep=1, pause_sleep=None,
            name=None, host=None, port=None):
        if not hasattr(self, loop_method_name):
            raise TypeError('Class is does not have loop method {}'.format(
                loop_method))
        self._loop_method_name = loop_method_name

        self._loop_sleep = loop_sleep
        self._pause_sleep = pause_sleep
        self._pause_event = Event()
        self._stop_event = Event()

        self._loop_thread = None

        super().__init__(name, host, port)

    def run_api(self):
        self._loop_thread = self._thread_factory()

        self._pause_event.clear()
        self._stop_event.clear()

        self._loop_thread.start()
        atexit.register(self.stop)

        super().run_api()

    def pause(self):
        self._pause_event.set()

    def resume(self):
        self._pause_event.clear()

    def stop(self):
        self._stop_event.set()

    @property
    def running_state(self):
        if not self._loop_thread or not self._loop_thread.isAlive():
            return 'dead'

        if self._pause_event.is_set():
            return 'paused'
        else:
            return 'running'

    @property
    def loop_sleep(self):
        if self._loop_thread:
            return self._loop_thread.loop_sleep
        else:
            return self._loop_sleep

    def set_loop_sleep(self, loop_sleep):
        self._loop_sleep = loop_sleep
        if self._loop_thread:
            self._loop_thread.loop_sleep = loop_sleep


    def _thread_factory(self):
        return TxClassLoopThread(
            txclass=self,
            loop_method_name=self._loop_method_name,
            pause_event=self._pause_event,
            stop_event=self._stop_event,
            loop_sleep=self._loop_sleep,
            pause_sleep=self._pause_sleep
        )

class TxClassLoopThread(Thread):
    def __init__(self, txclass, loop_method_name, pause_event, stop_event,
            loop_sleep=None, pause_sleep=None):
        self.txclass = txclass
        self.loop_method_name = loop_method_name
        self.pause_event = pause_event
        self.stop_event = stop_event
        self.loop_sleep = loop_sleep
        self.pause_sleep = pause_sleep or 0.1

        Thread.__init__(self)

    def run(self):
        loop_method = getattr(self.txclass, self.loop_method_name)

        while not self.stop_event.is_set():
            if not self.stop_event.is_set():
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

    def __repr__(self):
        return 'RxClass [{}] [{}]'.format(
            self.remote_name or 'uninitialised', self.url)

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
                try:
                    return literal_eval(r.text)
                except ValueError:
                    return r.text

        f.__name__ = name
        return f


class RxReadSimple():
    def __init__(self, remote_host, remote_port, remote_method,
            remote_args=None, callback=None):
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.remote_method = remote_method
        self.remote_args = remote_args or ()
        self.callback = callback or print
        self.remote = RxClass(host=remote_host, port=remote_port)

        self._initialised = False

    def read(self):
        if not self._initialised:
            self.remote.pull_methods()
            self._initialised = True

        method = getattr(self.remote, self.remote_method, None)

        if not method:
            raise RuntimeError('Remote object {}:{} does not have method {}'.format(
                self.remote_host, self.remote_port, self.remote_method))

        value = method(*self.remote_args)

        self.callback(value)