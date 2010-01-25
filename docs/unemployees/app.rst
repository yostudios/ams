:mod:`ams.unemployee.app`: Application library
==============================================

An unemployee has a defined set of task types it can handle, and this module
helps setting this up. It also provides an interface for running a predefined
number of jobs, and so on.

It's what could be referred to as an application library, if such a thing
exists. It provides a command-line interface for developers to extend with
their own domain-specific needs.

This module is mainly for helping developers set up the tedious bits and
pieces, like a configuration file, a :mod:`ams.platsbanken` interface, and so
on.

Overall structure
-----------------

The application is defined by the :class:`UnemployeeApp` class. The intent is
for the developer to subclass it, and customize what may need customization.

For example, it may be useful to override configuration loading, then merely
override :meth:`UnemployeeApp.load_conf`.

The setting up of the application is done, step-by-step, like this:

1. Parse the arguments (:meth:`UnemployeeApp.parse_args`),
2. setup logging (:meth:`UnemployeeApp.setup_logging`),
3. load configuration (:meth:`UnemployeeApp.load_conf`),
4. setup platsbanken (:meth:`UnemployeeApp.setup_platsbanken`),
5. build unemployee instance (:meth:`UnemployeeApp.build_unemployee`).

DSNs
----

The application library makes use of DSNs, or *database source name* as the
acronyms expand to, which are essentially URIs. For example, specifying that
the Platsbanken interface to use is a `beanstalkd` on the default host and
default port is written as::

    $ ./my_unemployee.py -p beanstalk:

In short, DSNs are nothing more than a simple form of URIs.

.. _unemp_logging:

Logging
-------

A basic logging setup is done using :class:`logging.WatchedFileHandler`. This
logging handler supports log rotation. Alternatively, if the logging target is
``-``, then logging is done to standard error.

The two methods to look at for overriding the behavior of either path is
:meth:`UnemployeeApp.setup_logging_file` and
:meth:`UnemployeeApp.setup_logging_stderr`. If you're looking to customize the
log formatter, have a look-see at :meth:`UnemployeeApp.make_logging_formatter`.

Configuration
-------------

The configuration file specified is loaded through a DSN. Refer to the relevant
documentation for more information on the subject.

.. seealso:: :mod:`ams.conf`

.. _handler_spec:

Task handler specifications
---------------------------

It's possible to specify handlers in a number of ways, in a globbing-like
fashion. A few examples:

* ``foo.handlers.bar.Barer``: Loads ``Barer`` of ``foo.handlers.bar``.
* ``foo.handlers.bar.*``: Loads each handler in the ``handlers`` attribute on
  ``fo.handlers.bar``.
* ``foo.handlers.bar.{Barer,Quuxer}``: Loads ``Barer`` and ``Quuxer`` of
  ``foo.handlers.bar``.

Reference
---------

.. class:: UnemployeeApp(args)

   `args` are the command-line arguments to run. (``sys.argv[1:]`` is a common
   value here.)

   .. method:: parse_args(args) -> opts, args

      Parse the arguments `args` into `opts` object and `args` sequence.

      .. note:: This is commonly a bound
                :meth:`optparse.OptionParser.parse_args` method.

   .. method:: invalid_setup(reason)

      Issue an error with `reason` relating to the setup of the unemployee.

      This exits the process.

   .. method:: run_unemployee(unemp=None)

      Runs `unemp` or :attr:`UnemployeeApp.unemployee` if `unemp` is None.

      Also passes the defined number of times to run.

   .. classmethod:: main()

      Set up a new instance based on ``sys.argv[1:]`` and run it.

   .. rubric:: Logging setup

   .. method:: make_logging_formatter() -> logging.Formatter

      Make the logging formatter to use for the log handler.

      Uses :attr:`UnemployeeApp.log_format` for the format and
      :attr:`UnemployeeApp.log_date_format` for the date format.

   .. method:: setup_logging_file(level, fname, target=logging.root)

      Set up a logging handler that logs to `fname` at `level` and attaches it
      to `target`.

   .. method:: setup_logging_stderr(level, target=logging.root)

      Set up a logging handler that logs to standard error at `level` and
      attaches it to `target`.

   .. method:: setup_logging(opts)

      Set up logging based on `opts`.

      Uses :attr:`opts.log_target` to determine where to log, and
      :attr:`opts.log_level` to determine logging level.

      .. seealso:: :ref:`unemp_logging`

   .. rubric:: Configuration

   .. method:: load_conf(opts) -> configuration

      Load configuration based on `opts`.

      Loads the configuration specified by the  DSN returned by
      :meth:`~UnemployeeApp.get_conf_dsn`.

   .. method:: get_conf_dsn(opts) -> dsn
      
      Return the DSN specified by :attr:`opts.conf_dsn` (i.e. the ``-c`` or
      ``--conf`` command-line options.)

   .. rubric:: Platsbanken and Unemployee

   .. method:: setup_platsbanken(opts) -> platsbanken

      Set up a platsbanken interface.

      Creates Platsbanken from the DSN provided by
      :meth:`~UnemployeeApp.get_platsbanken_dsn`.
      
   .. method:: get_platsbanken_dsn(opts) -> dsn

      Retrieves the DSN to use for Platsbanken based on `opts`, or the loaded
      configuration file if none is specified in `opts`.

      Uses the DSN specified by :attr:`opts.platsbank_dsn` (i.e. the ``-p`` or
      ``--platsbank`` command-line options), the :attr:`platsbank_dsn`
      configuration attribute, or defaults to ``"dummy:"``.

   .. method:: build_unemployee() -> unemployee

      Build an unemployee instance.
      
      Configures the platsbanken interface to accept tasks of the types loaded
      by :meth:`UnemployeeApp.load_task_handlers`, and then instanciates
      :attr:`UnemployeeApp.unemployee_cls` with `next_task` bound to the
      platsbanken interface.

   .. method:: load_task_handlers() -> list of handlers

      Load each of the task type specifications on the argument list.

      If no specifications were given on the command-line, looks for
      :attr:`task_handlers` in the configuration object.

   .. method:: load_task_handler(spec) -> list of handlers

      Load task handler specification `spec`.

      This could result in one or more handlers, depending on the specification.

      .. seealso:: :ref:`handler_spec`
