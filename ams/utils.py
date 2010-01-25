"""Misc. utilities."""

def endless_range(start=0, step=1):
    i = start
    while True:
        yield i
        i += step

try:
    from setproctitle import setproctitle
except ImportError:
    setproctitle = lambda t: NotImplemented

def mixined(cls, *mixin_clses):
    return type(cls.__name__ + "+Mixins", mixin_clses + (cls,), {})

import sys
import imp
from os import walk, path

def load_whole_package(package_modname):
    package = __import__(package_modname, fromlist=[""], level=0)
    suffixes = imp.get_suffixes()
    origin = path.dirname(package.__file__)
    for dirn, subdirns, fnames in walk(origin):
        subdirns[:] = filter(lambda dn: not dn.startswith("."), subdirns)
        curr_package = package_modname + dirn[len(origin):].replace(path.sep, ".")
        found_mods = {}
        # Phase one: collect modules to load in this directory.
        for fname in fnames:
            for suffix, mode, type_ in suffixes:
                if fname.endswith(suffix):
                    fpath = path.join(dirn, fname)
                    desc = suffix, mode, type_
                    found_mods[fname[:-len(suffix)]] = (fpath, desc)
        # Phase two: load modules in order (to get __init__ first and some
        # predictability.)
        for modname in sorted(found_mods):
            fpath, desc = found_mods[modname]
            if modname == "__init__":
                modname = curr_package
            else:
                modname = curr_package + "." + modname
            # Only load modules if they aren't already.
            if modname not in sys.modules:
                suffix, mode, type_ = desc
                fp = open(fpath, mode)
                try:
                    mod = imp.load_module(modname, fp, fpath, desc)
                finally:
                    fp.close()
                imp.acquire_lock()
                sys.modules[modname] = mod
                imp.release_lock()

# DSN Parsing
import urlparse

class DSNParseError(Exception): pass

def parse_dsn(dsn_url, scheme_map, default_scheme=None):
    """Parse *dsn_url* into a tuple of `(cls, opts)`."""
    dsn = urlparse.urlsplit(dsn_url)
    scheme = dsn.scheme or default_scheme
    if scheme not in scheme_map:
        raise DSNParseError("scheme must be one of %r, not %r" %
                            (scheme_map.keys(), dsn.scheme))
    return scheme_map[scheme], dsn
