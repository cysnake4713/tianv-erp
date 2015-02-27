__author__ = 'cysnak4713'

from openerp import http, SUPERUSER_ID
from openerp.http import request


class AttendanceMachineController(http.Controller):
    @http.route('/machine/import', type='json', auth='none')
    def import_data_from_machine(self, pwd, datas=None):
        password = request.registry('ir.config_parameter').get_param(request.cr, 1, 'tianv_machine.password')
        if pwd == password:
            result = request.registry['tianv.attendance.machine'].import_data_from_machine(request.cr, SUPERUSER_ID, datas, request.context)
            return result
        else:
            return False, 'password mismatch!'