# coding=utf-8
from openerp.report import report_sxw

__author__ = 'cysnake4713'
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _


class DocTransform(report_sxw.rml_parse):
    def set_context(self, objects, data, ids, report_type=None):

        self.localcontext.update({
            'object': self.pool['hr.contract'].browse(self.cr, self.uid, ids[0], context=self.localcontext),

        })
        return super(DocTransform, self).set_context(objects, data, ids, report_type=report_type)


class ReportTimetable(models.AbstractModel):
    _name = 'report.tianv_contract.report_doc_contract'
    _inherit = 'report.abstract_report'
    _template = 'tianv_contract.report_doc_contract'
    _wrapped_report_class = DocTransform
