{
    'name': 'Profitablility Report',
    'version': '13.0.0.1',
    'summary': """ Profitablility Report """,
    'description': """ Profitablility Report """,
    'author': 'GeoTechnosoft',
    'license': 'AGPL-3',
    'website': 'http://www.geotechnosoft.com',
    'category': '',
    'depends': ['sale','base','gts_sale'],
    'data': [
        'security/ir.model.access.csv',
        'security/security_view.xml',
        'views/profitability_report_view.xml',
    ],

    'installable': True,
    'application': True,
}
