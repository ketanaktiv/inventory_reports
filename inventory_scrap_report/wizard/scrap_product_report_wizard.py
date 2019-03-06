from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ScrapProductWizard(models.TransientModel):
    _name = "scrap.product.wizard"

    @api.model
    def _get_end_date(self):
        # Set current date in end date field
        return datetime.now().date()

    start_date = fields.Date(string="From Date", required=True)
    end_date = fields.Date(string="To Date", required=True,
                           default=_get_end_date)
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")

    @api.multi
    def get_product_data(self, scrap_recs):
        vals = []
        location_recs = scrap_recs.mapped('location_id')
        for location_rec in location_recs:
            data_dict = {location_rec.id: []}
            sp_recs = scrap_recs.with_context(location_id=location_rec).filtered(
                lambda sp: sp.location_id == sp._context['location_id'].id)
            for sp_rec in sp_recs:
                data = {'product_id': sp_rec.product_id,
                        'quantity': sp_rec.scrap_qty,
                        'location_id': location_rec.id}

    @api.multi
    def get_scrap_products(self):
        domain = [('date_expected', '>=', self.start_date),
                  ('date_expected', '<=', self.end_date)]
        scrap_recs = self.env['stock.scrap'].search(domain)
        if self.warehouse_id:
            location_recs = scrap_recs.mapped('location_id')
            list_location = []
            for location_rec in location_recs:
                warehouse_rec = location_rec.get_warehouse()
                if warehouse_rec.id == self.warehouse_id.id:
                    list_location.append(location_rec.id)
            scrap_recs = scrap_recs.with_context(
                list_location=list_location).filtered(
                lambda sp: sp.location_id in sp._context['list_location'])
            vals = self.get_product_data(scrap_recs)
        else:
            vals = self.get_product_data(scrap_recs)
        return vals

    @api.multi
    def print_sp_report(self):
        if self.start_date > self.end_date:
            raise UserError(_("To Date should be greater than From Date."))
        return self.env.ref(
            'inventory_scrap_report.report_scrap_product').report_action(self)
