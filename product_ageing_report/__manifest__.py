# -*- coding: utf-8 -*-
{
    'name': "Product Ageing Report",
    'version': '11.0.1.0.0',
    'category': 'Stock',
    'summary': """Product Ageing Report""",
    'website': 'http://www.aktivsoftware.com',
    'author': 'Aktiv Software',
    'license': "AGPL-3",
    'depends': ['stock'],
    'data': [
        'views/product_template.xml',
        'wizard/product_ageing_wizard.xml',
        'report/product_ageing_report_template.xml',
        'report/product_ageing_report.xml',
    ],
    'installable': True,
    'images': [],
    'application': False,
    'auto_install': False,
}
