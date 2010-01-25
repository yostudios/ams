AMS - queue-based dispatching
=============================

AMS is a fairly simple layer on top of any sort of queue daemon. AMS takes care
of serializing and deserializing jobs from a queue, and also wraps some other
parts of the queue system (such as running the actual jobs so that they may be
marked as done, or as failed.)

AMS can in theory be used with any queue daemon, however, for the time being
only `beanstalkd` is supported.

.. toctree::
   :maxdepth: 2

   protocol
   platsbanken
   unemployees/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

