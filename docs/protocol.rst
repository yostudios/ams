.. _protocol:

The AMS protocol
================

It's quite simple really. AMS uses `Python pickling`__ to serialize primitive
datatypes, and each job consists of a dict (or *object* as they call it in
JavaScript), with a single special key, ``type``, and the rest are arguments:

__ http://docs.python.org/library/pickle.html

.. code-block:: python

    {'arg1': 'value1',
     'arg2': 'value2',
     'type': 'job-type'}

.. note:: It is somewhat customary to use the ``name-with-dashes``
          convention in job names.

These job types essentially define which handler to use for a job, and can be
thought of as function names.

:mod:`ams.protocol`
-------------------

AMS works with *tasks* rather than *jobs* because it was necessary to
distinguish between the two for the sake of personal sanity. So, think of an
AMS task as a representation of a queue job.

.. class:: BaseTask(type_name, args)

   Base class for all tasks, providing serialization support and a well-defined
   interface.

   .. staticmethod:: decode(data) -> type_name, args
      
      Deserialize job *data* into *type_name* and *args*, for use with the
      class initializer.

   .. method:: encode() -> data

      Serialize task described by this instance into job *data*, for use with
      :meth:`BaseTask.decode`.

   .. method:: set_status(status)

      Set the status of the task described by this instance to *status*.

      *status* must be one of the values in :attr:`STATUSES`.

      This is a stub method raising :exc:`NotImplementedError`.

.. data:: STATUS_DONE

   Job status for jobs that are done.

.. data:: STATUS_UNHANDLED

   Job status for jobs that couldn't be handled by the worker that took them.

   Jobs of this status are reinserted into the queue server.

.. data:: STATUS_FAILED

   Job status for jobs that failed somehow, raising an exception.

   Jobs of this status are inserted into the queue server's available mechanism
   for failed jobs.

.. data:: STATUSES

   List of statuses which a job may be in. This is just for convenience, and
   maps to the statuses defined above.

Mapping onto `beanstalkd`
-------------------------

`beanstalkd` has an opaque *job data* field in which the serialized job
description is put. `beanstalkd` also provides a mechanism called *tubes*, and
AMS sends jobs of a certain type to a tube with the same name. This means a
worker must listen to each tube it knows how to execute jobs for.

The latter part is handled by AMS transparently, as each worker is required to
know which jobs it can handle on beforehand.
