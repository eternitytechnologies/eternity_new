{
    'name': 'Account',
    'version': '13.0.0.1',
    'summary': """ Account """,
    'description': """ Account """,
    'author': 'GeoTechnosoft',
    'license': 'AGPL-3',
    'website': 'http://www.geotechnosoft.com',
    'category': '',
    'depends': ['base', 'account', 'report_custom_layout', 'sale', 'web', 'sale_stock'],
    'data': [
        'security/security_view.xml',
        'views/invoice_form.xml',
        'report/external_layout.xml',
        'report/report_invoice_eternity.xml',
        'report/report_invoice_inherit.xml',
        'report/report_view.xml',
        'report/report_invoice_sr_number.xml'
    ],
    'installable': True,
    'application': True,
}
