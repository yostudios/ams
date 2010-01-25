"""Unemployees look for work.

They're the mechanical drive behind the system.
"""

import logging
from ams.protocol import STATUS_DONE, STATUS_UNHANDLED, STATUS_FAILED
from ams.utils import endless_range

class BaseUnemployee(object):
    logger = logging.getLogger("ams.unemployee")

    def __init__(self, conf, next_task):
        self.conf = conf
        self.next_task = next_task

    def __str__(self):
        spa = ["<%s " % type(self).__name__]
        if hasattr(self, "task_names_handled"):
            handles_str = ", ".join(self.task_names_handled)
            spa.append("for " + handles_str + " ")
        spa.append("using %s>" % self.next_task)
        return "".join(spa)

    def run_once(self, timeout=None):
        """Execute a singel task.

        This won't do anything if the task cannot be handled, and returns False
        in such a case.

        The task is burried if the execution fails, so that it may be rerun
        later.
        """
        task = self.next_task(timeout=timeout)
        if not self.handles_task(task):
            self.logger.warn("%r unable handle %r", self, task)
            task.set_status(STATUS_UNHANDLED)
            return False
        try:
            self.execute_task(task)
        except:
            self.logger.exception("%r execute_task %r", self, task)
            task.set_status(STATUS_FAILED)
        else:
            self.logger.debug("%r done %r", self, task)
            task.set_status(STATUS_DONE)
            return True

    def run(self, times=None):
        """Execute tasks, stopping after *times* tasks have been run. This
        doesn't necessarily mean that *times* tasks have been executed.

        If *times* is None, runs indefinitely.
        """
        if times:
            counter = xrange(times)
        else:
            counter = endless_range()
        for count in counter:
            self.logger.debug("looking for a job (#%d)", count)
            self.run_once()

    # Unemployee subclass API
    def handles_task(self, task):
        """Check whether or not the unemployee handles the task.

        This could be for any number of reasons, but will mostly be because the
        instance doesn't know how to handle the task type specified.

        Subclasses must override this and provide logics for determining this
        themselves.
        """
        raise NotImplementedError()

    def execute_task(self, task):
        """Execute a given task.

        This task should have been run through handles_task first, to see if
        it's feasible for execution. That is to say, handles_task shouldn't be
        run here.

        Subclasses must override this and provide logics for dispatching tasks
        to the correct task handler.
        """
        return self.handler_for_task(task).run_task(task)

    def handler_for_task(self, task):
        """Get the handling function for *task*.

        Only used by *execute_task*, and as such may not be relevant.

        Subclasses must override this or *execute_task* to provide logics for
        getting the handler for the correct task.
        """
        raise NotImplementedError()

class SimpleUnemployee(BaseUnemployee):
    """Executes jobs of a single type."""

    def __init__(self, conf, next_task, handler):
        super(SimpleUnemployee, self).__init__(conf, next_task)
        self.handler = handler

    @property
    def task_names_handled(self):
        return self.handler.type_name

    def handles_task(self, task):
        return task.type_name == self.handler.type_name

    def handler_for_task(self, task):
        return self.handler(self.conf)

class FlexibleUnemployee(BaseUnemployee):
    """Executes jobs of multiple types."""

    def __init__(self, conf, next_task, handlers):
        super(FlexibleUnemployee, self).__init__(conf, next_task)
        self.handler_map = dict((h.type_name, h) for h in handlers)

    @property
    def task_names_handled(self):
        return self.handler_map.keys()

    def handles_task(self, task):
        return task.type_name in self.handler_map

    def handler_for_task(self, task):
        return self.handler_map[task.type_name](self.conf)
