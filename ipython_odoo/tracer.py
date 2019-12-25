import inspect
import logging
import sys
from contextlib import contextmanager
from functools import wraps

from odoo.models import BaseModel

from .hierarchy import recordset_models

INTEREST_METHODS = {
    'sale.order': {
        '_prepare',
        'search',
    },

    'all': {
        'create',
        'write',
        'unlink',
    },
}

logger = logging.getLogger('debug')


def path_model_method(method):

    @wraps(method)
    def wrapped_method(self, *args, **kwargs):
        logger.debug('soma')
        return method(self, *args, **kwargs)

    return wrapped_method


def patch_model_methods(env):

    any_model_methods = INTEREST_METHODS.pop('all', set())

    for model_name, method_names in INTEREST_METHODS:
        models = recordset_models(env[model_name])
        for method_name in method_names:

            method = models.__dict__.get(method_name)
            if method:
                pass

# TRACE
all_method_names = reduce(set.union, INTEREST_METHODS.values())


def get_self(frame):
    if frame.f_code.co_name in all_method_names:
        args_info = inspect.getargvalues(frame)
        self = args_info.locals.get('self')
        if isinstance(self, BaseModel):
            return self

def trace(frame, event, arg):

    if event == 'call':
        self = get_self(frame)
        if self is not None:
            print self, frame.f_code.co_name
            return trace

    elif event == 'return':
        self = get_self(frame)
        if self is not None:
            print self, frame.f_code.co_name, 'returns', arg


@contextmanager
def tracing():
    sys.settrace(trace)
    yield
    sys.settrace(None)
