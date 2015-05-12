__author__ = 'cysnake4713'
# coding=utf-8
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _


class EmployeeInherit(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    residence_address = fields.Char('Residence Address')

    nationality = fields.Char('Nationality')
    school = fields.Char('School')
    educational = fields.Char('Educational Background')
    major = fields.Char('Major')
    language_skill = fields.Char('Language Skill')
    basic_english = fields.Char('Basic English')
    qq_id = fields.Char('QQ')
    wechat_id = fields.Char('Wechat')
    person_mail = fields.Char('Personal Mail')
    family_members = fields.Char('Family Members')

    attachments = fields.Many2many('ir.attachment', 'employee_attachment_rel', 'employee_id', 'attachment_id', 'Attachments')