__author__ = 'cysnake4713'
# coding=utf-8
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _


class HrHolidaysInherit(models.Model):
    _name = 'hr.holidays'
    _inherit = ['hr.holidays', 'odoosoft.workflow.abstract']

    _defaults = {
        'date_from': lambda *o: fields.Date.today() + ' 01:00:00',
        'date_to': lambda *o: fields.Date.today() + ' 10:00:00',
    }

    @api.multi
    def holidays_confirm(self):
        result = super(HrHolidaysInherit, self).holidays_confirm()
        self.with_context(**{
            'message_users': [u.id for u in self.env.ref('base.group_hr_manager').users],
            'message': '需要您的审批',
            'wechat_code': ['tianv_holidays.wechat_code'],
            'wechat_template': self.env.ref('tianv_holidays.message_tianv_holidays').id,
        }).common_apply()
        return result