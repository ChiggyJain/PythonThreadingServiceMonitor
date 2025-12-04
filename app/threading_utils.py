import threading
import logging


class StoppableThread(threading.Thread):
    """
    Industry-level Thread base class.
    Adds a stop() method using threading.Event.
    Ensures clean shutdown of loops inside the thread.
    """

    def __init__(self, name=None, daemon=False):
        ## calling the parent constructor [threading module]
        super().__init__(name=name, daemon=daemon)
        # thread-safe flag for signaling
        self._stop_event = threading.Event()

    def stop(self):
        """Signal the thread to stop."""
        self._stop_event.set()

    def stopped(self):
        """Check if stop was requested."""
        return self._stop_event.is_set()
