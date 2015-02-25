# coding=utf-8
__author__ = 'cysnak4713'
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _


class SocialInsuranceConfig(models.Model):
    _name = 'tianv.social.insurance.config'
    _rec_name = 'computer_code'

    contract = fields.Many2one('hr.contract', 'Hr Contract')
    computer_code = fields.Char('Computer Code')
    census_type = fields.Selection([('city', u'市内城镇'), ('country', u'市外农村')], 'Census Type')
    lines = fields.One2many('tianv.social.insurance.line', 'config', 'Config Lines')

    personal_total = fields.Float('Personal Total', (10, 2), compute='_compute_total')
    company_total = fields.Float('Company Part', (10, 2), compute='_compute_total')
    total = fields.Float('Total', (10, 2), compute='_compute_total')

    active = fields.Boolean('Is Active')

    @api.multi
    def _compute_total(self):
        for config in self:
            personal_total = 0
            company_total = 0
            for line in config.lines:
                personal_total += line.personal_part
                company_total += line.company_part
            config.personal_total = personal_total
            config.company_total = company_total
            config.total = config.personal_total + config.company_total

    _defaults = {
        'active': True,
    }


class SocialInsuranceType(models.Model):
    _name = 'tianv.social.insurance.type'

    name = fields.Char('Name', required=True)

    _sql_constraints = [('social_insurance_type_name_unique', 'unique(name)', _('name must be unique !'))]


class SocialInsuranceLine(models.Model):
    _name = 'tianv.social.insurance.line'
    _rec_name = 'type'

    type = fields.Many2one('tianv.social.insurance.type', 'Insurance Type', required=True)
    company_part = fields.Float('Company Part', (10, 2))
    personal_part = fields.Float('Personal Part', (10, 2))
    config = fields.Many2one('tianv.social.insurance.config', 'Related Config')
