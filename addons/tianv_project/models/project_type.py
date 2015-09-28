# -*- coding: utf-8 -*-
# author: cysnake4713
#
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _


class ProjectDeductType(models.Model):
    _name = 'tianv.project.deduct.type'
    _rec_name = 'name'
    _description = 'Project Deduct Type'

    name = fields.Char('Name', required=True)


