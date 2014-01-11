import gevent
from gevent import Greenlet
from gevent.event import Event
from gevent import fileobject
from logging import getLogger
import sys
import time
import code

import readline

log = getLogger(__name__)

class Timeout(Exception):
    pass

def shell(global_vars, local_vars, sup):
    sh = _shell_fun()
    try:
        sh(global_vars, local_vars)
    finally:
        sup.stop()


def _shell_fun():
    try:
        from IPython.Shell import IPShellEmbed
        return IPShellEmbed
    except ImportError:
        import readline # optional, will allow Up/Down/History in the console
        import code
        def sh(global_vars, local_vars):
            vars = global_vars.copy()
            vars.update(local_vars)
            shell = code.InteractiveConsole(vars)
            shell.interact()

        return sh


def mainloop(sup):
    try:
        gevent.wait()
    except KeyboardInterrupt:
        pass
    finally:
        sup.stop()


def send_after(pid, seconds, msg):
    gevent.spawn_later(
        seconds,
        pid.send,
        msg
    ).start()


class StopGreenlet(Greenlet):
    def __init__(self, *args, **kwargs):
        self._stop_event = Event()
        super(StopGreenlet, self).__init__()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class Actor(StopGreenlet):
    Timeout = Timeout

    def __init__(self, connection, name, *args, **kwargs):
        super(Actor, self).__init__(name=name, *args, **kwargs)
        self.connection = connection
        self._mbox = connection.SimpleQueue(name)

    def send(self, payload):
        self._mbox.put(payload, content_type="application/octet-stream")

    def receive(self, timeout=None):
        try:
            return self._mbox.get(block=True, timeout=timeout)
        except self._mbox.Empty:
            raise Timeout()


class Supervisor(StopGreenlet):
    """
    Calling stop() an this thread will stop all of the threads
    """
    def __init__(self, workers, *args, **kwargs):
        super(Supervisor, self).__init__(*args, **kwargs)
        self._workers = workers

    def stop(self):
        for worker in self._workers:
            worker.stop()
        super(Supervisor, self).stop()

    def _run(self):
        for worker in self._workers:
            worker.start()
        # wait until we're told to stop
        self._stop_event.wait()

            
class GenServer(Actor):
    def handle_message(self, message):
        return

    def _run(self):
        while True:
            try:
                self.handle_message(self.receive(timeout=1))
            except self.Timeout:
                pass

            if self.stopped():
                return
            
