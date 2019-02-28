from odoo import fields, models


class ProductTemplate(models.Model):
    """Class inherit product product."""

    _inherit = "product.template"

    in_report = fields.Boolean(string='In Ageing Report')
    minimum_qty = fields.Float(string="Minimum Sold Qty")
