# coding=utf-8
__author__ = 'cysnake4713'

from openerp import tools, exceptions
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
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
    _order = 'period desc'
    _description = 'Attendance Record'

    contract = fields.Many2one('hr.contract', 'Contract', required=True)
    employee = fields.Many2one('hr.employee', 'Employee', readonly=True, compute='_compute_info')
    period = fields.Many2one('account.period', 'Plan Period', required=True)

    legal_hour = fields.Float('Legal Total Hours', digits=(12, 1), readonly=True, compute='_compute_info')
    min_hour = fields.Float('Min Total Hours', digits=(12, 1), readonly=True, compute='_compute_info')
    holiday_date = fields.Float('Holiday Days', digits=(12, 1), readonly=True, compute='_compute_info')
    actual_hour = fields.Float('Actual Total Hours', digits=(12, 1), readonly=True, compute='_compute_info')
    plan_hour = fields.Float('Plan Total Hours', digits=(12, 1), readonly=True, compute='_compute_info')

    late_time = fields.Integer('Late Time', readonly=True, compute='_compute_info')
    early_time = fields.Integer('Early Time', readonly=True, compute='_compute_info')
    absent_time = fields.Float('Absent Hour', readonly=True, digits=(12, 1), compute='_compute_info')
    leave_time = fields.Float('Personal Leave Hour', readonly=True, digits=(12, 1), compute='_compute_info')
    sick_time = fields.Float('Sick Leave Hour', readonly=True, digits=(12, 1), compute='_compute_info')
    plan = fields.Many2one('tianv.hr.attendance.plan', 'Related Plan')

    lines = fields.One2many('tianv.hr.attendance.record.line', 'record', 'Lines')

    _sql_constraints = [
        ('period_uniq', 'unique(period,employee)', 'The period of a employee must be unique per record!'),
    ]

    @api.multi
    def _compute_info(self):
        absent_tag = self.env.ref('tianv_attendance.attendance_type_absent')
        late_tag = self.env.ref('tianv_attendance.attendance_type_late')
        early_tag = self.env.ref('tianv_attendance.attendance_type_early')
        leave_tag = self.env.ref('tianv_attendance.attendance_type_leave')
        sick_tag = self.env.ref('tianv_attendance.attendance_type_sick')
        for record in self:
            record.legal_hour = record.plan.legal_hour
            record.min_hour = record.plan.min_hour
            record.holiday_date = record.plan.holiday_date
            record.late_time = len(record.lines.filtered(lambda line: late_tag in line.adjust_tags))
            record.early_time = len(record.lines.filtered(lambda line: early_tag in line.adjust_tags))
            record.absent_time = sum([l.plan_hour - l.adjust_hour for l in record.lines.filtered(lambda line: absent_tag in line.adjust_tags)])
            record.leave_time = sum([l.plan_hour - l.adjust_hour for l in record.lines.filtered(lambda line: leave_tag in line.adjust_tags)])
            record.sick_time = sum([l.plan_hour - l.adjust_hour for l in record.lines.filtered(lambda line: sick_tag in line.adjust_tags)])
            record.actual_hour = sum([l.adjust_hour for l in record.lines])
            record.plan_hour = sum([l.plan_hour for l in record.lines])
            record.employee = record.contract.employee_id

    @api.multi
    def button_generate_record(self):
        for record in self:
            # clean
            record.lines.unlink()
            # generate
            try:
                plan = self.env['tianv.hr.attendance.plan'].search([('period', '=', record.period.id)]).ensure_one()
                record.plan = plan
            except Exception:
                exceptions.Warning(_('Have no relative Attendance Plan or have Multi!'))
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

    plan_hour = fields.Float('Plan Hour', digits=(12, 1), compute='_compute_plan', readonly=True)
    record_hour = fields.Float('Record Hour', digits=(12, 1))
    tags = fields.Many2many('tianv.hr.attendance.record.type', 'attendance_record_tag_rel', 'record_id', 'tag_id', 'Tags')

    adjust_hour = fields.Float('Adjust Hour', digits=(12, 1), )
    adjust_tags = fields.Many2many('tianv.hr.attendance.record.type', 'attendance_record_adjust_tag_rel', 'record_id', 'tag_id', 'Adjust Tags')
    comment = fields.Char('Comment')
    plan_comment = fields.Char('Plan Comment', compute='_compute_plan', readonly=True)

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
                record.plan_comment = record.plan_line.comment

    @api.one
    def process_employee_attendance(self):
        absent_tag = self.env.ref('tianv_attendance.attendance_type_absent').id
        late_tag = self.env.ref('tianv_attendance.attendance_type_late').id
        early_tag = self.env.ref('tianv_attendance.attendance_type_early').id
        error_tag = self.env.ref('tianv_attendance.attendance_type_error').id
        leave_tag = self.env.ref('tianv_attendance.attendance_type_leave').id
        sick_tag = self.env.ref('tianv_attendance.attendance_type_sick').id
        year_tag = self.env.ref('tianv_attendance.attendance_type_year').id
        out_tag = self.env.ref('tianv_attendance.attendance_type_out').id

        leave_holiday = self.env.ref('tianv_attendance.holiday_status_personal').id
        sick_holiday = self.env.ref('tianv_attendance.holiday_status_sick').id
        year_holiday = self.env.ref('tianv_attendance.holiday_status_year').id
        out_holiday = self.env.ref('tianv_attendance.holiday_status_out').id

        normal = lambda p_in, p_out, c_start, c_end, conf: ((c_end - c_start).seconds / 3600.0, [])
        absent = lambda p_in, p_out, c_start, c_end, conf: (0, [absent_tag])
        early = lambda p_in, p_out, c_start, c_end, conf: (
            (p_out - c_start).seconds / 3600.0, [early_tag] if c_end > p_out and (c_end - p_out).seconds / 60.0 > conf.allow_early_minute else [])
        late = lambda p_in, p_out, c_start, c_end, conf: (
            (c_end - p_in).seconds / 3600.0, [late_tag] if p_in > c_start and (p_in - c_start).seconds / 60.0 > conf.allow_late_minute else [])
        error = lambda p_in, p_out, c_start, c_end, conf: (0, [error_tag])
        early_late = lambda p_in, p_out, c_start, c_end, conf: \
            (0, [error_tag]) if p_in == p_out else (
                (p_out - p_in).seconds / 3600.0, late(p_in, p_out, c_start, c_end, conf)[1] + early(p_in, p_out, c_start, c_end, conf)[1]
            )
        # 真值表
        true_table = {
            (False, False, False, False): normal,  # 1
            (False, False, False, True): normal,  # 2
            (False, False, True, False): normal,  # 3
            (False, False, True, True): normal,  # 4

            (False, True, False, False): absent,  # 5
            (False, True, False, True): early,  # 6
            (False, True, True, False): absent,  # 7
            (False, True, True, True): early,  # 8

            (True, False, False, False): absent,  # 9
            (True, False, False, True): absent,  # 10
            (True, False, True, False): late,  # 11
            (True, False, True, True): late,  # 12

            (True, True, False, False): absent,  # 13
            (True, True, False, True): absent,  # 14
            (True, True, True, False): error,  # 15 maybe normal?
            (True, True, True, True): early_late,  # 16
        }

        def process(need_punch_in, need_punch_out, punch_in, punch_out, config_start_t, config_end_t, current_config):
            key = (need_punch_in, need_punch_out, True if punch_in else False, True if punch_out else False)
            t_punch_in_time = datetime.datetime.strptime(punch_in, DEFAULT_SERVER_DATETIME_FORMAT) if punch_in else None
            t_punch_out_time = datetime.datetime.strptime(punch_out, DEFAULT_SERVER_DATETIME_FORMAT) if punch_out else None
            t_config_start_time = datetime.datetime.strptime(config_start_t, DEFAULT_SERVER_DATETIME_FORMAT) if config_start_t else None
            t_config_end_time = datetime.datetime.strptime(config_end_t, DEFAULT_SERVER_DATETIME_FORMAT) if config_end_t else None
            return true_table[key](t_punch_in_time, t_punch_out_time, t_config_start_time, t_config_end_time, current_config)

        plan = self.plan_line
        rule = self.record.contract.attendance_rule
        target_date = self.plan_date
        config = self.env['tianv.hr.attendance.config'].sudo().search(
            [('start_date', '<=', target_date), ('end_date', '>=', target_date)]).ensure_one()

        machine_obj = self.env['tianv.attendance.machine']

        record_hour = 0.0
        tag_ids = []

        for config_type in plan.config_types:
            rule_line = rule.lines.filtered(lambda l: l.type.id == config_type.id)
            config_line = config.lines.filtered(lambda l: l.type.id == config_type.id)
            if not config_line or not rule_line:
                raise exceptions.Warning(_('Fail to get type related config or rule '))

            punch_in_time = None
            punch_out_time = None
            config_start_time = self._utc_datetime(target_date, config_line.start_time)
            config_end_time = self._utc_datetime(target_date, config_line.end_time, 1 if config_line.is_cross_day else 0)
            # compute punch in
            punch_in_machine = machine_obj.search(
                [('log_employee', '=', self.record.employee.id),
                 ('log_time', '>=', self._utc_datetime(target_date, config_line.punch_begin_time)),
                 ('log_time', '<=', config_end_time)],
                order='log_time',
                limit=1)
            if punch_in_machine:
                punch_in_time = punch_in_machine.log_time
            # compute punch out
            punch_out_machine = machine_obj.search(
                [('log_employee', '=', self.record.employee.id),
                 ('log_time', '>=', config_start_time),
                 ('log_time', '<=', self._utc_datetime(target_date, config_line.punch_end_time, 1 if config_line.is_cross_day else 0))],
                order='log_time desc',
                limit=1)
            if punch_out_machine:
                punch_out_time = punch_out_machine.log_time

            (hour, tags) = process(rule_line.is_need_punch_in,
                                   rule_line.is_need_punch_out,
                                   punch_in_time,
                                   punch_out_time,
                                   config_start_time,
                                   config_end_time,
                                   config_line)

            # if is leave
            if self.env['hr.holidays'].search([
                ('employee_id', '=', self.record.employee.id),
                ('date_from', '<=', config_start_time),
                ('date_to', '>=', config_end_time),
                ('state', '=', 'validate'),
                ('holiday_status_id', '=', leave_holiday)]):
                (hour, tags) = (hour, [leave_tag])
            # if is sick
            elif self.env['hr.holidays'].search([
                ('employee_id', '=', self.record.employee.id),
                ('date_from', '<=', config_start_time),
                ('date_to', '>=', config_end_time),
                ('state', '=', 'validate'),
                ('holiday_status_id', '=', sick_holiday)]):

                (hour, tags) = (hour, [sick_tag])
            elif self.env['hr.holidays'].search([
                ('employee_id', '=', self.record.employee.id),
                ('date_from', '<=', config_start_time),
                ('date_to', '>=', config_end_time),
                ('state', '=', 'validate'),
                ('holiday_status_id', '=', year_holiday)]):
                (hour, tags) = (normal(None, None, datetime.datetime.strptime(config_start_time, DEFAULT_SERVER_DATETIME_FORMAT),
                                       datetime.datetime.strptime(config_end_time, DEFAULT_SERVER_DATETIME_FORMAT), None)[0], [year_tag])

            elif self.env['hr.holidays'].search([
                ('employee_id', '=', self.record.employee.id),
                ('date_from', '<=', config_start_time),
                ('date_to', '>=', config_end_time),
                ('state', '=', 'validate'),
                ('holiday_status_id', '=', out_holiday)]):
                (hour, tags) = (normal(None, None, datetime.datetime.strptime(config_start_time, DEFAULT_SERVER_DATETIME_FORMAT),
                                       datetime.datetime.strptime(config_end_time, DEFAULT_SERVER_DATETIME_FORMAT), None)[0], [out_tag])

            tag_ids += tags
            record_hour += hour

        tag_ids = list(set(tag_ids))
        values = {
            'record_hour': record_hour,
            'tags': [(6, 0, tag_ids)],
            'adjust_hour': record_hour,
            'adjust_tags': [(6, 0, tag_ids)],
        }
        self.write(values)

    @api.model
    def _utc_datetime(self, date, time, timedelta=0):
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
            return fields.Datetime.to_string(context_timestamp.astimezone(utc))
        return fields.Datetime.to_string(timestamp)

    @api.multi
    def button_get_machine_record(self):
        res = self.env['ir.actions.act_window'].for_xml_id('tianv_machine', 'action_attendance_machine')
        res['domain'] = [('log_time', '>=', self._utc_datetime(self.plan_date, 0)),
                         ('log_time', '<=', self._utc_datetime(self.plan_date, 0, 1)),
                         ('log_employee', '=', self.record.employee.id)]
        return res


class AttendanceRecordType(models.Model):
    _name = 'tianv.hr.attendance.record.type'
    _rec_name = 'name'
    _description = 'New Description'

    name = fields.Char('Name', required=True)
