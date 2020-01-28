# coding=utf8
__import__('os').environ['TZ'] = 'UTC'
__import__('pkg_resources').declare_namespace('odoo.addons')

import os
import time
from collections import OrderedDict

from .model_names import CONVERT_ENV_KEYS
# http://localhost:63342/api/file//home/voronin/projects/sintez_addons/sintez_base/__manifest__.py:1

from .access import get_user_permissions


def get_model_vars(env):
    model_vars = {}

    for key, model in env.items():
        if key in CONVERT_ENV_KEYS:
            model_vars[CONVERT_ENV_KEYS[key]] = model
        else:
            pass
            # logging.error('No %r in CONVERT_ENV_KEYS', key)

        # underscore_key = key.replace('.', '_')
        # model_vars[CONVERT_ENV_KEYS.get(key, underscore_key)] = model

    return model_vars

OPERATORS = {
    '=', '!=',
    '>', '<',
    '>=', '<=',
    '=?',
    '=like',
    'like', 'not like',
    'ilike', 'not ilike',
    '=ilike',
    'in', 'not in',
    'child_of',
}

# OP_SUFFIXES = {
#     '=': '_',
#     '!=': '_ne',
#     '>': '_gt',
#     '<': '_lt',
#     '>=': '_gte',
#     '<=': '_lte',
#     '=?': '_set',
#     '=like': '_pattern',
#     'like': '_like',
#     'not like': '_not_like',
#     'ilike': '_ilike',
#     'not ilike': '_not_ilike',
#     '=ilike': '_ipattern',
#     'in': '_in',
#     'not in': '_not_in',
#     'child_of': '_child_of',
# }

SUFFIX_TO_OPERATOR = OrderedDict([
    ('_', '='),
    ('_eq', '='),       # Specially
    ('_ne', '!='),
    ('_gt', '>'),
    ('_lt', '<'),
    ('_gte', '>='),
    ('_lte', '<='),
    ('_set', '=?'),
    ('_pattern', '=like'),
    ('_ipattern', '=ilike'),
    ('_not_like', 'not like'),      # _not_like is before _like
    ('_like', 'like'),
    ('_not_ilike', 'not ilike'),    # _not_ilike is before _ilike
    ('_ilike', 'ilike'),
    ('_not_in', 'not in'),          # _not_in is before _in
    ('_in', 'in'),
    ('_child_of', 'child_of'),
])

OPERATOR_TO_SUFFIX = {operator: suffix for suffix, operator in SUFFIX_TO_OPERATOR.items()}

# INTEGER_OPS = ['=', '!=', '>', '<', '>=', '<=', 'not in', 'in']
# CHAR_OPS = ['=', '!=', '=like', '=ilike', 'not like', 'like', 'not ilike', 'ilike']   # _ -> ilike, _eq -> =
# MANY_OPS = ['=', 'not in', 'in']

BOOLEAN_SUFFIXES = OrderedDict([
    ('_', '='),
])

RELATION_SUFFIXES = OrderedDict([
    ('_', '='),
    ('_ne', '!='),

    ('_not_in', 'not in'),          # _not_in is before _in
    ('_in', 'in'),
])

NUMBER_SUFFIXES = OrderedDict([
    ('_', '='),
    ('_ne', '!='),

    ('_gt', '>'),
    ('_lt', '<'),
    ('_gte', '>='),
    ('_lte', '<='),

    ('_not_in', 'not in'),          # _not_in is before _in
    ('_in', 'in'),
])

CHAR_SUFFIXES = OrderedDict([
    ('_eq', '='),       # Specially
    ('_ne', '!='),

    # ('_pattern', '=like'),
    # ('_ipattern', '=ilike'),

    ('_not_like', 'not like'),      # _not_like is before _like
    ('_like', 'like'),

    ('_not_ilike', 'not ilike'),    # _not_ilike is before _ilike
    ('_', 'ilike'),

    ('_not_in', 'not in'),          # _not_in is before _in
    ('_in', 'in'),
])

