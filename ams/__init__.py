"""AMS -- takes care of handing out jobs to unemployees.

The fundamental concept in AMS is the task type. Each task is of a specific
task type, and each unemployee can handle any number of task types through the
use of task handlers.

The task handlers are simply callables which take at least a conf argument, and
any number of keyword arguments which are passed on as task data.

The job data in the queue system for AMS is serialized using JSON.
"""
