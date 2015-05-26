# -*- coding: utf-8 -*-
{
    'name': 'Tianv Social Insurance Module',
    'version': '0.2',
    'category': 'attendance',
    'complexity': "easy",
    'description': """
Tianv Social Insurance Module
""",
    'author': 'Matt Cai',
    'website': 'http://odoosoft.com',
    'depends': ['base', 'hr', 'account', 'mail', 'odoosoft_workflow', 'odoosoft_wechat_enterprise'],
    'data': [
        'data/cron.xml',
        'data/wechat_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        #
        'views/insurance_view.xml',
        'views/insurance_record_view.xml',
        # 'views/hr_contract_view.xml',
        'views/menu.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [],
    'application': True
}
