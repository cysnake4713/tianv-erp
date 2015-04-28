__author__ = 'cysnake4713'

# coding=utf-8
# coding=utf-8
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _

# coding=utf-8
from openerp import models, api


class HrPayslip(osv.Model):
    _name = 'hr.payslip'
    _inherit = 'hr.payslip'

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
        if self.sudo().contract_id.employee_id.user_id.id == self.env.uid:
            return self.sudo().write({'state': 'is_confirmed'})

    @api.multi
    def button_verified(self):
        return self.sudo().write({'is_confirmed': True})

    @api.multi
    def check_done(self):
        return self.is_confirmed