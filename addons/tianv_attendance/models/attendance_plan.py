__author__ = 'cysnake4713'
# coding=utf-8
from openerp import tools, exceptions
from openerp import models, fields, api
from openerp.tools.translate import _
from dateutil import rrule
import datetime
from datetime import timedelta


def get_workdays(start, end, holidays=0, days_off=None):
    if days_off is None:
        days_off = 5, 6  # 默认：周六和周日

    workdays = [x for x in range(7) if x not in days_off]
    days = rrule.rrule(rrule.DAILY, dtstart=start, until=end,
                       byweekday=workdays)
    return days.count() - holidays


class AttendancePlan(models.Model):
    _name = 'tianv.hr.attendance.plan'
    _rec_name = 'period'
    _order = 'period desc'
    _description = 'Attendance Plan'

    period = fields.Many2one('account.period', 'Plan Period', required=True)

    legal_hour = fields.Float('Legal Total Hours', digits=(12, 1), readonly=True, compute='_compute_hours')
    min_hour = fields.Float('Min Total Hour', digits=(12, 1), readonly=True, compute='_compute_hours')
    holiday_date = fields.Float('Holiday Days', digits=(12, 1))
    actual_hour = fields.Float('Actual Total Hours', digits=(12, 1), readonly=True, compute='_compute_hours')
    lines = fields.One2many('tianv.hr.attendance.plan.line', 'plan', 'Lines')

    _sql_constraints = [
        ('period_uniq', 'unique(period)', 'The period must be unique per plan!'),
    ]

    @api.multi
    def _compute_hours(self):
        for plan in self:
            if plan.period:
                date_start = fields.Date.from_string(plan.period.date_start)
                date_stop = fields.Date.from_string(plan.period.date_stop)
                plan.legal_hour = get_workdays(date_start, date_stop, holidays=plan.holiday_date) * 8.8
                plan.min_hour = get_workdays(date_start, date_stop, holidays=plan.holiday_date) * 8
            plan.actual_hour = sum([l.hour for l in plan.lines])

    @api.multi
    def button_generate_plan(self):
        for plan in self:
            self.lines.unlink()
            date_start = fields.Date.from_string(plan.period.date_start)
            date_stop = fields.Date.from_string(plan.period.date_stop)
            for i in range((date_stop - date_start).days + 1):
                current_date = date_start + timedelta(days=i)
                config_types = False
                if current_date.isoweekday() not in [6, 7]:
                    config_types = [(6, 0, [self.env.ref('tianv_attendance.attendance_config_type_morning').id,
                                            self.env.ref('tianv_attendance.attendance_config_type_afternoon').id])]
                    comment = u'正常上班'
                else:
                    comment = u'周末休息'
                value = {'plan': plan.id, 'plan_date': fields.Date.to_string(current_date), 'config_types': config_types,
                         'comment': comment}
                self.env['tianv.hr.attendance.plan.line'].create(value)
        return True

    @api.model
    def cron_generate_record(self):
        contracts = self.env['hr.contract'].search([('date_start', '<=', fields.Datetime.now()), ('date_end', '>=', fields.Datetime.now())])
        period = self.env['account.period'].search([('date_start', '<=', fields.Datetime.now()), ('date_stop', '>=', fields.Datetime.now())])
        relative_attendances = self.env['tianv.hr.attendance.record'].search(
            [('period', '=', period.id), ('contract', 'in', [e.id for e in contracts])])
        need_process_contracts = contracts.filtered(lambda c: c not in [s.contract for s in relative_attendances])
        for contract in need_process_contracts:
            try:
                new_attendance_record = self.env['tianv.hr.attendance.record'].create({'contract': contract.id, 'period': period.id})
                new_attendance_record.button_generate_record()
            except Exception:
                pass


class AttendancePlanLine(models.Model):
    _name = 'tianv.hr.attendance.plan.line'
    _rec_name = 'plan_date'
    _description = 'Attendance Plan Line'
    _order = 'plan_date'

    plan = fields.Many2one('tianv.hr.attendance.plan', 'Plan', required=True, ondelete='cascade')
    plan_date = fields.Date('Plan Date', required=True)
    plan_date_week = fields.Selection([(0, u'星期一'),
                                       (1, u'星期二'),
                                       (2, u'星期三'),
                                       (3, u'星期四'),
                                       (4, u'星期五'),
                                       (5, u'星期六'),
                                       (6, u'星期日'), ], 'Week', readonly=True, compute='_compute_week')
    config_types = fields.Many2many('tianv.hr.attendance.config.type', 'attendance_plan_config_type_rel', 'plan_line_id', 'type_id', 'Need Work Type')

    hour = fields.Float('Hour', compute='_compute_hour', digits=(12, 1))
    comment = fields.Char('Comment')

    _sql_constraints = [
        ('plan_date_uniq', 'unique(plan,plan_date)', 'The plan_date must be unique per plan!'),
    ]

    @api.multi
    def _compute_week(self):
        for line in self:
            line.plan_date_week = fields.Date.from_string(line.plan_date).isoweekday() - 1

    @api.multi
    def _compute_hour(self):
        for line in self:
            hour = 0.0
            for config_type in line.config_types:
                hour += self.env['tianv.hr.attendance.config'].get_type_work_time(line.plan_date, config_type)
            line.hour = hour

    @api.one
    @api.constrains('plan_date', 'plan')
    def _constrains_date(self):
        plan_date = fields.Date.from_string(self.plan_date)
        date_start = fields.Date.from_string(self.plan.period.date_start)
        date_stop = fields.Date.from_string(self.plan.period.date_stop)

        if not date_start <= plan_date <= date_stop:
            raise exceptions.Warning(_('Plan Date must between plan period'))

