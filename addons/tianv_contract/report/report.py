# coding=utf-8
from openerp.report import report_sxw

__author__ = 'cysnake4713'
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _
from datetime import date


class ContractTrial(report_sxw.rml_parse):
    def set_context(self, objects, data, ids, report_type=None):
        def format_date(n_date):
            return fields.Date.from_string(n_date)

        self.localcontext.update({
            'object': self.pool['hr.contract'].browse(self.cr, self.uid, ids[0], context=self.localcontext),
            'format_date': format_date,

        })
        return super(ContractTrial, self).set_context(objects, data, ids, report_type=report_type)


class ReportTimetable(models.AbstractModel):
    _name = 'report.tianv_contract.report_doc_contract'
    _inherit = 'report.abstract_report'
    _template = 'tianv_contract.report_doc_contract'
    _wrapped_report_class = ContractTrial


class ReportContract(models.AbstractModel):
    _name = 'report.tianv_contract.report_doc_contract_trial'
    _inherit = 'report.abstract_report'
    _template = 'tianv_contract.report_doc_contract_trial'
    _wrapped_report_class = ContractTrial