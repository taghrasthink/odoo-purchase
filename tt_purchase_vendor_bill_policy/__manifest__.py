{
    'name': 'Purchase Vendor Bill Policy',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'Define purchase bill control policy at the vendor level with override on each purchase order.',
    'description': """
Purchase Vendor Bill Policy
===========================
Adds a third configuration level for the purchase bill control policy:

* Vendor (res.partner) — default policy for all POs of this vendor
* Purchase Order — inherited from vendor, editable while draft/sent
* Falls back to product's own policy when set to "Product Policy"

Hierarchy: Purchase Order > Vendor > Product > Global setting.
    """,
    'author': 'TaghrasThink',
    'website': 'https://github.com/taghrasthink',
    'license': 'LGPL-3',
    'depends': [
        'purchase',
    ],
    'data': [
        'views/res_partner_views.xml',
        'views/purchase_order_views.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
