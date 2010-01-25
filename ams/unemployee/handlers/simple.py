"""Simple task handlers like ping, error, etc."""

from ams.unemployee.handlers import HandlerRegistry
from time import sleep
import logging

def make_logger(subname=""):
    if subname:
        subname = "." + subname
    return logging.getLogger("ams.unemployee.handlers.simple" + subname)

logger = make_logger()
handlers = HandlerRegistry()

@handlers.simple_handler("ping")
def log_pings(conf, data):
    make_logger("ping").info("ping: %r", data)

@handlers.simple_handler("raise-error")
def raise_error(conf, value):
    raise TypeError("phony error (%r)" % (value,))

@handlers.simple_handler("sleep")
def do_sleep(conf, delay=5.0):
    sleep(delay)
