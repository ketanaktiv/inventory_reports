from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class ProductAgingWizard(models.TransientModel):
    """Class for invoice summary report."""
    _name = "product.ageing.report"

    start_date = fields.Date(
        string='From Date', required='1', help='select start date')
    end_date = fields.Date(
        string='To Date', required='1', help='select end date')
    location_id = fields.Many2one(
        'stock.location', string='Location', help='select location',
        domain="[('usage', '=', 'internal')]")
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse', help='select warehouse')
    selection = fields.Selection([
        ('location', 'Location'),
        ('warehouse', 'Warehouse')], string="Location/Warehouse",
        default='location')

    @api.onchange('selection')
    def _onchange_selection(self):
        if self.selection == 'location':
            self.warehouse_id = False
        else:
            self.location_id = False

    @api.multi
    def fetch_stock_moves(self, picking_recs, product):
        stock_move_recs = self.env['stock.move'].search(
            [('picking_id', 'in', picking_recs.ids),
             ('product_id', '=', product.id)],
            order='date_expected DESC')
        if stock_move_recs:
            product_sale_total = sum(
                [stock_move_rec.product_uom_qty for stock_move_rec in stock_move_recs])
            if product_sale_total <= product.minimum_qty:
                return {'move_rec': stock_move_recs[0],
                        'sale_quantity': product_sale_total}
            return {}
        else:
            return {'no_sale': True}

    @api.multi
    def get_products_by_location(self, location_rec):
        stock_quant_recs = self.env['stock.quant'].search([
            ('location_id', '=', location_rec.id)])
        product_recs = stock_quant_recs.mapped(
            'product_id').filtered(lambda product: product.in_report)
        return product_recs.ids

    @api.multi
    def get_product_last_month_data(self):
        product_list = []
        vals = []
        if self.location_id:
            product_recs = self.get_products_by_location(self.location_id)
            location_recs = self.location_id
        if self.warehouse_id:
            location_recs = self.env['stock.location'].search(
                [('usage', '=', 'internal')])
            location_ids = []
            for location_rec in location_recs:
                warehouse_rec = location_rec.get_warehouse()
                if warehouse_rec.id == self.warehouse_id.id:
                    product_ids = self.get_products_by_location(location_rec)
                    if product_ids:
                        product_list.extend(product_ids)
                    location_ids.append(location_rec.id)
            location_recs = self.env['stock.location'].browse(location_ids)
            product_recs = self.env['product.product'].browse(product_list)
        if not product_list:
            product_recs = self.env['product.product'].search(
                [('in_report', '=', True),
                 ('type', '=', 'product')])
        if product_recs:
            domain = [('state', 'in', ['confirmed', 'done', 'assigned']),
                      ('picking_type_code', '=', 'outgoing'),
                      ('scheduled_date', '<=', self.end_date),
                      ('scheduled_date', '>=', self.start_date)]
            if self.warehouse_id or self.location_id:
                domain += [('location_id', 'in', location_recs.ids)]
            picking_recs = self.env['stock.picking'].search(domain)
            for product in product_recs:
                data_dict = {}
                stock_move_rec = self.fetch_stock_moves(picking_recs, product)
                if stock_move_rec.get('move_rec'):
                    last_sale_date = datetime.strptime(
                        stock_move_rec['move_rec'].date_expected,
                        "%Y-%m-%d %H:%M:%S")
                    data_dict.update({
                        'product_id': stock_move_rec['move_rec'].product_id,
                        'last_sale_date': str(last_sale_date.date()),
                        'quantity': stock_move_rec['move_rec'].product_uom_qty,
                        'sale_quantity': stock_move_rec['sale_quantity']
                    })
                    vals.append(data_dict)
                if stock_move_rec.get('no_sale'):
                    data_dict.update({
                        'product_id': product,
                        'last_sale_date': False,
                        'quantity': False,
                        'sale_quantity': 0.0
                    })
                    vals.append(data_dict)
        return vals

    @api.multi
    def print_report(self, data):
        if self.start_date > self.end_date:
            raise UserError(_("Period to should be greater than Period From"))
        return self.env.ref(
            'product_ageing_report.action_product_ageing_report').report_action(self)
