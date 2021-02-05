# -*- coding: utf-8 -*-
{
    'name' : 'GTS SO MO LINK',
    'version': '11.0.0',
    'summary': 'This module enables the functionality to count MO of Sale Orders.',
    'category': 'MRP',
    'description': """
    This module shows a MO smart button,which gives you the list and count of Manfacturing Orders,
    related to its SO.
    """,
    'sequence': 1,
    'author': 'Geo Technosoft',
    'website': 'https://www.geotechnosoft.com',
    'depends': ['sale', 'mail', 'mrp_account', 'stock', 'mrp','report_custom_layout','account'],
    'data': [
        'security/ir.model.access.csv',
        'security/security_view.xml',
        'views/sale_order_view.xml',
        'views/stock_move_lots.xml',
        'views/mrp_view.xml',
        'views/lot_serial_view.xml',
        'views/produce_wiz_view.xml',
        'views/test_report_view.xml',
        'views/bom_view.xml',
        'reports/qrcode_mo.xml',
        'reports/test_report.xml',
        'reports/lot_qr_report.xml',
        'reports/label_report.xml',
        'reports/warranty_card.xml',
        'reports/report_bom_mrp.xml',
        'wizard/views/update_mo.xml',
        'views/move_view.xml'
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
}
