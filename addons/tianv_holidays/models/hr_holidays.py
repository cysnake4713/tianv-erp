__author__ = 'cysnake4713'
# coding=utf-8
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _


class HrHolidaysInherit(models.Model):
    _inherit = 'hr.holidays'

    _defaults = {
        'date_from': lambda *o: fields.Date.today() + ' 01:00:00',
        'date_to': lambda *o: fields.Date.today() + ' 10:00:00',
    }