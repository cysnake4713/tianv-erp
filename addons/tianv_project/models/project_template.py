# -*- coding: utf-8 -*-
# author: cysnake4713
#
from project import PRICE_DIGITS
from openerp import tools, exceptions
from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval


class ProjectTemplate(models.Model):
    _name = 'tianv.project.template'
    _rec_name = 'name'
    _description = 'Tianv Project Template'

    name = fields.Char('Name', required=True)

    param_ids = fields.One2many('tianv.project.template.param', 'template_id', 'Params')

    line_ids = fields.One2many('tianv.project.template.line', 'template_id', 'Lines')

    @api.multi
    def button_test_available(self):
        for template in self:
            custom_context = {
                'TOTAL': 0,
                'ACTUAL_TOTAL': 0,
            }
            for param in template.param_ids:
                custom_context[param.code] = 0
            error = ''
            for line in template.line_ids:
                try:
                    line.compute_price(custom_context)
                except Exception, e:
                    error += u'序列:%s 名称:%s ---> %s' % (line.sequence, line.name, e.message)
            message = error if error else u'测试通过'
            return {
                'type': 'ir.actions.act_window.message',
                'title': _('测试结果'),
                'message': message,
            }


class ProjectTemplateParam(models.Model):
    _name = 'tianv.project.template.param'
    _rec_name = 'name'
    _description = 'Tianv Project Template Param'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    default_proportion = fields.Float('Default Proportion', PRICE_DIGITS)
    default_value = fields.Float('Default_value', PRICE_DIGITS)
    template_id = fields.Many2one('tianv.project.template', 'Related Template', ondelete='cascade')


class ProjectTemplateLine(models.Model):
    _name = 'tianv.project.template.line'
    _rec_name = 'name'
    _order = 'sequence'
    _description = 'Tianv Project Template Line'

    sequence = fields.Integer('Sequence', default=1)
    name = fields.Char('Name', required=True)
    type_id = fields.Many2one('tianv.project.deduct.type', 'Type', required=True)
    python_code = fields.Text('Python Code')
    template_id = fields.Many2one('tianv.project.template', 'Related Template', ondelete='cascade')

    @api.multi
    def compute_price(self, custom_context):
        context = {
            'RESULT': 0,
        }
        context.update(custom_context)
        for line in self:
            if line.python_code:
                eval(line.python_code, context, mode="exec", nocopy=True)
        return context['RESULT']
