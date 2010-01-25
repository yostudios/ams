import sys

import logging
from logging.handlers import WatchedFileHandler

log_format = "%(levelname)9s [%(asctime)s] %(name)s: %(message)s"

# TODO Do to ams.conf what we did to ams.platsbanken.
from ams.conf import all_conf_types
from ams.utils import DSNParseError, setproctitle, mixined, parse_dsn
from ams.platsbanken import get_all_platsbanker, parse_platsbank_dsn
from ams.unemployee import FlexibleUnemployee

default_platsbank_scheme = get_all_platsbanker()[0].dsn_name

def parse_conf_dsn(dsn, conf_types=all_conf_types):
    conf_type_map = dict((ct.dsn_name, ct) for ct in conf_types)
    conf_cls, opts = parse_dsn(dsn, conf_type_map)
    return conf_cls.from_dsn(opts)

import optparse

class SetProcessTitleMixin(object):
    def run_once(self, *a, **kw):
        hstr = ", ".join(self.task_names_handled)
        if len(hstr) > 50:
            hstr = hstr[:47] + "..."
        setproctitle("ams-unemployee: waiting (%s)" % hstr)
        return super(SetProcessTitleMixin, self).run_once(*a, **kw)

    def execute_task(self, task):
        setproctitle("ams-unemployee: executing (%s)" % (task.type_name,))
        return super(SetProcessTitleMixin, self).execute_task(task)

class UnemployeeApp(object):
    parser = optparse.OptionParser()
    parser.add_option("-p", "--platsbank", dest="platsbank_dsn", metavar="DSN",
                      help="Use DSN to connect to Platsbanken.")
    parser.add_option("-c", "--conf", dest="conf_dsn", metavar="CONF",
                      help="Use CONF for configuration.")
    parser.add_option("-v", "--verbose", dest="verbosity", action="count",
                      default=0, help="Increase logging verbosity.")
    parser.add_option("-l", "--log", dest="log_target", default="-",
                      help="Log to target file. Use - for stderr.")
    parser.add_option("-n", "--times", dest="times", metavar="N", type="int",
                      help="Run max N jobs (default: no limit).")

    logger = logging.getLogger("ams.unemployee.app")
    log_levels = logging.DEBUG, logging.INFO, logging.WARN, logging.ERROR
    log_format = "%(levelname)9s [%(asctime)s] %(name)s: %(message)s"
    log_date_format = None

    unemployee_cls = mixined(FlexibleUnemployee, SetProcessTitleMixin)

    def __init__(self, args):
        self.opts, self.args = self.parse_args(args)
        self.setup_logging(self.opts)
        self.conf = self.load_conf(self.opts)
        self.logger.info("using conf %s", self.conf)
        self.platsbank = self.setup_platsbanken(self.opts)
        self.logger.info("platsbank: %s", self.platsbank)
        self.unemployee = self.build_unemployee()

    parse_args = parser.parse_args

    def invalid_setup(self, reason):
        self.logger.error("invalid setup: %s", reason)
        sys.exit(1)

    # {{{ Logging
    def _log_handler(self, target, handler):
        """Set *handler* as a logging handler for *target*, and set some stuff."""
        handler.setFormatter(self.make_logging_formatter())
        target.addHandler(handler)

    def make_logging_formatter(self):
        return logging.Formatter(self.log_format, self.log_date_format)

    def setup_logging(self, opts):
        self.log_level = self.log_levels[max(0, 2 - opts.verbosity)]
        logging.root.setLevel(self.log_level)
        if opts.log_target != "-":
            self.setup_logging_file(self.log_level, opts.log_target)
        else:
            self.setup_logging_stderr(self.log_level)

    def setup_logging_file(self, level, fname, target=logging.root):
        handler = WatchedFileHandler(fname)
        handler.setLevel(level)
        self._log_handler(target, handler)

    def setup_logging_stderr(self, level, target=logging.root):
        handler = logging.StreamHandler()
        handler.setLevel(level)
        self._log_handler(target, handler)
    # }}}

    def load_conf(self, opts):
        try:
            conf = parse_conf_dsn(self.get_conf_dsn(opts))
        except DSNParseError, e:
            self.invalid_setup("dsn %r: %s" % (dsn, e))
        return conf

    def get_conf_dsn(self, opts):
        return opts.conf_dsn

    def setup_platsbanken(self, opts):
        try:
            platsbank = parse_platsbank_dsn(self.get_platsbanken_dsn(opts))
        except DSNParseError, e:
            self.invalid_setup("dsn %r: %s" % (dsn, e))
        return platsbank

    def get_platsbanken_dsn(self, opts):
        if opts.platsbank_dsn:
            return opts.platsbank_dsn
        elif hasattr(self.conf, "platsbank_dsn"):
            return self.conf.platsbank_dsn
        else:
            return default_platsbank_scheme + ":"

    def build_unemployee(self):
        hdlrs = self.load_task_handlers()
        self.platsbank.accept_task_types(hdlr.type_name for hdlr in hdlrs)
        return self.unemployee_cls(self.conf, self.platsbank.next_task, hdlrs)

    def run_unemployee(self, unemp=None):
        if unemp is None:
            unemp = self.unemployee
        self.logger.info("running %s %s times", unemp,
                         self.opts.times or "unlimited")
        unemp.run(self.opts.times)

    def load_task_handlers(self):
        specs = self.args
        if not specs:
            specs = list(getattr(self.conf, "task_handlers", []))
            if not specs:
                self.invalid_setup("no task handlers specs")
        rv = []
        for spec in specs:
            rv.extend(self.load_task_handler(spec))
        return rv

    def load_task_handler(self, spec):
        rv = []
        modname, attrs = spec.rsplit(".", 1)
        self.logger.info("searching module %s for %s", modname, attrs)
        mod = __import__(modname, fromlist=[""])
        self.logger.debug("found module %r", mod)
        # If the specification is *, load by the attribute handlers on the
        # module.
        if attrs == "*":
            if not hasattr(mod, "handlers"):
                raise ValueError("couldn't load specifier %s: module %s has no "
                                 "'handlers' attribute" % (spec, mod))
            self.logger.info("adding task handlers %r", mod.handlers)
            rv = mod.handlers
        else:
            # If we have a specification like {a,b,c}, split it out.
            if attrs.startswith("{") and attrs.endswith("}"):
                attnames = attrs[1:-1].split(",")
            else:
                attnames = (attrs,)
            # Then add the task types one by one.
            for attname in attnames:
                handler = getattr(mod, attname)
                self.logger.info("adding task handler %r", handler)
                rv.append(handler)
        return rv

    @classmethod
    def main(cls):
        self = cls(sys.argv[1:])
        self.run_unemployee()

if __name__ == "__main__":
    UnemployeeApp.main()
