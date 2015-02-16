# -*- coding: utf-8 -*-
{
    'name': 'Tianv Attendance Machine Module',
    'version': '0.2',
    'category': 'tianv',
    'complexity': "easy",
    'description': """
    Tianv Attendance Machine Module
""",
    'author': 'Matt Cai',
    'website': 'http://odoosoft.com',
    'depends': ['base', 'hr'],
    'data': [
        'views/machine_view.xml',
        'views/menu.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [],
    'application': True
}