FIELD_SUFFIXES = OrderedDict()
FIELD_SUFFIXES.update(CHAR_SUFFIXES)
FIELD_SUFFIXES.update(NUMBER_SUFFIXES)


def get_suffix_reverse(operators):
    suffix_dict = OrderedDict()
    for op in operators:
        suffix_dict[op] = OPERATOR_TO_SUFFIX[op]

    return suffix_dict

# boolean - eq only

# integer
# float
# monetary

# text
# html - None

# date
# datetime

# binary none

# selection  is int or varchar

suffix_choser = {
    'boolean': BOOLEAN_SUFFIXES,

    'integer': NUMBER_SUFFIXES,
    'float': NUMBER_SUFFIXES,
    'monetary': NUMBER_SUFFIXES,

    'char': CHAR_SUFFIXES,
    # TODO: Select can be integer
    'selection': CHAR_SUFFIXES,

    'many2one': RELATION_SUFFIXES,
    'one2many': RELATION_SUFFIXES,
    'many2many': RELATION_SUFFIXES,
}

assert len(set(OPERATOR_TO_SUFFIX.keys())) == len(OPERATOR_TO_SUFFIX), 'Not all suffixes is unique'


def get_search_func_kwargs(model):
    # kwargs = {}
    kwargs = []
    for field_name, field in model._fields.items():
        if field.type in suffix_choser:
            kwargs.extend(field_name + op_suffix for op_suffix in suffix_choser[field.type])

    return kwargs


def split_kwarg_name(model, var_name):
    for suffix in SUFFIX_TO_OPERATOR:
        if var_name.endswith(suffix):
            field_name = var_name[:-len(suffix)]
            if suffix == '_' and model._fields[field_name].type == 'char':
                operator = 'ilike'
            else:
                operator = SUFFIX_TO_OPERATOR[suffix]
            return field_name, operator

    assert False, 'Incorrect var name'


# TODO Make keyword-only arguments
search_def = '''
def search(self, ids=None, count=False, {kwargs}):
    local_vars = locals()
    domains = []
    for kwarg_name in {kwargs_set}:
        kwarg_value = local_vars[kwarg_name]
        if kwarg_value is None:
            continue
        kwarg_name, operator = split_kwarg_name(self, kwarg_name)
        domains.append((kwarg_name, operator, kwarg_value))

    if ids:
        if domains:
            raise ValueError('No ids and kwargs together')
    
        if isinstance(ids, (str, unicode)):
            domains.append(('name', 'ilike', ids))
        else:
            return self.browse(ids)
            
    # domains.append(('create_date', '>', '2019-11-24 10:55:00'))
            
    return self.search(domains, count=count)
'''

def model_str(self):
    if 1 <= len(self) <= 1 and 'name' in self._fields:
        ids_part = []
        for record in self:
            name = record.name

            if not name:
                name = u'---'

            if len(name) > 40:
                name = name[:39] + u'...'
            # strip u in u'...'
            name = repr(name)[1:]
            ids_part.append('{}: {}'.format(record.id, name))
        result = '{}({})'.format(self._name, ', '.join(ids_part))
        # return result.encode('utf8')
        return result

    return "%s%s" % (self._name, getattr(self, '_ids', ""))


def model_unicode(self):
    if 1 <= len(self) <= 1 and 'name' in self._fields:
        ids_part = []
        for record in self:
            name = record.name

            if not name:
                name = u'---'

            if len(name) > 40:
                name = name[:39] + u'…'
            ids_part.append(u"{}: '{}'".format(record.id, name))
        return u'{}({})'.format(self._name, u', '.join(ids_part))

    return u"%s%s" % (self._name, getattr(self, '_ids', ""))


