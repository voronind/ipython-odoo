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


@api.multi
@api.returns('procurement.rule', lambda value: value.id if value else False)
def _find_suitable_rule(self):
    rule = super(ProcurementOrder, self)._find_suitable_rule()
    if not rule:
        # a rule defined on 'Stock' is suitable for a procurement in 'Stock\Bin A'
        all_parent_location_ids = self._find_parent_locations()
        rule = self._search_suitable_rule([('location_id', 'in', all_parent_location_ids.ids)])
    return rule


def parent_locations(location):
    result = location.browse()
    while location:
        result |= location
        location = location.location_id
    return result


def on_warehouse():
    location = warehouse.lot_stock_id
    return location


def search_suitable_rule(env, product, location=None, warehouse=None):

    expression = odoo.osv.expression
    result = OrderedDict()

    location = location or env['stock.location']

    domain = [('location_id', 'in', parent_locations(location).ids)]

    if warehouse:
        domain = expression.AND([['|', ('warehouse_id', '=', warehouse.id), ('warehouse_id', '=', False)], domain])

    Pull = self.env['procurement.rule']
    # res = self.env['procurement.rule']

    product_routes = product.route_ids | product.categ_id.total_route_ids
    if product_routes:
        result['Product'] = product_res = OrderedDict()
        for route in product_routes.sorted(''):
            product_res[]
        res = Pull.search(expression.AND([[('route_id', 'in', product_routes.ids)], domain]), order='route_sequence, sequence', limit=1)



    if not res:
        warehouse_routes = warehouse.route_ids
        if warehouse_routes:
            res = Pull.search(expression.AND([[('route_id', 'in', warehouse_routes.ids)], domain]), order='route_sequence, sequence', limit=1)
    if not res:
        res = Pull.search(expression.AND([[('route_id', '=', False)], domain]), order='sequence', limit=1)
    return res
