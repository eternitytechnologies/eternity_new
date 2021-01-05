{
    'name': 'Product',
    'version': '13.0.0.1',
    'summary': """ Product """,
    'description': """ Product """,
    'author': 'GeoTechnosoft',
    'license': 'AGPL-3',
    'website': 'http://www.geotechnosoft.com',
    'category': '',
    'depends': ['product', 'account', 'l10n_in', 'stock_account', 'mail','stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/security_view.xml',
        'views/product_view.xml',
        'views/restrict_product_create.xml',
        'template/email_template.xml',
        'wizard/views/import_quantity.xml'
    ],

    'installable': True,
    'application': True,
}
