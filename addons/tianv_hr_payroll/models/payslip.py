# coding=utf-8
__author__ = 'cysnake4713'

from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _

from openerp import models, api


class HrPayslip(osv.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip', 'odoosoft.workflow.abstract']

    _columns = {
        'state': fields.selection([
            ('draft', 'Draft'),
            ('verify', 'Waiting'),
            ('is_confirmed', 'Is Confirmed'),
            ('done', 'Done'),
            ('cancel', 'Rejected'),
        ], 'Status', select=True, readonly=True, copy=False),

        'is_confirmed': fields.boolean('Is Confirmed'),
    }

    _defaults = {
        'is_confirmed': False,
    }


class HrPayslipInherit(models.Model):
    _name = 'hr.payslip'
    _inherit = 'hr.payslip'

    @api.multi
    def button_is_confirmed_sheet(self):
        if self.sudo().employee_id.user_id.id == self.env.uid:
            self.sudo().write({'state': 'is_confirmed'})
            self.with_context(message_groups=['base.group_hr_manager'],
                              message=u'员工已确认工资单,请确认是否生效',
                              wechat_code='tianv_hr_payroll.tianv_hr_payroll',
                              wechat_template=self.env.ref('tianv_hr_payroll.message_tianv_hr_payslip').id,
                              ).common_apply()

    @api.multi
    def button_verified(self):
        self.sudo().write({'is_confirmed': True})
        for payslip in self:
            self.with_context(message_users=[payslip.employee_id.user_id.id],
                              message=u'工资单已经生效',
                              wechat_code='tianv_hr_payroll.tianv_hr_payroll',
                              wechat_template=self.env.ref('tianv_hr_payroll.message_tianv_hr_payslip').id,
                              ).common_apply()

    @api.multi
    def check_done(self):
        return self.is_confirmed

    @api.multi
    def hr_verify_sheet(self):
        super(HrPayslipInherit, self).hr_verify_sheet()
        for payslip in self:
            self.with_context(message_users=[payslip.employee_id.user_id.id],
                              message=u'您的工资单已经出来,请确认是否正确',
                              wechat_code=['tianv_hr_payroll.tianv_hr_payroll'],
                              wechat_template=self.env.ref('tianv_hr_payroll.message_tianv_hr_payslip').id,
                              ).common_apply()