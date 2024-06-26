def recordset_formatter(records):
    if len(records) == 1:
        ids_part = f'{records.id}: {records.display_name}'
    else:
        ids_part = ', '.join(map(str, records._ids))

    print(f'{records._name}({ids_part})')

def setup_recordset_pretty_formatting(ipython):
    try:
        from odoo import models
    except ImportError:
        return

    ipython.display_formatter.ipython_display_formatter.for_type(
        models.BaseModel,
        recordset_formatter,
    )
