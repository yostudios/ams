"""Platsbanken provides interfaces to AMS for both giving and getting jobs."""

from ams.protocol import BaseTask
from ams.utils import parse_dsn, load_whole_package

class Platsbank(object):
    def next_task(self, timeout=None):
        """Fetch the next task from the queue server, blocking for max
        *timeout* seconds.
        """
        raise NotImplementedError()

    def accept_task_types(self, type_names=None):
        """Accept tasks of type name in *type_names*. If *type_names* is None,
        all types are fair game.
        """
        raise NotImplementedError()

    def queue_task(self, priority=None, delay=None):
        """Queue this task on the queue server, setting priority to *priority*,
        and delay insertion to after *delay* seconds.

        Note that the job should appear after *delay* seconds, not that this
        method should block for *delay* seconds before inserting.

        As above, if the queue server doesn't handle any or all of the
        features, a ValueError should be raised if that keyword argument is not
        None.

        This method is for subclasses to implement in the best possible way.
        """
        raise NotImplementedError()

    def queue(self, type_name, **args):
        """Queue a task of type *type_name* with arguments *args*.

        Really just calls self.queue_task with a task object constructed from
        the arguments given to this function.
        """
        return self.queue_task(BaseTask(type_name, args))

class DummyPlatsbank(Platsbank):
    dsn_name = "dummy"

    def next_task(self, timeout=None):
        raise RuntimeError("dummy platsbank can't get tasks")

    def queue_task(self, task, priority=None, delay=None):
        pass

    def accept_task_types(self, type_names=None):
        self.accept_type_names = type_names

    @classmethod
    def from_dsn(cls, dsn):
        return cls()

class RecordingDummyPlatsbank(DummyPlatsbank):
    dsn_name = "dummy+record"

    def __init__(self):
        self.queued = []

    def queue_task(self, task, priority=None, delay=None):
        # Funny way to copy the base task type.
        task = type(task)(task.type_name, task.args)
        task.priority = priority
        task.delay = delay
        self.queued.append(task)
        return task

_platsbanker_cache = []
def parse_platsbank_dsn(dsn, platsbanker=None, default=None):
    if platsbanker is None:
        platsbanker = get_all_platsbanker()
    platsbank_map = dict((pb.dsn_name, pb) for pb in platsbanker)
    platsbank_cls, opts = parse_dsn(dsn, platsbank_map, default)
    return platsbank_cls.from_dsn(opts)

def get_all_platsbanker():
    rv = _platsbanker_cache
    if not rv:
        load_whole_package("ams.platsbanken")
        # FIXME Don't use __subclasses__, only nests one level.
        def _walk_clses(cls):
            if hasattr(cls, "dsn_name") and hasattr(cls, "from_dsn"):
                rv.append(cls)
            for subcls in cls.__subclasses__():
                _walk_clses(subcls)
        _walk_clses(Platsbank)
    return rv
