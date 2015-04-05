# -*- coding: utf-8 -*-
{
    'name': 'Tianv Attendance Wizard Module',
    'version': '0.2',
    'category': 'attendance',
    'complexity': "easy",
    'description': """
Tianv Attendance Wizard""",
    'author': 'Matt Cai',
    'website': 'http://odoosoft.com',
    'depends': ['base', 'tianv_attendance', 'tianv_insurance'],
    'data': [
        'views/menu.xml',
        'views/attendance_wizard_view.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [],
    'application': True
}
