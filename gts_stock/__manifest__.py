{
    'name': 'GTS Stock',
    'version': '13.0.0.1',
    'summary': """ Stock """,
    'description': """ Stock """,
    'author': 'GeoTechnosoft',
    'license': 'AGPL-3',
    'website': 'http://www.geotechnosoft.com',
    'category': 'Inventory',
    'depends': ['base', 'stock', 'sale_stock','report_custom_layout'],
    'data': [
        'security/ir.model.access.csv',
        'report/report_delivery_document_inherit.xml',
        'report/report_picking_inherit.xml',
        'report/qrcode_delivery.xml',
        'report/test_certificate.xml',
        'report/mrp_production_templates_inherit.xml',
        'report/warranty_card.xml',
        'views/stock_picking.xml',
        'views/stock_move_view.xml',
        'views/warranty_view.xml',
        'views/warranty.xml',
        'wizard/update_product_variant.xml',
    ],
    'installable': True,
    'application': True,
}
