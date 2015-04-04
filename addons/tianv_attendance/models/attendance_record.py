# coding=utf-8
__author__ = 'cysnake4713'

# coding=utf-8
from openerp import tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp import models, fields, api
from openerp.tools.translate import _
from dateutil import rrule
import datetime
import pytz


def get_workdays(start, end, holidays=0, days_off=None):
    if days_off is None:
        days_off = 5, 6  # 默认：周六和周日

    workdays = [x for x in range(7) if x not in days_off]
    days = rrule.rrule(rrule.DAILY, dtstart=start, until=end,
                       byweekday=workdays)
    return days.count() - holidays


class AttendanceRecord(models.Model):
    _name = 'tianv.hr.attendance.record'
    _rec_name = 'employee'
    _description = 'Attendance Record'

    employee = fields.Many2one('hr.employee', 'Employee', required=True)
    contract = fields.Many2one('hr.contract', 'Contract', required=True)
    period = fields.Many2one('account.period', 'Plan Period', required=True)

    legal_hour = fields.Float('Legal Total Hours', digits=(12, 1), readonly=True, compute='_compute_hours')
    actual_hour = fields.Float('Actual Total Hours', digits=(12, 1), readonly=True, compute='_compute_hours')
    lines = fields.One2many('tianv.hr.attendance.record.line', 'record', 'Lines')

    _sql_constraints = [
        ('period_uniq', 'unique(period,employee)', 'The period of a employee must be unique per record!'),
    ]

    @api.multi
    def _compute_hours(self):
        for record in self:
            if record.period:
                date_start = fields.Date.from_string(record.period.date_start)
                date_stop = fields.Date.from_string(record.period.date_stop)
                record.legal_hour = get_workdays(date_start, date_stop) * 8
            record.actual_hour = sum([l.record_hour for l in record.lines])

    @api.onchange('employee')
    def _onchange_employee(self):
        if self.employee:
            self.contract = self.employee.contract_id

    @api.multi
    def button_generate_record(self):
        for record in self:
            # clean
            record.lines.unlink()
            # generate
            plan = self.env['tianv.hr.attendance.plan'].search([('period', '=', record.period.id)]).ensure_one()
            for plan_line in plan.lines:
                value = {
                    'plan_line': plan_line.id,
                    'record': record.id,
                }
                line = self.env['tianv.hr.attendance.record.line'].create(value)
                line.process_employee_attendance()

    @api.multi
    def button_clean(self):
        self.lines.unlink()


