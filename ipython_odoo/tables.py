# coding=utf8
import re
import inspect
from collections import OrderedDict

from odoo.models import LOG_ACCESS_COLUMNS, Model
from odoo.fields import Field

import baron
import redbaron
from texttable import Texttable

from IPython.core.magic import Magics, magics_class, line_magic, cell_magic, line_cell_magic


def vals(model):
    model.ensure_one()
    return {field_name: getattr(model, field_name) for field_name in model._fields}


def prepare_value_for_table(record, field_name):

    if field_name == '__xml_id__':
        return record.get_xml_id()[record.id]

    field = record._fields[field_name]

    if field.type == 'binary':
        return "b'...'"
    else:
        return record[field_name]


def value_to_str(value, col_width):
    value_str = unicode(value)

    if len(value_str) > col_width:
        return value_str[:col_width - 1] + u'…'

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value_str.ljust(col_width)
    else:
        return value_str.ljust(col_width)


def pad_table(table):

    row_count = len(table)
    col_count = len(table[0])

    col_widths = {}
    for col_number in range(col_count):
        col_values = [table[row_number][col_number] for row_number in range(row_count)]
        col_lengths = map(len, map(unicode, col_values))
        col_widths[col_number] = max(col_lengths)

    for col_number in range(col_count):
        col_widths[col_number] = min(col_widths[col_number], 60)

    for row_number in range(row_count):
        for col_number in range(col_count):
            value = table[row_number][col_number]
            col_width = col_widths[col_number]

            table[row_number][col_number] = value_to_str(value, col_width)

    return table


def print_table(table):
    for row in table:
        print(u' '.join(row))

# TODO skip __xml_id__ row if no data
PINNED_FIELD_NAMES = [
    'id',
    'name',
    # 'create_date',
    # 'create_uid',
    # 'write_date',
    # 'write_uid',
]

IGNORE_FIELD_NAMES = set(LOG_ACCESS_COLUMNS)
IGNORE_FIELD_NAMES.add('__last_update')


def field_detailed_name(field):
    detailed_name = field.name

    if field.related:
        detailed_name += u' → ' + u'.'.join(field.related)

    return detailed_name


def get_field_names(fields):

    field_names = OrderedDict()

    for field_name, field in sorted(fields.items()):
        if field_name in IGNORE_FIELD_NAMES:
            continue

        field_names[field_name] = field_detailed_name(field)

    pinned_field_names = OrderedDict({'__xml_id__': '__xml_id__'})
    pinned_field_names.update((pinned_field_name, field_names.pop(pinned_field_name, ''))
                              for pinned_field_name in PINNED_FIELD_NAMES)

    pinned_field_names.update(field_names)

    return pinned_field_names


def prepare_function(func):
    try:
        func_source = inspect.getsource(func)
    except IOError as error:
        func_source = unicode(error)

    # Decrease indent
    func_source_lines = [line for line in func_source.splitlines() if line.strip()]
    min_indent_count = min(len(re.match('^ *', line).group()) for line in func_source_lines)
    func_source = '\n'.join(line[min_indent_count:].rstrip() for line in func_source_lines)

    try:
        red = redbaron.RedBaron(func_source)
    except baron.parser.ParsingError:
        if '@api.returns' in func_source:
            return '-@api.returns-'
        else:
            return '-parsing error-'

    func_def = red[0]
    assert func_def.type == 'def'

    func_body = func_def.value

    # Remove docstring
    first_line = func_body[0]
    if first_line.type == 'string' and first_line.name is None:
        del func_body[0]

    min_indent_count = min(len(line.indentation) for line in func_body)
    func_body.decrease_indentation(min_indent_count)

    func_body_source = func_body.dumps()

    if len(func_body_source) < 180:
        return func_body_source
    else:
        return u'✓'


def get_model_attrs(records, model_attr_name=None):
    models = [klass for klass in records.__class__.__mro__ if Model in klass.__bases__]

    IGNORE_ATTRS = {'_module', '__module__', '_inherit', '_order', '_name', '_description', '__doc__',
                    '_local_constraints', '_local_sql_constraints',}
    models.reverse()

    # Headers
    attrs = [[''] + [model._module for model in models]]

    # TODO show _inherits model attrs like in res.users and product.product
    names = set()
    for model in models:
        if model_attr_name:
            model_attr_names = [model_attr_name]
        else:
            model_attr_names = sorted(model.__dict__.keys())

        for name in model_attr_names:
            if name in names:
                continue

            if name in IGNORE_ATTRS:
                continue

            attrs.append([name] + [mdl.__dict__.get(name) for mdl in models])
            names.add(name)

    return attrs

def prepare_model_attrs(attrs):

    row_count = len(attrs)
    col_count = len(attrs[0])

    for col in xrange(col_count):
        for row in xrange(row_count):
            attr = attrs[row][col]

            if isinstance(attr, Field):
                attrs[row][col] = attr.__class__.__name__

            elif attr is None:
                attrs[row][col] = u''

            elif callable(attr):
                # attrs[row][col] = u'✓'
                attrs[row][col] = prepare_function(attr)

    return attrs


def print_model_attrs(attrs):
    table = Texttable()

    table.set_deco(Texttable.HEADER | Texttable.VLINES | Texttable.HLINES)
    table.set_max_width(180)

    table.add_rows(attrs)

    print(table.draw())

# Python AST
# https://github.com/PyCQA/redbaron         Preferred
# https://github.com/python-rope/rope

# Для вывода таблиц в консоль есть модули   Last release    Stars
# https://pypi.org/project/texttable/       2019            200
# https://pypi.org/project/tabulate/        2019            100
# https://pypi.org/project/termtables/      2019            15
# https://pypi.org/project/tableprint/      2018            100
# https://pypi.org/project/terminaltables/  2016            600
# https://pypi.org/project/PrettyTable/     2013
# https://pypi.org/project/asciitable/      2011

@magics_class
class MyMagics(Magics):

    @line_magic
    def t(self, line):
        """records_table"""

        # import ipdb
        # ipdb.set_trace()

        if not line.strip():
            line = '_'

        records = eval(line, self.shell.user_ns)

        if not isinstance(records, Model):
            return records

        field_names = get_field_names(records._fields)

        table = [[''] * (len(records) + 1) for i in range(len(field_names))]

        for row_number, (field_name, field_detailed_name) in enumerate(field_names.items()):
            table[row_number][0] = field_detailed_name

            for col_number, record in enumerate(records, start=1):
                table[row_number][col_number] = prepare_value_for_table(record, field_name)


        pad_table(table)
        print_table(table)


    @line_magic
    def h(self, line):
        if '.' in line:
            records_var_name, model_attr_name = line.split('.')
        else:
            records_var_name = line
            model_attr_name = ''

        records = eval(records_var_name, self.shell.user_ns)

        attrs = get_model_attrs(records, model_attr_name)
        prepare_model_attrs(attrs)
        print_model_attrs(attrs)
