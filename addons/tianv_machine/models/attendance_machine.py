__author__ = 'cysnak4713'

# coding=utf-8
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _
import logging

_logger = logging.getLogger(__name__)


class AttendanceMachine(models.Model):
    _name = 'tianv.attendance.machine'
    _rec_name = 'log_time'

    _order = 'log_time desc'

    log_time = fields.Datetime('Log Time')
    log_employee = fields.Many2one('hr.employee', 'Log Employee')

    user_id = fields.Integer('Machine User ID')
    user_true_name = fields.Char('Machine User True Name')

    code = fields.Integer('Identify ID')

    def import_data_from_machine(self, cr, uid, datas, context=None):
        cr.execute('SAVEPOINT import')
        for data in datas:
            try:
                self.create(cr, uid, data, context=context)
            except Exception, e:
                _logger.error('Import attendance machine error!', e)
                break
        else:
            cr.execute('RELEASE SAVEPOINT import')
            self.pool['tianv.attendance.machine.log'].create(cr, uid, {'is_success': True}, context=context)
            return True

        cr.execute('ROLLBACK TO SAVEPOINT import')
        self.pool['tianv.attendance.machine.log'].create(cr, uid, {'is_success': False}, context=context)
        return False


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