def patch_models(env):

    for model in env.values():
        common_kwargs = {
            'limit': 1000,
        }

        kwarg_names = get_search_func_kwargs(model)

        kwargs_def = ', '.join(kwarg_name + '=None' for kwarg_name in kwarg_names)
        kwargs_set = '{' + ','.join(map(repr, kwarg_names)) + '}'

        model_search_def = search_def.format(kwargs=kwargs_def, kwargs_set=kwargs_set)

        exec(model_search_def)
        model.__class__.__call__ = search

        # model.__class__._origin__str__ = model.__class__.__str__
        model.__class__.__str__ = model_str
        model.__class__.__unicode__ = model_unicode
        model.__class__.__repr__ = model_str

# def get_odoo_domain(domain):
#     # if domain.left ...
#     odoo_domain = (domain.left.name, domain.operator, domain.right)
#     return [odoo_domain]


# def model_call_method(self, *args):
#     # domain = reduce(operator.and_, args)
#     odoo_domain = get_odoo_domain(args[0])
#     return self.search(odoo_domain)


# class FieldsNamespace(object):
#     def __getattr__(self, field_name):
#         return DomainField(field_name)


# class Domain(object):
#     NEG_OPERATOR = {
#         '<': '>',
#         '<=': '>=',
#         '=': '!=',
#         'like': 'not like',
#         'ilike': 'not ilike',
#         'in': 'not in',
#     }
#
#     NEG_OPERATOR.update({op2: op1 for op1, op2 in NEG_OPERATOR.items()})
#
#     def __init__(self, left, operator, right):
#         self.left = left
#         self.operator = operator
#         self.right = right
#
#     def __and__(self, domain):
#         return Domain(self, '&', domain)
#
#     def __or__(self, domain):
#         return Domain(self, '|', domain)
#
#     def __neg__(self):
#         neg_operator = self.NEG_OPERATOR[self.operator]
#         return Domain(self.left, neg_operator, self.right)


# class DomainField(object):
#     def __init__(self, name):
#         self.name = name
#
#     def __eq__(self, other):
#         if type(other) is list:
#             return Domain(self, 'in', other)
#         else:
#             return Domain(self, '=', other)
#
#     def __ne__(self, other):
#         return Domain(self, '!=', other)
#
#     def __gt__(self, other):
#         return Domain(self, '>', other)
#
#     def __ge__(self, other):
#         return Domain(self, '>=', other)
#
#     def __lt__(self, other):
#         return Domain(self, '<', other)
#
#     def __le__(self, other):
#         return Domain(self, '<=', other)
#
#     # def __=?__(self, other):
#     #     return Domain(self, '=?', other)
#
#     def __imod__(self, other):
#         """
#         %=
#         """
#         return Domain(self, '=like', other)
#
#     def __mod__(self, other):
#         return Domain(self, 'like', other)
#
#     # def __ilike__(self, other):
#     #     return Domain(self, 'ilike', other)
#
#     # def __=ilike__(self, other):
#     #     return Domain(self, '=ilike', other)
#
#     def child_of(self, other):
#         return Domain(self, 'child_of', other)


