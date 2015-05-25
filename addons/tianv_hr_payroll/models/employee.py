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
        result = rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date).count()
        return result - 1 if result > 0 else 0

    @api.multi
    def get_insurance_record_by_date(self, date_start, date_end):
        try:
            return self.env['tianv.social.insurance.record'].search(
                [('period.date_start', '<=', date_start), ('period.date_stop', '>=', date_end), ('state', '=', 'confirm')]).ensure_one()
        except Exception:
            raise exceptions.Warning(_("can't find insurance record in period or have multi record for one period"))


