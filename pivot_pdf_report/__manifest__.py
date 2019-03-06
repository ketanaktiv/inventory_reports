# -*- coding: utf-8 -*-
{
    'name': "Pivot PDF Report",
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
    'depends': ['stock', 'web'],
    'data': [
        'views/add_js.xml',
        'reports/stock_quant_report.xml',
    ],
    'qweb': ['static/src/xml/base_pivot_buttons.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
