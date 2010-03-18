.. currentmodule:: ams.platsbanken

:mod:`ams.platsbanken`: Delegating jobs to those in need
========================================================

When you've got a job you need a guy for, it'd be absurd for you to actually go
find somebody yourself. We've got all sorts of bureaucracy to through first!
And of course, this is where Platsbanken comes in handy.

On a more serious note, platsbanken makes it easy for job applicants
(`unemployees`) to get jobs, and for job providers to provide jobs.

Think of it in terms of this fine chart::

    [ Producer ] --> [ Platsbanken ] <--> [ Unemployee ]

In reality it's actually a little more like this::

    [ Producer ] --> [ Platsbanken ]  --> [ Queue ]
    [ Queue ]  <-->  [ Platsbanken ] <--> [ Unemployee ]

In other words, platsbanken is an interface to the queue service of choice.

.. seealso:: :ref:`unemployees`

Responsibilities
----------------

First and perhaps foremost Platsbanken is an interface for job providers to
announce new jobs to be consumed by one of many consumers.

Anouncing new jobs is done via :meth:`Platsbank.queue_task`, and its helper
version :meth:`Platsbank.queue`.

Reference
---------

.. autoclass:: Platsbank
   :members:
