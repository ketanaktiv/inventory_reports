from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round


class ProductNotMove(models.TransientModel):
    _name = "product.not.move.report"

    @api.model
    def _get_end_date(self):
        # Set current date in end date field
        return datetime.now().date()

    start_date = fields.Date(string="From Date", required=True)
    end_date = fields.Date(string="End Date", required=True,
                           default=_get_end_date)
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")

    @api.multi
    def fetch_stock_moves(self, picking_recs, product):
        stock_move_rec = self.env['stock.move'].search(
            [('picking_id', 'in', picking_recs.ids),
             ('product_id', '=', product.id)],
            order='date_expected DESC', limit=1)
        if stock_move_rec:
            stock_date_object = str(datetime.strptime(
                stock_move_rec.date_expected,
                "%Y-%m-%d %H:%M:%S").date())
            if stock_date_object >= self.start_date and\
                    stock_date_object <= self.end_date:
                return {}
            return {'move_rec': stock_move_rec}
        else:
            return {'no_sale': True}

    @api.multi
    def fetch_picking_data(self, product_rec=False, location_id=False):
        if not product_rec:
            product_rec = self.env['product.product'].search(
                [('type', '=', 'product')])
        vals = []
        domain = [('state', 'in', ['confirmed', 'done', 'assigned']),
                  ('picking_type_code', '=', 'outgoing')]
        if location_id:
            domain += [('location_id', 'in', location_id)]
        picking_recs = self.env['stock.picking'].search(domain)
        if picking_recs:
            for product in product_rec:
                data_dict = {}
                stock_move_rec = self.fetch_stock_moves(
                    picking_recs, product)

                if stock_move_rec.get('move_rec'):
                    last_sale_date = datetime.strptime(
                        stock_move_rec['move_rec'].date_expected,
                        "%Y-%m-%d %H:%M:%S")
                    duration = datetime.today().date() - last_sale_date.date()
                    data_dict.update({
                        'product_id': stock_move_rec['move_rec'].product_id,
                        'last_sale_date': str(last_sale_date.date()),
                        'duration': duration.days
                    })
                    vals.append(data_dict)
                if stock_move_rec.get('no_sale'):
                    data_dict.update({
                        'product_id': product,
                        'last_sale_date': False,
                        'duration': False
                    })
                    vals.append(data_dict)
        return vals

    @api.multi
    def get_product_data(self):
        if self.warehouse_id:
            vals = []
            all_internal_loc_recs = self.env['stock.location'].search(
                [('usage', '=', 'internal')])
            location_list = []
            for location in all_internal_loc_recs:
                warehouse_rec = location.get_warehouse()
                if warehouse_rec.id == self.warehouse_id.id:
                    location_list.append(location.id)
            product_recs = self.env['stock.quant'].search(
                [('location_id', 'in', location_list)]).mapped('product_id')
            vals = self.fetch_picking_data(
                product_recs, location_list)
        else:
            vals = self.fetch_picking_data()
        return vals

    @api.multi
    def get_product_incoming_qty(self, product_rec):
        stock_quant_ids = self.env['stock.quant'].search(
            [('product_id', '=', product_rec.id)])
        location_ids = stock_quant_ids.mapped('location_id')
        location_id_list = location_ids.filtered(
            lambda s: s.usage == "internal").ids
        stock_location_records = {}
        for location_id in location_id_list:
            res = self.sudo().get_product_stock_location(
                location_id, product_rec)
            stock_location_records.update(res)
        incoming_qty = 0.0
        for data in stock_location_records:
            incoming_qty += stock_location_records[data]['incoming_qty']
        return incoming_qty

    def get_product_stock_location(self, location_id, product_id):
        # Get Incoming Quantity of product with perticular location.
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self.env[
            'product.product']._get_domain_locations_new(
                location_id, company_id=False, compute_child=True)
        domain_quant = [('product_id', 'in', product_id.ids)
                        ] + domain_quant_loc
        domain_move_in = [
            ('product_id', 'in', product_id.ids)] + domain_move_in_loc
        domain_move_out = [
            ('product_id', 'in', product_id.ids)] + domain_move_out_loc
        Move = self.env['stock.move']
        Quant = self.env['stock.quant']
        domain_move_in_todo = [
            ('state', 'not in', ('done', 'cancel', 'draft'))] + domain_move_in
        domain_move_out_todo = [
            ('state', 'not in', ('done', 'cancel', 'draft'))] + domain_move_out
        moves_in_res = dict((item['product_id'][0], item[
            'product_qty']) for item in Move.read_group(
            domain_move_in_todo, ['product_id', 'product_qty'], [
                'product_id']))
        moves_out_res = dict((item['product_id'][0], item[
            'product_qty']) for item in Move.read_group(
            domain_move_out_todo, ['product_id', 'product_qty'], [
                'product_id']))
        quants_res = dict((item['product_id'][0], item[
            'quantity']) for item in Quant.read_group(
            domain_quant, ['product_id', 'quantity'], ['product_id']))
        res = dict()
        for product in product_id:
            res[location_id] = {}
            qty_available = quants_res.get(product.id, 0.0)
            res[location_id]['qty_available'] = float_round(
                qty_available, precision_rounding=product.uom_id.rounding)
            res[location_id]['incoming_qty'] = float_round(moves_in_res.get(
                product.id, 0.0), precision_rounding=product.uom_id.rounding)
            res[location_id]['outgoing_qty'] = float_round(moves_out_res.get(
                product.id, 0.0), precision_rounding=product.uom_id.rounding)
            res[location_id]['virtual_available'] = float_round(
                qty_available +
                res[location_id]['incoming_qty'] -
                res[location_id]['outgoing_qty'],
                precision_rounding=product.uom_id.rounding)
        return res

    @api.multi
    def print_product_report(self):
        if self.start_date > self.end_date:
            raise UserError(_("Period to should be greater than Period From"))
        return self.env.ref(
            'product_not_move_report.report_product_move').report_action(self)
