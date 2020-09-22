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
        #views
      'views/contact/contact.xml',
      'reports/reports.xml',
      'reports/solicitud_alta.xml',
      'mail/mail_colab.xml',
      'security/security.xml',
      'static/src/xml/theme.xml',
      'security/ir.model.access.csv', 
      'views/prestamo/prestamo.xml',
      'views/settings.xml',
      #sequence
      'data/prestamo_folio.xml',
      #wizard
      'wizard/terminos.xml',
      #menu
      'views/menu.xml', 
    ],  
     'qweb': [
           "qweb/*.xml",
         ]
        ,
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    # "qweb": ["static/src/xml/*.xml"],
    'application': True,
}
