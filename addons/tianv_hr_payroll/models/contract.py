__author__ = 'cysnake4713'

# coding=utf-8
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    job = fields.Many2one('hr.contract.job', 'Job', required=True)
    skill = fields.Many2one('hr.contract.skill', 'Skill', required=True)

    @api.multi
    def get_insurance_record_by_date(self, date_start, date_end):
        try:
            return self.social_insurance.records.filtered(lambda r: r.period.date_start <= date_start and r.period.date_stop >= date_end).ensure_one()
        except Exception:
            raise exceptions.Warning(_("can't find insurance record in period or have multi record for on peroid"))

    @api.multi
    def get_attendance_record_by_date(self, date_start, date_end):
        try:
            period = self.env['account.period'].search([('date_start', '<=', date_start), ('date_stop', '=', date_end)]).ensure_one()
            return self.env['tianv.hr.attendance.record'].search([('period', '=', period.id), ('contract', '=', self.id)]).ensure_one()
        except Exception:
            raise exceptions.Warning(_("can't find insurance record in period or have multi record for on peroid"))


class HrContractJob(models.Model):
    _name = 'hr.contract.job'

    name = fields.Char('Name', required=True)
    coefficient = fields.Float('coefficient', required=True)


class HrContractSkill(models.Model):
    _name = 'hr.contract.skill'

    name = fields.Char('Name', required=True)
    coefficient = fields.Float('coefficient', required=True)
