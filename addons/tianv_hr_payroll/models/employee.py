__author__ = 'cysnake4713'

# coding=utf-8
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _
from dateutil import rrule


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    work_start_date = fields.Date('Work Start Date', required=True)

    @api.multi
    def compute_worked_month(self, end_date_string):
        start_date = fields.Date.from_string(self.work_start_date)
        end_date = fields.Date.from_string(end_date_string)
        return rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date).count()

