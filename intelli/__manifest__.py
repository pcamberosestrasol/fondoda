# -*- coding: utf-8 -*-
{
    'name': "Intelli",

    'summary': """
        Towers and blinds""",

    'description': """
        New module developed
    """,

    'author': "Estrasol -Kevin Daniel del Campo",
    'website': "https://estrasol.com.mx/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','base_setup','web','mail'],
    #.
    # always loaded
    'data': [
      'security/security.xml',
         'security/ir.model.access.csv',
         
        'views/settings/actuation.xml',   
         'views/settings/area.xml',      
           'views/settings/cloth.xml',      
             'views/settings/control.xml',      
               'views/settings/electronic.xml',      
                 'views/settings/fall.xml',      
                   'views/settings/instalation.xml',
                   'views/settings/pdf.xml',
                    'views/towers/blind.xml', 
                     #'views/towers/blind_admon.xml',         
                    'views/towers/tower.xml',
                      'views/department/department.xml', 
                      'views/department/department_area.xml',          
                     'views/settings/style.xml',  
                     'views/theme/theme.xml',   
                     'views/settings/res_config_settings_views.xml',    
        'views/menus/menus.xml',
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
