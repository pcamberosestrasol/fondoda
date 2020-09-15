# -*- coding: utf-8 -*-
{
    'name': "Fondo de ahorros",
 
    'summary': """
        Colaboradores y prestamos""",

    'description': """
        New module developed
    """,

    'author': "Estrasol - Pablo Camberos",
    'website': "https://estrasol.com.mx/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','base_setup','web','mail','contacts','portal'],
    #.
    # always loaded
    'data': [
      'views/contact/contact.xml',
      'reports/reports.xml',
      'reports/solicitud_alta.xml',
      'mail/mail_colab.xml',
      #'security/security.xml',
      #'security/ir.model.access.csv', 
    ],  
     'qweb': [
           #'qweb/replace_menu_base.xml',
         ]
        ,
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}
