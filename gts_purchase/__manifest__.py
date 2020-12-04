{
    'name': 'Purchase',
    'version': '13.0.0.1',
    'summary': """ Purchase """,
    'description': """ Purchase """,
    'author': 'GeoTechnosoft',
    'license': 'AGPL-3',
    'website': 'http://www.geotechnosoft.com',
    'category': '',
    'depends': ['base', 'purchase'],
    'data': [
        'views/purchase_view.xml',
        'report/report_purchase_order_inherit.xml',
        'report/report_purchase_quotation_inherit.xml',
    ],
    'installable': True,
    'application': True,
}
