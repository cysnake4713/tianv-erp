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
    'depends': ['base', 'hr', 'account', 'tianv_machine', 'hr_holidays'],
    'data': [
        'data/data.xml',
        'views/menu.xml',
        'views/attendance_config_view.xml',
        'views/attendance_rule_view.xml',
        'views/attendance_plan_view.xml',
        'views/attendance_record_view.xml',

    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [],
    'application': True
}
