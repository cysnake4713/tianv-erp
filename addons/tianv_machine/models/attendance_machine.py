__author__ = 'cysnak4713'

# coding=utf-8
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


class AttendanceMachine(models.Model):
    _name = 'tianv.attendance.machine'
    _rec_name = 'log_time'

    _order = 'log_time desc, code desc, id desc'

    log_time = fields.Datetime('Log Time', required=True)
    log_employee = fields.Many2one('hr.employee', 'Log Employee')

    user_id = fields.Integer('Machine User ID', required=True)
    user_true_name = fields.Char('Machine User True Name', required=True)

    code = fields.Integer('Identify ID', required=True)

    @api.model
    def import_data_from_machine(self, datas):
        self.env.cr.execute('SAVEPOINT import')
        employees = {u.name: u.id for u in self.env['hr.employee'].search([])}
        result = True, ''
        for data in datas:
            try:
                self.match_user(employees, data)
                self.create(data)
            except Exception, e:
                _logger.error('Import attendance machine error!', e)
                result = False, e.message
                break
        else:
            self.env.cr.execute('RELEASE SAVEPOINT import')
            self.env['tianv.attendance.machine.log'].create({'is_success': True})
            return result

        self.env.cr.execute('ROLLBACK TO SAVEPOINT import')
        self.env['tianv.attendance.machine.log'].create({'is_success': False})
        return result

    @api.model
    def match_user(self, employees, data):
        if 'user_true_name' in data and data['user_true_name'] in employees:
            data['log_employee'] = employees[data['user_true_name']]


class AttendanceImportLog(models.Model):
    _name = 'tianv.attendance.machine.log'

    _rec_name = 'import_datetime'
    _order = 'import_datetime desc'

    import_datetime = fields.Datetime('Import Datetime')
    is_success = fields.Boolean('Is Success')

    _defaults = {
        'import_datetime': lambda *args: fields.Datetime.now(),
        'is_success': True,
    }



