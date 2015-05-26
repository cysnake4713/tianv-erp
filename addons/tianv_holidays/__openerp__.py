# -*- coding: utf-8 -*-
{
    'name': ' Module',
    'version': '0.2',
    'category': 'odoosoft',
    'complexity': "easy",
    'description': """
""",
    'author': 'Matt Cai',
    'website': 'http://odoosoft.com',
    'depends': ['base', 'hr_holidays', 'odoosoft_workflow', 'odoosoft_wechat_enterprise'],
    'data': [
        'data/wechat_data.xml',
        'views/holidays_view.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [],
    'application': True
}
