.. module:: ams.unemployee.handlers

:mod:`ams.unemployee.handlers`: Handlers support
================================================

The handler support in AMS is *completely optional*, i.e., it is only a
well-defined interface, very little actual implementation (but there is some.)

Handlers are instances of subclasses of the :class:`Handler` class.

This class is then initialized with the current configuration object as the
sole argument, and its :meth:`~Handler.run_task` method is called with the task
object.

.. class:: Handler(conf)

   A handler for a certain type of job, the one described by type name
   :attr:`~Handler.type_name`.

   Consider this the interface definition.

   .. attribute:: type_name

      The name of the type of task this handler handles. This must not change,
      ever.

   .. method:: run_task(task)

      Run `task`. It is up to each handler to decide how to run the actual
      task.

Lifecycle of a handler
----------------------

A handler is a short-lived object, and should be able to run multiple jobs on a
single instance. However, handlers are always reinstantiated by AMS when a new
task is to be handled.

Simple handlers
---------------

So, with the very simple interface being done with, there are some helpers to
define handlers and collections thereof.

Firstly there is the concept of *simple handlers*. These are single-function
handlers, and also the most common case. Simple handlers are produced by the
function factory (or decorator) :func:`simple_handler`. It creates subclasses
of :class:`SimpleHandler`.

Usage is simple, consider the lillies::

    from ams.unemployees.handlers import simple_handler

    @simple_handler("foo-handler")
    def foo_handler(conf, a, b):
        print a, "+", b, "=", a + b

.. function:: simple_handler(name, [bases]) -> decorator

   Returns a decorator which will replace the function decorated with a
   subclass of :class:`SimpleHandler`.

   The class name is taken from the function's name, with some automated
   camelcasing applied.

Handler registries
------------------

A handler registry is a glorified name for a list of handlers.

Instances have two relevant attributes, :attr:`~HandlerRegistry.Handler` and
:meth:`~HandlerRegistry.simple_handler`.

.. class:: HandlerRegistry()

   Subclass of the list data type with helpers for registering new handlers
   when they're defined.

   .. class:: Handler()

      Special subclass of the base :class:`Handler` that appends any subclasses
      to the current instance.

   .. method:: simple_handler(name) -> decorator

      Special wrapper for :func:`simple_handler` that passes
      ``self.SimpleHandler`` as base class.

      This effectively appends new simple handlers to the current instance.

It might seem complicated, but to reiterate our previous example::

    from ams.unemployee.handlers import HandlerRegistry

    handlers = HandlerRegistry()

    @handlers.simple_handler("foo-handler")
    def foo_handler(conf, a, b):
        print a, "+", b, "=", a + b

``handlers`` above will have ``foo_handler`` in it. Well, actually it will have
a class with that function as the call handler.

As you might've figured out, handler registries are handy when specifying which
tasks an unemployee should handle, if the above module would be called
``fooproj.handlers``, then the following command-line would be enough to
include all handlers in that module::

    $ ./ams-unemp.py fooproj.handlers.*

Star globbing in the task type specification means "look for attribute
``handlers``".
