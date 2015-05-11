__author__ = 'cysnake4713'
# coding=utf-8
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _


class ContractInherit(models.Model):
    _inherit = 'hr.contract'

    work_info = fields.Char('Work Info')
    contract_wage = fields.Float('Contract Wage')

