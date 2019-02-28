# -*- coding: utf-8 -*-
{
    'name': "Product not moving Report",
    'summary': """
        Display that products which are not sold in selected period.""",
    'description': """
        This reports will display all stockable products which are not\
        sold in selected period.
        User can also filter products by warehouse.
    """,
    'author': 'Aktiv Software',
    'website': 'http://www.aktivsoftware.com',
    'category': 'Stock',
    'version': '11.0.1.0.0',
    'depends': ['stock'],
    'data': [
        'reports/product_not_move_report.xml',
        'wizard/product_not_moving.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
