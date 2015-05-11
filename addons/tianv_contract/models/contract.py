# coding=utf-8

__author__ = 'cysnake4713'
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _
from datetime import date
from datetime import timedelta


class ContractInherit(models.Model):
    _inherit = 'hr.contract'
    _order = 'date_end desc'

    work_info = fields.Char('Work Info')
    contract_wage = fields.Float('Contract Wage')

    @api.model
    def cron_contract_reminder(self):
        employees = self.env['hr.employee'].search([('active', '=', True)])
        need_process_employee = []
        for employee in employees:
            if employee.contract_id is not None and employee.contract_id.date_end and fields.Date.from_string(
                    employee.contract_id.date_end) <= date.today() - timedelta(days=10):
                need_process_employee += [employee]

        if need_process_employee:
            template_id = self.env['ir.model.data'].get_object('tianv_contract', 'contract_cron_email_template')
            users = self.env.ref('base.group_hr_manager').users
            ctx = {
                'data': need_process_employee,
            }

            wechat_template = self.env.ref('tianv_contract.message_tianv_hr_contract')
            for user_id in users:
                template_id.with_context(ctx).send_mail(user_id.id, force_send=False)

            self.env['odoosoft.wechat.enterprise.message'].create_message(obj=None,
                                                                          content=wechat_template.with_context(data=need_process_employee).render(),
                                                                          code='tianv_hr_contract.tianv_hr_contract', user_ids=[u.id for u in users],
                                                                          type='news', title=wechat_template.title)



