# coding=utf-8
__author__ = 'cysnake4713'

from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _


class BALANCE(models.Model):
    _name = 'hr.payslip.balance.view'
    _table = 'hr_payslip_balance_view'
    _auto = False

    employee = fields.Many2one('hr.employee', 'Employee')
    contract = fields.Many2one('hr.contract', 'Contract')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    balance = fields.Float('Balance', digits=(12, 2))

    @api.v7
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'hr_payslip_balance_view')

        cr.execute(""" CREATE VIEW hr_payslip_balance_view AS (
            SELECT hr_payslip_line.id AS id,
                    hr_payslip_line.amount AS "balance",
                    hr_payslip.date_from as date_from,
                    hr_payslip.date_to as date_to,
                    hr_payslip.employee_id as employee,
                    hr_payslip.contract_id as contract
            FROM (SELECT id
                FROM hr_salary_rule_category
                WHERE code = 'BALANCE') as BALANCE, hr_payslip_line, hr_payslip
            WHERE hr_payslip_line.category_id = BALANCE.id
                    and hr_payslip_line.slip_id = hr_payslip.id
                    and hr_payslip.state =  'done'
            ORDER BY date_from desc
        )
        """)
