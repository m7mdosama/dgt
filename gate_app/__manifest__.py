# -*- coding: utf-8 -*-
{
    'name': "Security Gate",

    'description': """ Invoices and Deliveries Sources """,

    'summary': """
        Easily get invoices and deliveries sources to security gate and get Driver car's information
        """,

    'author': "BTC GOLD",
    'website': "https://btcegyptgold.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase', 'account_accountant', 'account', 'stock' , 'sale_management'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/gate_view.xml',
        'views/persons_view.xml',
    ],
    'sequence': 60,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'installable': True,

}
