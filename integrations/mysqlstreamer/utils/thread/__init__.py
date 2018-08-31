
from threading import Thread


class CoordinatedThread(Thread):

    def __init__(self, coordinator, *args, **kwargs):
        super(CoordinatedThread, self).__init__(*args, **kwargs)
        self._coordinator = coordinator

    def stop(self):
        self._coordinator.stop()

    def should_stop(self):
        return self._coordinator.should_stop()
