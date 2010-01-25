:mod:`ams.unemployee`: Worker interface
=======================================

An unemployee in its most primitive form is represented by this module. It can
run a pass (fetch a task and execute it), fetch tasks, be told to handle
certain task types, and execute tasks.

.. class:: BaseUnemployee(conf, next_task)

   A basic unemployee using `conf` and getting tasks from the callable
   `next_task`.

   A base unemployee does not fully define an interface for handling tasks, but
   leaves this to the subclasses to define.

   .. method:: run_once(timeout=None) -> success

      Run a pass of fetching a task and executing it.

      `timeout` is used for fetching a task, and does *not* specify the duration
      for which the pass must run.

      Returns False if the task fetched can't be handled by this unemployee,
      None if it failed to run, and True if it was successfully executed.

   .. method:: run(times=None)

      Run `times` passes of fetching a task and executing it.

      Essentially calls :meth:`BaseUnemployee.run_once` `times`. If `times` is
      None, runs indefinitely.

   .. method:: handles_task(task) -> bool

      Check if this unemployee can handle `task`.

      Must be overriden by a subclass.
      
      This method may be as smart as it'd like, and does not need to be
      consequent in its return value for certain task types.

   .. method:: execute_task(task)

      Execute `task`.

      Note that :meth:`BaseUnemployee.handles_task` must've been called first
      to determine if the unemployee instance can run the specified task.

      Can be overriden by a subclass, see :meth:`handler_for_task`.

   .. method:: handler_for_task(task):

      Get a handler instance for *task*.

      This is only used by :meth:`execute_task`, and hence either this method
      or :meth:`execute_task` must be overridden in a subclass.

  .. data:: task_names_handled

     A list of task names of the types of tasks handled.

     This attribute doesn't exist on the base class, but setting it will yield
     proper process titles as well as nicer string representations.

Concrete implementations
------------------------

.. class:: SimpleUnemployee(conf, next_task, handler)

   Executes tasks of `handler` type.

   `handler` is expected to be a handler-like callable with a :attr:`type_name`
   attribute.

.. class:: FlexibleUnemployee(conf, next_task, handlers)

   Executes tasks of `handlers` types.

   `handlers` should be a sequence of handler-like callables with
   :attr:`type_name` attributes.
