# -*- coding: utf-8 -*-
# __author__ = cysnake4713@gmail.com
{
    'name': 'Tianv Project Module',
    'version': '0.2',
    'category': 'odoosoft',
    'complexity': "easy",
    'description': """
Tianv Project Module""",
    'author': 'Matt Cai',
    'website': 'http://odoosoft.com',
    'depends': ['base', 'account', 'tianv_service', 'odoosoft_workflow'],
    'data': [
        'views/menuitem.xml',
        'views/project_type_view.xml',
        'views/project_template_view.xml',
        'views/project_view.xml',
        'views/project_record.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [],
    'application': True
}
