# coding=utf-8
__author__ = 'cysnake4713'

from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _

from openerp import models, api
from openerp.tools.safe_eval import safe_eval as eval

class HrPayslip(osv.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip', 'odoosoft.workflow.abstract']
    _order = 'date_from desc'

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
            self.sudo().with_context(message_groups=['base.group_hr_manager'],
                                     message=u'员工已确认工资单,请确认是否生效',
                                     wechat_code='tianv_hr_payroll.tianv_hr_payroll',
                                     wechat_template=self.env.ref('tianv_hr_payroll.message_tianv_hr_payslip').id,
                                     ).common_apply()
        return True

    @api.multi
    def button_verified(self):
        self.sudo().write({'is_confirmed': True})
        for payslip in self:
            self.sudo().with_context(message_users=[payslip.employee_id.user_id.id],
                                     message=u'工资单已经生效',
                                     wechat_code='tianv_hr_payroll.tianv_hr_payroll',
                                     wechat_template=self.env.ref('tianv_hr_payroll.message_tianv_hr_payslip').id,
                                     ).common_apply()
        return True

    @api.multi
    def check_done(self):
        return self.is_confirmed

    @api.multi
    def hr_verify_sheet(self):
        super(HrPayslipInherit, self).hr_verify_sheet()
        for payslip in self:
            self.sudo().with_context(message_users=[payslip.employee_id.user_id.id],
                                     message=u'您的工资单已经出来,请确认是否正确',
                                     wechat_code=['tianv_hr_payroll.tianv_hr_payroll'],
                                     wechat_template=self.env.ref('tianv_hr_payroll.message_tianv_hr_payslip').id,
                                     ).common_apply()
        return True


class HrSalaryRuleInherit(models.Model):
    _inherit = 'hr.salary.rule'

    @api.v7
    def compute_rule(self, cr, uid, rule_id, localdict, context=None):
        """
        :param rule_id: id of rule to compute
        :param localdict: dictionary containing the environement in which to compute the rule
        :return: returns a tuple build as the base/amount computed, the quantity and the rate
        :rtype: (float, float, float)
        """
        rule = self.browse(cr, uid, rule_id, context=context)
        if rule.amount_select == 'fix':
            try:
                return rule.amount_fix, float(eval(rule.quantity, localdict)), 100.0
            except:
                raise osv.except_osv(_('Error!'), _('Wrong quantity defined for salary rule %s (%s).') % (rule.name, rule.code))
        elif rule.amount_select == 'percentage':
            try:
                return (float(eval(rule.amount_percentage_base, localdict)),
                        float(eval(rule.quantity, localdict)),
                        rule.amount_percentage)
            except:
                raise osv.except_osv(_('Error!'), _('Wrong percentage base or quantity defined for salary rule %s (%s).') % (rule.name, rule.code))
        else:
            try:
                eval(rule.amount_python_compute, localdict, mode='exec', nocopy=True)
                return float(localdict['result']), 'result_qty' in localdict and localdict['result_qty'] or 1.0, 'result_rate' in localdict and \
                       localdict['result_rate'] or 100.0
            except Exception, e:
                raise osv.except_osv(_('Error!'), _('Wrong python code defined for salary rule %s (%s). error: %s') % (rule.name, rule.code, str(e)))