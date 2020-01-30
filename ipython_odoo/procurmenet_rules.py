from collections import OrderedDict


def _search_suitable_rule(self, domain):
    """ First find a rule among the ones defined on the procurement order
    group; then try on the routes defined for the product; finally fallback
    on the default behavior """
    if self.warehouse_id:
        domain = expression.AND(
            [['|', ('warehouse_id', '=', self.warehouse_id.id), ('warehouse_id', '=', False)], domain])
    Pull = self.env['procurement.rule']
    res = self.env['procurement.rule']
    if self.route_ids:
        res = Pull.search(expression.AND([[('route_id', 'in', self.route_ids.ids)], domain]),
                          order='route_sequence, sequence', limit=1)
    if not res:
        product_routes = self.product_id.route_ids | self.product_id.categ_id.total_route_ids
        if product_routes:
            res = Pull.search(expression.AND([[('route_id', 'in', product_routes.ids)], domain]),
                              order='route_sequence, sequence', limit=1)
    if not res:
        warehouse_routes = self.warehouse_id.route_ids
        if warehouse_routes:
            res = Pull.search(expression.AND([[('route_id', 'in', warehouse_routes.ids)], domain]),
                              order='route_sequence, sequence', limit=1)
    if not res:
        res = Pull.search(expression.AND([[('route_id', '=', False)], domain]), order='sequence', limit=1)
    return res


def parent_locations(location):
    result = location.browse()
    while location:
        result |= location
        location = location.location_id
    return result


def by_company(company, product):
    warehouse = env['stock.warehouse'].search([('company_id', '=', company.id)], limit=1)
    # location = warehouse.lot_stock_id
    location = env.ref('stock.stock_location_customers')
    return search_suitable_rule(product, location=location, warehouse=warehouse)


def search_suitable_rule(product=None, location=None, warehouse=None):
    from collections import OrderedDict

    expression = odoo.osv.expression
    result = OrderedDict()

    location = location or env['stock.location']
    warehouse = warehouse or env['stock.warehouse']

    domain = [('location_id', 'in', parent_locations(location).ids)]

    if warehouse:
        domain = expression.AND([['|', ('warehouse_id', '=', warehouse.id), ('warehouse_id', '=', False)], domain])

    Pull = env['procurement.rule']

    if product:
        product_routes = product.route_ids | product.categ_id.total_route_ids
        if product_routes:
            result['Product'] = product_res = OrderedDict()
            for route in product_routes.sorted('sequence'):
                product_rules = Pull.search(expression.AND([[('route_id', 'in', route.ids)], domain]), order='route_sequence, sequence')
                if product_rules:
                    product_res[route] = product_rules

    warehouse_routes = warehouse.route_ids
    if warehouse_routes:
        result['Warehouse'] = warehouse_res = OrderedDict()
        for route in warehouse_routes.sorted('sequence'):
            warehouse_rules = Pull.search(expression.AND([[('route_id', 'in', route.ids)], domain]), order='route_sequence, sequence')
            if warehouse_rules:
                warehouse_res[route] = warehouse_rules

    global_rules = Pull.search(expression.AND([[('route_id', '=', False)], domain]), order='sequence')
    if global_rules:
        result['Global'] = global_rules

    return result


def warehouse_rules(warehouse_or_company):
    from collections import OrderedDict
    from odoo.osv import expression

    result = OrderedDict()

    if warehouse_or_company._name == 'stock.warehouse':
        warehouse_id = warehouse_or_company.id
    elif warehouse_or_company._name == 'res.company':
        warehouse_id = env['res.company'].search([('company_id', '=', warehouse_or_company.id)], limit=1).id
    else:
        raise TypeError('Arg must be Warehouse or Company')


    warehouse_id =
    rules = env['procurement.rules'].search([('warehouse_id', '=', )])

    location = location or env['stock.location']
    warehouse = warehouse or env['stock.warehouse']

    domain = [('location_id', 'in', parent_locations(location).ids)]

    if warehouse:
        domain = expression.AND([['|', ('warehouse_id', '=', warehouse.id), ('warehouse_id', '=', False)], domain])

    Pull = env['procurement.rule']

    if product:
        product_routes = product.route_ids | product.categ_id.total_route_ids
        if product_routes:
            result['Product'] = product_res = OrderedDict()
            for route in product_routes.sorted('sequence'):
                product_rules = Pull.search(expression.AND([[('route_id', 'in', route.ids)], domain]), order='route_sequence, sequence')
                if product_rules:
                    product_res[route] = product_rules

    warehouse_routes = warehouse.route_ids
    if warehouse_routes:
        result['Warehouse'] = warehouse_res = OrderedDict()
        for route in warehouse_routes.sorted('sequence'):
            warehouse_rules = Pull.search(expression.AND([[('route_id', 'in', route.ids)], domain]), order='route_sequence, sequence')
            if warehouse_rules:
                warehouse_res[route] = warehouse_rules

    global_rules = Pull.search(expression.AND([[('route_id', '=', False)], domain]), order='sequence')
    if global_rules:
        result['Global'] = global_rules

    return result
