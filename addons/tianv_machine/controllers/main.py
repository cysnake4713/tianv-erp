__author__ = 'cysnak4713'

from openerp import http
from openerp.http import request


class AttendanceMachineController(http.Controller):
    @http.route('/machine/import', type='json', auth='none')
    def import_data_from_machine(self, pwd, datas=None):
        password = request.registry('ir.config_parameter').get_param(request.cr, 1, 'tianv_machine.password')
        if pwd == password:
            result = request.registry['tianv.attendance.machine'].import_data_from_machine(request.cr, 1, datas, request.context)
            if result:
                return True
            else:
                return False
        else:
            return False