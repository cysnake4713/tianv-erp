# -*- coding: utf-8 -*-
{
    'name': 'Tianv Attendance Module',
    'version': '0.1',
    'category': 'attendance',
    'complexity': "easy",
    'description': """
Tianv Attendance Module
""",
    'author': 'Matt Cai',
    'website': 'http://odoosoft.com',
    'depends': ['base', 'hr'],
    'data': [
        'views/menu.xml',
        'views/attendance_config_view.xml',
        'views/attendance_rule_view.xml',

    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [],
    'application': True
}
