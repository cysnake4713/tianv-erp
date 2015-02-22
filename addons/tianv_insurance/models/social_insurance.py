__author__ = 'cysnak4713'

# coding=utf-8
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _


class SocialInsurance(models.Model):
    _name = 'tianv.social.insurance.type'

    name = fields.Char('Name', required=True)

    _sql_constraints = [('social_insurance_type_name_unique', 'unique(name)', _('name must be unique !'))]