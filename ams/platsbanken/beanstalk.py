"""Beanstalk source for platsbanken."""

from __future__ import absolute_import

import logging
from ams.platsbanken import Platsbank
from ams.protocol import (BaseTask, STATUSES, STATUS_DONE,
                          STATUS_UNHANDLED, STATUS_FAILED)

# Let this fail later on if the module doesn't exist
try:
    import beanstalkc
except ImportError:
    beanstalkc = None

logger = logging.getLogger("ams.unemployee.platsbanken.beanstalk")

class BeanstalkTask(BaseTask):
    """Beanstalkd-specific task subclass."""

    def __init__(self, job, type_name, args):
        """Annotates the instance with a *job* attribute."""
        super(BeanstalkTask, self).__init__(type_name, args)
        self.job = job

    def __hash__(self):
        return hash(self.job.jid)

    @classmethod
    def from_job(cls, job):
        """Create a task from the beanstalkc job instance *job*."""
        type_name, args = cls.decode(job.body)
        return cls(job, type_name, args)

    def set_status(self, status):
        """Set job status of this task to *status*.
        
        STATUS_DONE means the job is deleted from the queue,
        STATUS_UNHANDLED means the job is simply released back into the queue,
        STATUS_FAILED means the job is burried.
        """
        if status not in STATUSES:
            raise ValueError("status %r unknown (should be one of %r)" %
                             (status, STATUSES))
        if status == STATUS_DONE:
            self.job.delete()
        # TODO Better workaround than giving a false priority in release and
        #      bury.
        # If you don't pass a priority to bury and release, beanstalkc will try
        # to look up the job's priority (why doesn't beanstalkd do this by
        # itself?) through decoding the YAML stats of the job.
        # Not a great idea, and top that off with the fact that we don't load
        # YAML.
        # What needs to be done is that beanstalkd has a sensible default
        # priority for burried and released jobs (i.e., the job's current
        # priority.)
        elif status == STATUS_UNHANDLED:
            self.job.release(priority=beanstalkc.DEFAULT_PRIORITY)
        elif status == STATUS_FAILED:
            self.job.bury(priority=beanstalkc.DEFAULT_PRIORITY)

class BeanstalkPlatsbank(Platsbank):
    """Platsbanken for beanstalkd."""

    dsn_name = "beanstalk"
    task_cls = BeanstalkTask

    def __init__(self, client):
        self.client = client

    def __str__(self):
        return "<%s with %s>" % (type(self).__name__, self.client)

    def next_task(self, timeout=None):
        """Get next task from beanstalkd."""
        job = self.client.reserve(timeout=timeout)
        if job:
            return self.task_cls.from_job(job)

    def queue_task(self, task, priority=None, delay=None):
        """Queue task *task* in beanstalkd and return updated task object."""
        if priority is None: priority = beanstalkc.DEFAULT_PRIORITY
        if delay is None: delay = 0
        body = task.encode()
        self.client.use(task.type_name)
        jid = self.client.put(body, priority=priority, delay=delay)
        job = beanstalkc.Job(self.client, jid, body, reserved=False)
        return self.task_cls.from_job(job)

    def accept_task_types(self, type_names=None):
        if type_names is None:
            return
        for type_name in type_names:
            self.client.watch(type_name)

    @classmethod
    def from_dsn(cls, dsn):
        """Create a platsbank connected to the beanstalkd at *dsn*."""
        if not dsn.path:
            host, port = beanstalkc.DEFAULT_HOST, beanstalkc.DEFAULT_PORT
        elif ":" in dsn.path:
            host, port = dsn.path.split(":")
            port = int(port)
        else:
            host, port = dsn.path, beanstalkc.DEFAULT_PORT
        logger.info("%s connecting to (%r, %r)", cls, host, port)
        conn = beanstalkc.Connection(host=host, port=port)
        return cls(conn)
