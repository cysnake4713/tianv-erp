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
    'depends': ['base', 'hr_payroll', 'hr_contract', 'hr', 'odoosoft_workflow', 'odoosoft_wechat_enterprise'],
    'data': [
        'data/wechat_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/employee_view.xml',
        'views/contract_view.xml',
        'views/payslip_view.xml',
        'views/payroll_menu.xml',
        'views/menu.xml',
        'data/data.xml',

        'report/report.xml',
        'report/report_payslip.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [],
    'application': True
}
