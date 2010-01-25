"""Protocol-related functionality."""

try:
    import cPickle as pickle
except ImportError:
    import pickle

STATUS_DONE = "done"
STATUS_UNHANDLED = "unhandled"
STATUS_FAILED = "failed"
STATUSES = STATUS_DONE, STATUS_UNHANDLED, STATUS_FAILED

class BaseTask(object):
    """Tasks are the abstraction layer between the queue server's job
    representation and the generic interface used throughout AMS.

    See the package's docs for more info on the overall workings.
    """

    def __init__(self, type_name, args):
        """Initialize a new task with type *type_name*, and arguments *args*."""
        self.type_name = type_name
        self.args = args

    def __repr__(self):
        return "%s(%r, %r)" % (type(self).__name__, self.type_name, self.args)

    def __eq__(self, other):
        if hasattr(other, "type_name") and hasattr(other, "args"):
            return other.type_name == self.type_name and other.args == self.args
        return NotImplemented

    @staticmethod
    def decode(raw):
        """Decode raw job data *raw* into a two-tuple of (task type, args).

        The format for the raw data is JSON, with the outermost value being an
        object with at least a type member. The rest of the members are
        arguments. (The type member is removed from args in the return tuple.)
        """
        data = pickle.loads(raw)
        return (data.pop("type"), data)

    def encode(self):
        """Encode the instance into raw job data.

        See the decode method for the data format used.
        """
        data = self.args.copy()
        data["type"] = self.type_name
        return pickle.dumps(data)

    def set_status(self, status):
        """Set status of this task to *status*. The statuses may be one of
        STATUSES.

        If the status is STATUS_DONE, the queue job should be flagged as
        such, so it's not run again.

        If the status is STATUS_FAILED, the queue job should be somehow stored
        so it may be run at a later time.

        If the status is STATUS_UNHANDLED, the queue job should be reinserted
        into the queue server so another pass of next_task might get it again.
        """
        raise NotImplementedError()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
