from __future__ import print_function
import inspect
import sys

from functools import partial

from .util import is_stringish

# Set
#
# - METAFLOW_DEBUG_SUBCOMMAND=1
#   to see command lines used to launch subcommands (especially 'step')
# - METAFLOW_DEBUG_SIDECAR=1
#   to see command lines used to launch sidecars
# - METAFLOW_DEBUG_S3CLIENT=1
#   to see command lines used by the S3 client. Note that this environment
#   variable also disables automatic cleaning of subdirectories, which can
#   fill up disk space quickly


class Debug(object):
    def __init__(self):
        import metaflow.metaflow_config as config

        for typ in config.DEBUG_OPTIONS:
            if getattr(config, "DEBUG_%s" % typ.upper()):
                op = partial(self.log, typ)
            else:
                op = self.noop
            # use debug.$type_exec(args) to log command line for subprocesses
            # of type $type
            setattr(self, "%s_exec" % typ, op)
            # use the debug.$type flag to check if logging is enabled for $type
            setattr(self, typ, op != self.noop)

    def log(self, typ, args):
        if is_stringish(args):
            s = args
        else:
            s = " ".join(args)
        lineno = inspect.currentframe().f_back.f_lineno
        filename = inspect.stack()[1][1]
        print("debug[%s %s:%s]: %s" % (typ, filename, lineno, s), file=sys.stderr)

    def __getattr__(self, name):
        # Small piece of code to get pyright and other linters to recognize that there
        # are dynamic attributes.
        return getattr(self, name)

    def noop(self, args):
        pass


debug = Debug()
