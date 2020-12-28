{
    'name': 'Product',
    'version': '13.0.0.1',
    'summary': """ Product """,
    'description': """ Product """,
    'author': 'GeoTechnosoft',
    'license': 'AGPL-3',
    'website': 'http://www.geotechnosoft.com',
    'category': '',
    'depends': ['product', 'account', 'l10n_in', 'stock_account', 'mail'],
    'data': [
        'security/security_view.xml',
        'views/product_view.xml',
        'views/restrict_product_create.xml',
        'views/cost_cron.xml',
        'template/email_template.xml',
    ],

    'installable': True,
    'application': True,
}
