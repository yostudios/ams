Example usages
==============

Misc. example usages of how the application library might be used.

Adding a configuration type
---------------------------

You might want to add a configuration type, either because you dislike the
existing support for them, or you want other formats, or you want to hook some
settings into your own, or whatever. Here's how.

.. code-block:: python

    import pyconf
    from ams.unemployee.app import UnemployeeApp

    class MyUnemployeeApp(UnemployeeApp):
        default_conf_dsn = "pyconf:pkgname=foo"

        def load_conf(self, opts):
            dsn = opts.conf_dsn or self.default_conf_dsn
            if dsn.startswith("pyconf:"):
                spec, val = dsn[7:].split("=", 1)
                return pyconf.load(**{spec: val})
            else:
                return super(MyUnemployeeApp, self).load_conf(opts)

.. silly** vim bug

.. note:: As you might see this is an area where there's room for improvement.
          You could also add your configuration type to
          :attr:`ams.conf.all_conf_types`, but this isn't finalized as the way
          to go yet.
