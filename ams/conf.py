"""Configuration system for AMS."""

class BaseConf(object):
    """Provides the basic interface for configuration objects."""

    @property
    def db_type(self):
        """Database type (currently only 'postgresql' is allowed.)

        Subclasses need to override this.
        """
        raise NotImplementedError()

    @property
    def db_info(self):
        """Database information in format of `(name, user, pswd, host, port)`.

        Subclasses need to override this.
        """
        raise NotImplementedError()

class DummyConf(BaseConf):
    """Dummy conf type which reads no configuration at all."""

    dsn_name = "dummy"

    @classmethod
    def from_dsn(cls, dsn):
        if dsn.geturl() != "dummy:":
            raise ValueError("dummy conf doesn't accept options: %r" % (dsn,))
        return cls()

# {{{ Django settings descriptors
# TODO This is essentially an attribute getter.
class DjangoSettingGetter(object):
    def __init__(self, name, settings=None):
        self.name = name

    def __get__(self, instance, owner):
        return getattr(instance.mod, self.name)

class DjangoSettingsGetter(object):
    def __init__(self, names, prefix=None):
        prefix = prefix or ""
        self.names = tuple(prefix + name for name in names)

    def __get__(self, instance, owner):
        return tuple(getattr(instance.mod, name) for name in self.names)
# }}}

class DjangoConf(BaseConf):
    dsn_name = "django"

    def __init__(self, mod, setup_environ=True):
        self.mod = mod
        if setup_environ:
            self.setup_environ(mod)

    def __str__(self):
        return "<%s using %s>" % (type(self).__name__, self.mod)

    @classmethod
    def from_dsn(cls, dsn):
        # Don't auto-setup the environ since we have a better name for the
        # module.
        modname = dsn.path
        mod = __import__(modname, fromlist=[""])
        self = cls(mod, setup_environ=False)
        self.setup_environ(mod, modname)
        return self

    db_type = DjangoSettingGetter("DATABASE_ENGINE")
    db_info = DjangoSettingsGetter(("NAME", "USER", "PASSWORD",
                                    "HOST", "PORT"), prefix="DATABASE_")

    def setup_environ(self, mod, modname=None):
        from django.core.management import setup_environ
        return setup_environ(mod, original_settings_path=modname)

class PyconfConf(BaseConf):
    dsn_name = "py"

    def __init__(self, *args, **kwds):
        raise TypeError("cannot make instances of %r" % (self.__class__,))

    @classmethod
    def from_dsn(cls, dsn):
        return pyconf.load(dsn.path)

try:
    import pyconf
except ImportError:
    del PyconfConf

all_conf_types = list(BaseConf.__subclasses__())