def init_odoo():
    import odoo

    # init(args)
    # config.parse_config(sys.argv[1:])

    # odoo.tools.config.parse_config("""--database=dev
    # --addons-path=.,../custom_addons
    # --update=sintez_base,sintez_account,sintez_crm,sintez_mrp,sintez_mrp_production_purchase,sintez_product,sintez_product_cost_bom_auto,sintez_purchase,sintez_sale,sintez_stock
    # """.split())

    # odoo_db_name = os.environ['ODOO_DEV_DB_NAME']
    # odoo_db_name = 'fix-rule'
    # odoo_db_name = 'report3'
    # odoo_db_name = 'fix-bombe-rules'
    # odoo_db_name = 'sm-po'
    # odoo_db_name = 'sale-order'
    # odoo_db_name = 'contact-change-log'
    # odoo_db_name = 'oktmo'
    # odoo_db_name = 'competitor'
    # odoo_db_name = '78'
    # odoo_db_name = 'ip-service'
    # odoo_db_name = 'lead'
    # odoo_db_name = 'head'
    odoo_db_name = os.environ['DB_NAME']

    # update = ('sintez_base,sintez_account,sintez_crm,sintez_mrp,sintez_mrp_production_purchase,'
    #           'sintez_product,sintez_product_cost_bom_auto,sintez_purchase,sintez_sale,sintez_stock')
    # update = ['sintez_crm']
    update = []
    extra = ''

    updates = ' --update={}'.format(update) if update else ''

    # extra = ' --log-level=debug_sql'

    odoo_args = "--database={} --xmlrpc-port=8099 --addons-path=addons,custom_addons ".format(odoo_db_name) + updates + extra

    odoo.tools.config.parse_config(odoo_args.split())

    odoo.cli.server.report_configuration()
    odoo.service.server.start(preload=[], stop=True)

    # shell(config['db_name'])
    # with odoo.api.Environment.manage():
    #     registry = odoo.registry(odoo.tools.config['db_name'])
    #     with registry.cursor() as cr:
    #         uid = odoo.SUPERUSER_ID
    #         ctx = odoo.api.Environment(cr, uid, {})['res.users'].context_get()
    #         env = odoo.api.Environment(cr, uid, ctx)
    #
    #         user_ns = {'env': env}
    #         start_time = time.time()
    #
    #         models = get_model_vars(env)
    #         user_ns.update(models)
    #
    #         for model in models.values():
    #             model.__class__.__call__ = model_call_method
    #
    #         user_ns['c'] = FieldsNamespace()
    #
    #         finish_time = time.time()
    #         print('Time it: {:.3f}'.format(finish_time - start_time))
    #
    #         from IPython import start_ipython
    #         start_ipython(argv=['notebook', '--profile=sintez'], user_ns=user_ns)
    #
    #         cr.rollback()

    # Enter
    env_manage = odoo.api.Environment.manage()
    env_manage.__enter__()
    registry = odoo.registry(odoo.tools.config['db_name'])
    cr = registry.cursor()

    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    user_ns = {
        'odoo': odoo,
        'env': env,
        'cr': env.cr,
        'commit': env.cr.commit,
        'rollback': env.cr.rollback,
        'ref': env.ref,
        'self': env.user,
    }
    start_time = time.time()
    models = get_model_vars(env)
    user_ns.update(models)

    patch_models(env)

    # user_ns['c'] = FieldsNamespace()
    # for model in models.values():
    #     model.__class__.__call__ = model_call_method

    print('Time it: {:.3f}'.format(time.time() - start_time))

    user_ns['environment_management'] = env_manage
    return user_ns

    # Exit: on close or unload extension
    cr.rollback()
    cr.__exit__()
    env_manage.__exit__()

    # Cursor class
    # def __exit__(self, exc_type, exc_value, traceback):
    #     if exc_type is None:
    #         self.commit()
    #     self.close()

    # @classmethod
    # @contextmanager
    # def manage(cls):
    #     """ Context manager for a set of environments. """
    #     if hasattr(cls._local, 'environments'):
    #         yield
    #     else:
    #         try:
    #             cls._local.environments = Environments()
    #             yield
    #         finally:
    #             release_local(cls._local)

    # Environment.manage().__exit__():


from .magic import MyMagics


def load_ipython_extension(ipython):
    # The `ipython` argument is the currently active `InteractiveShell`
    # instance, which can be used in any way. This allows you to register
    # new magics or aliases, for example.
    print('Init Odoo...')
    ipython.push('get_user_permissions')
    ipython.push({'i': ipython})
    ipython.push(init_odoo())

    # ipython.register_magic_function(records_table, magic_name='t')
    ipython.register_magics(MyMagics)


def unload_ipython_extension(ipython):
    # If you want your extension to be unloadable, put that logic here.
    pass
