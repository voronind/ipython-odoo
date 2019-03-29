

def table(model):
    vals = model._fields
    for field_name in model._fields:
        for obj in model:
            obj_vals = {field_name}
            vals.append()


def vals(model):
    model.ensure_one()
    return {field_name: getattr(model, field_name) for field_name in model._fields}
