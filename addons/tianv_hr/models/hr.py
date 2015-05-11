__author__ = 'cysnake4713'
# coding=utf-8
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _


class EmployeeInherit(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    residence_address = fields.Char('Residence Address')

