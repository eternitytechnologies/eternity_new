{
    "name": " Daily Analysis Email Reporting",
    "sequence": "1",
    "summary": "Daily analysis Email Report",
    "version": "13.0.1.0.1",
    "category": "email",
    "author": "TECHNOGEO SOFT Pvt. Ltd.",
    "website": "http://www.geotechnosoft.com",
    "description": """

        """,
    "license": "LGPL-3",
    "installable": True,
    "depends": ['base', 'account', 'sale', 'crm', 'mrp', 'purchase','mail'],
    "data": [
        'security/security_view.xml',
        'views/daily_analysis.xml',
    ],
}
