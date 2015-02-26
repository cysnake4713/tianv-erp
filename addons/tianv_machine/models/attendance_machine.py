__author__ = 'cysnak4713'

# coding=utf-8
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _


class AttendanceMachine(models.Model):
    _name = 'tianv.attendance.machine'
    _rec_name = 'log_time'

    _order = 'log_time desc'

    log_time = fields.Datetime('Log Time')
    log_employee = fields.Many2one('hr.employee', 'Log Employee')

    user_id = fields.Integer('Machine User ID')
    user_true_name = fields.Char('Machine User True Name')

    code = fields.Integer('Identify ID')



