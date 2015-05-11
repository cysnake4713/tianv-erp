# -*- coding: utf-8 -*-
{
    'name': 'Tianv Contract Module',
    'version': '0.2',
    'category': 'contract',
    'complexity': "easy",
    'description': """
Tianv Contract Module""",
    'author': 'Matt Cai',
    'website': 'http://odoosoft.com',
    'depends': ['base', 'hr_contract'],
    'data': [
        'report/report.xml',
        'report/report_contract.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [],
    'application': True
}
