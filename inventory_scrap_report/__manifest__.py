# -*- coding: utf-8 -*-
{
    'name': "Inventory Scrap Report",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': 'Aktiv Software',
    'website': 'http://www.aktivsoftware.com',
    'category': 'Stock',
    'version': '11.0.1.0.0',
    'depends': ['stock'],
    'data': [
        'wizard/scrap_product_wizard_view.xml',
        'reports/scrap_product_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
