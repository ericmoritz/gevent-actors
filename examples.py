from gevent.monkey import patch_all
patch_all(sys=True)

from kombu import Connection
from actor import GenServer, shell, send_after


class TimeoutActor(GenServer):
    def __init__(self, *args, **kwargs):
        super(TimeoutActor, self).__init__(*args, **kwargs)
        send_after(self, 1, "timeout")


    def handle_message(self, message):
        if message.payload == "timeout":
            print "got timeout, rescheduling"
            send_after(self, 1, "timeout")
        else:
            print "unhandled message: {!r}".format(message.payload)


if __name__ == '__main__':
    with Connection(transport="memory") as conn:
        pid = TimeoutActor(conn, "timeout-actor")
        pid.start()
        shell(globals(), locals(), pid)
