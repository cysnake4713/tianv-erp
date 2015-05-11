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
    'depends': ['base', 'hr', 'tianv_hr', 'odoosoft_wechat_enterprise'],
    'data': [
        'data/wechat_data.xml',
        'data/service_cron.xml',
        'report/report.xml',
        'report/report_contract.xml',
        'views/contract_view.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [],
    'application': True
}
