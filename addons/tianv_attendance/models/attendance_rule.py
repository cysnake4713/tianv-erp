__author__ = 'cysnake4713'
# coding=utf-8
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _


class AttendanceRule(models.Model):
    _name = 'tianv.hr.attendance.rule'
    _rec_name = 'name'
    _description = 'Tianv Attendance Rule'

    name = fields.Char('Name', required=True)

    lines = fields.One2many('tianv.hr.attendance.rule.line', 'rule', 'Rule Lines')
    is_need_attendance = fields.Boolean('Is Need attendance', compute='_compute_is_need_attendance')

    @api.multi
    def _compute_is_need_attendance(self):
        result = False
        for line in self.lines:
            if line.is_need_punch_in or line.is_need_punch_out:
                result = True
                break
        return result


class AttendanceRuleLine(models.Model):
    _name = 'tianv.hr.attendance.rule.line'
    _rec_name = 'type'
    _description = 'Tianv Attendance Rule'

    rule = fields.Many2one('tianv.hr.attendance.rule', 'Relative Rule', required=True, ondelete='cascade')
    type = fields.Many2one('tianv.hr.attendance.config.type', 'Type', required=True)
    is_need_punch_in = fields.Boolean('Need Punch In')
    is_need_punch_out = fields.Boolean('Need Punch Out')


class HrContractInherit(models.Model):
    _inherit = 'hr.contract'

    attendance_rule = fields.Many2one('tianv.hr.attendance.rule', 'Attendance Rule', required=True)