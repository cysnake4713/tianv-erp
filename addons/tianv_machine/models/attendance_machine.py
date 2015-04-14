# coding=utf-8
__author__ = 'cysnak4713'
import json
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
# import xmlrpclib
import logging

_logger = logging.getLogger(__name__)
# noinspection PyUnresolvedReferences
class AttendanceMachine(models.Model):
    _name = 'tianv.attendance.machine'
    _rec_name = 'log_time'

    _order = 'log_time desc, code desc, id desc'

    log_time = fields.Datetime('Log Time', required=True)
    log_employee = fields.Many2one('hr.employee', 'Log Employee')

    user_id = fields.Integer('Machine User ID', required=True)
    user_true_name = fields.Char('Machine User True Name', required=True)

    code = fields.Integer('Identify ID', required=True, )

    _sql_constraints = [('attendance_machine_code_unique', 'unique(code)', _('code must be unique !'))]

    @api.model
    def import_data_from_machine(self, json_datas):
        datas = json.loads(json_datas)
        if self.user_has_groups('tianv_machine.group_attendance_machine_upload'):
            self.sudo().env.cr.execute('SAVEPOINT import')
            employees = {u.name: u.id for u in self.sudo().env['hr.employee'].search([])}
            result = True
            error_string = ''
            for data in datas:
                try:
                    self.sudo().match_user(employees, data)
                    self.sudo().create(data)
                except Exception, e:
                    _logger.error('Import machine record error.', e)
                    result = False
                    error_string = str(e)
                    break
            else:
                self.sudo().env.cr.execute('RELEASE SAVEPOINT import')
                self.sudo().env['tianv.attendance.machine.log'].create({'is_success': True})
                return result

            self.sudo().env.cr.execute('ROLLBACK TO SAVEPOINT import')
            self.sudo().env['tianv.attendance.machine.log'].create({'is_success': False}, error_string)
            return result
        else:
            return False

    @api.model
    def get_last_update_info(self):
        if self.user_has_groups('tianv_machine.group_attendance_machine_upload'):
            last_import_datetime = self.sudo().env['tianv.attendance.machine.log'].search([('is_success', '=', True)], order='import_datetime desc',
                                                                                          limit=1)
            last_import_datetime = last_import_datetime[0].import_datetime if last_import_datetime else None
            last_import_datetime = fields.Datetime.to_string(
                fields.Datetime.context_timestamp(self, fields.Datetime.from_string(last_import_datetime))) if last_import_datetime else False
            last_code = self.sudo().search([], order='code desc', limit=1)
            last_code = last_code[0].code if last_code else False
            return last_code, last_import_datetime
        else:
            return False

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
    error_info = fields.Text('Error Info')

    _defaults = {
        'import_datetime': lambda *args: fields.Datetime.now(),
        'is_success': True,
    }


    # if __name__ == '__main__':
    # username = 'machine'  # the user
    # pwd = 'machine'  # the password of the user
    # dbname = 'tianv-erp'  # the database
    #     OPENERP_URL = 'localhost:8069'
    #
    #     sock_common = xmlrpclib.ServerProxy('http://' + OPENERP_URL + '/xmlrpc/common')
    #     uid = sock_common.login(dbname, username, pwd)
    #     sock = xmlrpclib.ServerProxy('http://' + OPENERP_URL + '/xmlrpc/object')
    #
    #     print sock.execute(dbname, uid, pwd, 'tianv.attendance.machine', 'get_last_update_info')
    #
    #     datas = [
    #         {
    #             "log_time": "2014-02-11 12:22:10",
    #             "code": 10,
    #             "user_id": 1,
    #             "user_true_name": "符为"
    #         },
    #         {
    #             "log_time": "2014-02-12 12:22:10",
    #             "code": 11,
    #             "user_id": 1,
    #             "user_true_name": "符为"
    #         }
    #     ]
    #
    #     print sock.execute(dbname, uid, pwd, 'tianv.attendance.machine', 'import_data_from_machine', datas)