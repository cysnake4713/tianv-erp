# coding=utf-8
__author__ = 'cysnake4713'
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _


class AttendanceConfig(models.Model):
    _name = 'tianv.hr.attendance.config'
    _description = 'Attendance Timetable Config'

    start_date = fields.Date('Start Date', required=True, default=lambda *args: fields.Date.today())
    end_date = fields.Date('End Date', required=True, default=lambda *args: fields.Date.today())

    allow_late_time = fields.Integer('Allow Late Time')
    allow_early_time = fields.Integer('Allow Early Time')
    # 请假
    allow_leave_time = fields.Integer('Allow Leave Time')

    lines = fields.One2many('tianv.hr.attendance.config.line', 'config', 'Config Lines')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = u'%s ~ %s'
            result.append((record.id, name % (record.start_date, record.end_date)))
        return result

    @api.one
    @api.constrains('start_date', 'end_date')
    def _check_contract(self):
        if self.end_date < self.start_date:
            raise Warning(_('End Date must after Start Date'))

    @api.model
    def get_type_work_time(self, current_date, config_type):
        config = self.search([('start_date', '<=', current_date), ('end_date', '>=', current_date)])
        line = config.lines.filtered(lambda l: l.type.id == config_type.id)
        if line:
            return line.work_time
        else:
            return 0.0


class AttendanceConfigLine(models.Model):
    _name = 'tianv.hr.attendance.config.line'
    _rec_name = 'type'
    _description = 'Attendance Timetable Config Line'

    config = fields.Many2one('tianv.hr.attendance.config', 'Config', required=True, ondelete='cascade')
    type = fields.Many2one('tianv.hr.attendance.config.type', 'Type', required=True)

    start_time = fields.Float('Start Time', required=True)
    end_time = fields.Float('End Time', required=True)
    allow_late_minute = fields.Integer('Allow Late Minute', required=True)
    allow_early_minute = fields.Integer('Allow Early Minute', required=True)

    punch_begin_time = fields.Float('Punch Begin Time', required=True)
    punch_end_time = fields.Float('End Punch End Time', required=True)

    is_cross_day = fields.Boolean('Is Cross Day')

    work_time = fields.Float('Work Time(h)', digits=(12, 1), compute='_compute_work_time')

    @api.multi
    def _compute_work_time(self):
        for line in self:
            line.work_time = (line.end_time - line.start_time)


class AttendanceConfigType(models.Model):
    _name = 'tianv.hr.attendance.config.type'
    _rec_name = 'name'
    _description = 'Attendance Timetable Config Type'

    name = fields.Char('Name', required=True)


