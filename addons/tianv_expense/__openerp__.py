# -*- coding: utf-8 -*-
# __author__ = cysnake4713@gmail.com
{
    'name': 'Tianv Expense Module',
    'version': '0.2',
    'category': 'tianv',
    'complexity': "easy",
    'description': """
Tianv Expense""",
    'author': 'Matt Cai',
    'website': 'http://odoosoft.com',
    'depends': ['base', 'hr_expense'],
    'data': [
        'views/expense_view.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [],
    'application': True
}
