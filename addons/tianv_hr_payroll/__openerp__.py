# -*- coding: utf-8 -*-
{
    'name': 'Tianv Hr Payroll Module',
    'version': '0.2',
    'category': 'odoosoft',
    'complexity': "easy",
    'description': """
Tianv Hr Payroll Module""",
    'author': 'Matt Cai',
    'website': 'http://odoosoft.com',
    'depends': ['base', 'hr_payroll', 'hr_contract', 'hr'],
    'data': [
        'views/employee_view.xml',
        'views/contract_view.xml',
        'views/menu.xml',
        'data/data.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [],
    'application': True
}
