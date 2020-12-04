{
    'name': 'Contacts',
    'version': '13.0.0.1',
    'summary': """ Contacts """,
    'description': """ Contacts """,
    'author': 'GeoTechnosoft',
    'license': 'AGPL-3',
    'website': 'http://www.geotechnosoft.com',
    'category': '',
    'depends': ['base', 'contacts', 'sales_team', 'account'],
    'data': [
        'security/security_view.xml',
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/restrict_create.xml',
        'views/country_view.xml',
    ],

    'installable': True,
    'application': True,
}
