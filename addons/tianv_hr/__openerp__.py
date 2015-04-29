# -*- coding: utf-8 -*-
{
    'name': 'Tianv Hr Module',
    'version': '0.2',
    'category': 'human_resources',
    'complexity': "easy",
    'description': """
Tianv Hr Module""",
    'author': 'Matt Cai',
    'website': 'http://odoosoft.com',
    'depends': ['base', 'hr'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hr_view.xml',

    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [],
    'application': True
}
