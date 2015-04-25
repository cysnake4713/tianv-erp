__author__ = 'cysnake4713'

# coding=utf-8
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    job = fields.Many2one('hr.contract.job', 'Job', required=True)
    skill = fields.Many2one('hr.contract.skill', 'Skill', required=True)


class HrContractJob(models.Model):
    _name = 'hr.contract.job'

    name = fields.Char('Name', required=True)
    coefficient = fields.Float('coefficient', required=True)


class HrContractSkill(models.Model):
    _name = 'hr.contract.skill'

    name = fields.Char('Name', required=True)
    coefficient = fields.Float('coefficient', required=True)
