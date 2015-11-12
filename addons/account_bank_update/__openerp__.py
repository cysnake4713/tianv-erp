# -*- coding: utf-8 -*-
# __author__ = cysnake4713@gmail.com
{
    'name': 'Tianv Account Bank Statement Update Module',
    'version': '0.2',
    'category': 'odoosoft',
    'complexity': "easy",
    'description': """
Tianv Account Bank Statement Update""",
    'author': 'Matt Cai',
    'website': 'http://odoosoft.com',
    'depends': ['base'],
    'data': [
        'views/account_bank_statement_view.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [],
    'application': True
}
