# coding=utf8

from collections import OrderedDict, defaultdict

from IPython.core.magic import Magics, magics_class, line_magic, cell_magic, line_cell_magic


def table(model):
    vals = model._fields
    for field_name in model._fields:
        for obj in model:
            obj_vals = {field_name}
            vals.append()


def vals(model):
    model.ensure_one()
    return {field_name: getattr(model, field_name) for field_name in model._fields}


def prepare_value_for_table(record, field_name):
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


@magics_class
class MyMagics(Magics):

    @line_magic
    def t(self, line):
        """records_table"""
        records = eval(line, self.shell.user_ns)

        fields = sorted(records._fields.items())

        table = [[''] * (len(records) + 1) for i in range(len(fields))]

        for row_number, (field_name, field) in enumerate(sorted(records._fields.items())):
            table[row_number][0] = field_name

            for col_number, record in enumerate(records, start=1):
                table[row_number][col_number] = prepare_value_for_table(record, field_name)


        pad_table(table)
        print_table(table)
