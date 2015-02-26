# -*- coding: utf-8 -*-
{
    'name': 'Tianv Attendance Machine Module',
    'version': '0.2',
    'category': 'attendance',
    'complexity': "easy",
    'description': """
    Tianv Attendance Machine Module
""",
    'author': 'Matt Cai',
    'website': 'http://odoosoft.com',
    'depends': ['base', 'hr'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/machine_view.xml',
        'views/menu.xml',

        'data/data.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [],
    'application': True
}
