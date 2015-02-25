__author__ = 'cysnak4713'
# coding=utf-8
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    social_insurance = fields.Many2one('tianv.social.insurance.config', 'Social Insurance', compute='_compute_social_insurance', readonly=True)

    @api.multi
    def _compute_social_insurance(self):
        for contract in self:
            social_insurance_id = self.env['tianv.social.insurance.config'].search([('contract', '=', contract.id), ('active', '=', True)])
            contract.social_insurance = social_insurance_id