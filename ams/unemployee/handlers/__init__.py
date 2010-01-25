class Handler(object):
    """Handler for tasks of a specific type."""

    def __init__(self, conf):
        self.conf = conf

    def run_task(self, task):
        return self(**dict((str(k), v) for (k, v) in task.args.iteritems()))

    def __call__(self, **kwds):
        raise NotImplementedError("%r doesn't implement any handling code "
                                  "(kwds: %r)" % (self, kwds))

class SimpleHandler(Handler):
    """Single-function handlers are subclasses of this class, with __call__ set
    to the handler function.
    """

def conf_passer(func):
    """Passes the conf instance of a handler as the first argument instead of
    self.
    """
    def inner(self, *a, **kw):
        return func(self.conf, *a, **kw)
    return inner

def simple_handler(name, bases=(SimpleHandler,)):
    def deco(func):
        clsname = func.__name__.replace("_", " ").title().replace(" ", "")
        attrs = {"__call__": conf_passer(func), "type_name": name}
        subcls = type(clsname, bases, attrs)
        return subcls
    return deco

# Here's some fine meta class trickery. RegisterHandlerType is a meta type
# which adds newly created classes of its type to a handlers registry.
class RegisterHandlerType(type):
    def __new__(cls, name, bases, attrs):
        rv = super(RegisterHandlerType, cls).__new__(cls, name, bases, attrs)
        if "_handlers" not in attrs:
            rv._handlers.append(rv)
        return rv

class HandlerRegistry(list):
    """Helper for registering handlers in a module."""

    def __init__(self, *args, **kwds):
        super(HandlerRegistry, self).__init__(*args, **kwds)
        # The aforementioned meta type is subclassed and "bound" to this
        # instance through the use of per-instance subclasses and a _handlers
        # class attribute.
        attrs = {"_handlers": self}
        cls_type = RegisterHandlerType
        self.Handler = cls_type("RHandler", (Handler,), attrs)
        self.SimpleHandler = cls_type("RSimpleHandler", (SimpleHandler,), attrs)

    def simple_handler(self, name):
        """Just like handlers.simple_handler, but registers the handler."""
        # Quite straight-forward, sets base class to our special-type class.
        return simple_handler(name, bases=(self.SimpleHandler,))
