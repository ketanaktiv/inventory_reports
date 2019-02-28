from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    picking_type_code = fields.Selection([
        ('incoming', 'Vendors'),
        ('outgoing', 'Customers'),
        ('internal', 'Internal')], related='picking_type_id.code',
        readonly=True, store=True)