class AttendanceRecordLine(models.Model):
    _name = 'tianv.hr.attendance.record.line'
    _description = 'Attendance Record Line'
    _order = 'plan_line'

    record = fields.Many2one('tianv.hr.attendance.record', 'Related Record', required=True, ondelete='cascade')

    plan_line = fields.Many2one('tianv.hr.attendance.plan.line', 'Plan Line', required=True)
    plan_date = fields.Date('Plan Date', required=True, compute='_compute_plan', readonly=True)
    plan_date_week = fields.Selection([(0, u'星期一'),
                                       (1, u'星期二'),
                                       (2, u'星期三'),
                                       (3, u'星期四'),
                                       (4, u'星期五'),
                                       (5, u'星期六'),
                                       (6, u'星期日'), ], 'Week', readonly=True, compute='_compute_plan')

    plan_hour = fields.Float('Plan Hour', compute='_compute_plan', readonly=True)
    record_hour = fields.Float('Record Hour')

    tags = fields.Many2many('tianv.hr.attendance.record.type', 'attendance_record_tag_rel', 'record_id', 'tag_id', 'Tags')
    comment = fields.Char('Comment')

    _sql_constraints = [
        ('plan_record_uniq', 'unique(record,plan)', 'The plan must be unique per record!'),
    ]

    @api.multi
    def _compute_plan(self):
        for record in self:
            if record.plan_line:
                record.plan_date = record.plan_line.plan_date
                record.plan_date_week = record.plan_line.plan_date_week
                record.plan_hour = record.plan_line.hour

    @api.one
    def process_employee_attendance(self):
        rule = self.record.contract.attendance_rule
        target_date = self.plan_date
        config = self.env['tianv.hr.attendance.config'].sudo().search(
            [('start_date', '<=', target_date), ('end_date', '>=', target_date)]).ensure_one()

        machine_obj = self.env['tianv.attendance.machine']

        record_hour = 0.0
        tag_ids = []

        for rule_line in rule.lines:
            config_line = config.lines.filtered(lambda obj: obj.type.id == rule_line.type.id)
            if not config_line:
                continue
            # compute punch in
            start_time = None
            config_start_time = self._utc_timestamp(target_date, config_line.start_time)
            if rule_line.is_need_punch_in:
                punch_in_machine = machine_obj.search([('log_time', '>=', self._utc_timestamp(target_date, config_line.start_punch_begin_time)),
                                                       ('log_time', '<=', self._utc_timestamp(target_date, config_line.start_punch_end_time))],
                                                      order='log_time',
                                                      limit=1)
                if punch_in_machine:
                    start_time = punch_in_machine.log_time
            else:
                start_time = config_start_time

            # compute punch in
            end_time = None
            config_end_time = self._utc_timestamp(target_date, config_line.end_time, 1 if config_line.start_time > config_line.end_time else 0)
            if rule_line.is_need_punch_out:
                punch_out_machine = machine_obj.search([('log_time', '>=', self._utc_timestamp(target_date, config_line.end_punch_begin_time)),
                                                        ('log_time', '<=', self._utc_timestamp(target_date, config_line.end_punch_end_time,
                                                                                               1 if config_line.end_punch_begin_time > config_line.end_punch_end_time else 0))],
                                                       order='log_time desc',
                                                       limit=1)
                if punch_out_machine:
                    end_time = punch_out_machine.log_time
            else:
                end_time = config_end_time

            # 如果两个时间都没有,说明旷工
            if start_time is None and end_time is None:
                tag_ids += [self.env.ref('tianv_attendance.attendance_type_absent').id]
            elif start_time is None:
                # 如果只有签出时间,没有签入时间,二而且不需要签出打卡,说明旷工
                if not rule_line.is_need_punch_out:
                    tag_ids += [self.env.ref('tianv_attendance.attendance_type_absent').id]
                # 否则算打卡异常
                else:
                    tag_ids += [self.env.ref('tianv_attendance.attendance_type_error').id]
            elif end_time is None:
                # 如果只有签入时间,没有签出时间,二而且不需要签入打卡,说明旷工
                if not rule_line.is_need_punch_in:
                    tag_ids += [self.env.ref('tianv_attendance.attendance_type_absent').id]
                # 否则算打卡异常
                else:
                    tag_ids += [self.env.ref('tianv_attendance.attendance_type_error').id]

            elif start_time < end_time:
                record_hour += (end_time - start_time).seconds / 3600.0
                # 如果如果超过允许迟到分钟数
                if abs((start_time - config_start_time).seconds / 60) > config_line.allow_late_minute:
                    tag_ids += [self.env.ref('tianv_attendance.attendance_type_late').id]
                if abs((end_time - config_end_time).seconds / 60) > config_line.allow_early_minute:
                    tag_ids += [self.env.ref('tianv_attendance.attendance_type_early').id]

            elif start_time == end_time:
                tag_ids += [self.env.ref('tianv_attendance.attendance_type_error').id]
            elif start_time > end_time:
                tag_ids += [self.env.ref('tianv_attendance.attendance_type_error').id]

        tag_ids = list(set(tag_ids))
        if record_hour > self.plan_hour:
            record_hour = self.plan_hour
        values = {
            'record_hour': record_hour,
            'tags': [(6, 0, tag_ids)],
        }
        self.write(values)

    @api.model
    def _utc_timestamp(self, date, time, timedelta=0):
        """Returns the given timestamp converted to the client's timezone.
           This method is *not* meant for use as a _defaults initializer,
           because datetime fields are automatically converted upon
           display on client side. For _defaults you :meth:`fields.datetime.now`
           should be used instead.

           :param datetime timestamp: naive datetime value (expressed in UTC)
                                      to be converted to the client timezone
           :rtype: datetime
           :return: timestamp converted to timezone-aware datetime in context
                    timezone
        """
        timestamp = datetime.datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT) + datetime.timedelta(hours=time) + datetime.timedelta(days=timedelta)
        assert isinstance(timestamp, datetime.datetime), 'Datetime instance expected'
        tz_name = self.env.context.get('tz') or self.env.user.tz
        if tz_name:
            utc = pytz.timezone('UTC')
            context_tz = pytz.timezone(tz_name)
            context_timestamp = context_tz.localize(timestamp, is_dst=False)  # UTC = no DST
            return context_timestamp.astimezone(utc)
        return timestamp


class AttendanceRecordType(models.Model):
    _name = 'tianv.hr.attendance.record.type'
    _rec_name = 'name'
    _description = 'New Description'

    name = fields.Char('Name', required=True)
