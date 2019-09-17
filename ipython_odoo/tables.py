# coding=utf8

from collections import OrderedDict, defaultdict

from odoo.models import LOG_ACCESS_COLUMNS, Model

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

def sort_field_names(field_names):
    top_field_presence = OrderedDict((field_name, False) for field_name in PINNED_FIELD_NAMES)
    bottom_field_names = []

    for field_name in sorted(field_names):
        if field_name in top_field_presence:
            top_field_presence[field_name] = True
        else:
            if field_name in IGNORE_FIELD_NAMES:
                pass
            else:
                bottom_field_names.append(field_name)

    top_field_names = [field_name for field_name, is_present in top_field_presence.items() if is_present]
    top_field_names.insert(1, '__xml_id__')

    return top_field_names + bottom_field_names


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

        field_names = sort_field_names(records._fields)

        table = [[''] * (len(records) + 1) for i in range(len(field_names))]

        for row_number, field_name in enumerate(field_names):
            table[row_number][0] = field_name

            for col_number, record in enumerate(records, start=1):
                table[row_number][col_number] = prepare_value_for_table(record, field_name)


        pad_table(table)
        print_table(table)
