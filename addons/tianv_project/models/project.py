# -*- coding: utf-8 -*-
# author: cysnake4713
#
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _

PRICE_DIGITS = (10, 2)


class ProjectTemplate(models.Model):
    _name = 'tianv.project.template'
    _rec_name = 'name'
    _description = 'Tianv Project Template'

    name = fields.Char('Name', required=True)

    param_ids = fields.One2many('tianv.project.template.param', 'template_id', 'Params')

    line_ids = fields.One2many('tianv.project.template.line', 'template_id', 'Lines')


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


class ProjectProject(models.Model):
    _name = 'tianv.project.project'
    _rec_name = 'name'
    _description = 'Tianv Project'

    name = fields.Char('Name', required=True)
    # 状态
    state = fields.Selection([('draft', 'Draft'),
                              ('processing', 'Processing'),
                              ('finish', 'Finish'),
                              ('canceled', 'Canceled'),
                              ('pause', 'Pause'), ],
                             'State', default='draft')
    # 客户公司
    partner_id = fields.Many2one('res.partner', 'Custom Company', required=True, domain=[('customer', '=', True), ('is_company', '=', True)])
    # 合同编号
    code = fields.Char('Code', required=True)
    # 产品
    product_id = fields.Many2one('product.product', 'Product', required=True)
    # 签约日期
    sign_date = fields.Date('Sign Date')
    # 相关订单
    order_id = fields.Many2one('sale.order', 'Res Order')
    # 计划完成日期
    plan_finish_date = fields.Date('Plan Finish Date')
    # 实际完成日期
    actual_finish_date = fields.Date('Actual Finish Date')
    # 使用的模板
    template_id = fields.Many2one('tianv.project.template', 'Res Template')
    # 合同金额
    contract_price = fields.Float('Contract Price', PRICE_DIGITS)
    # 税
    tax_id = fields.Many2one('account.tax', 'Tax')
    # 实际金额
    actual_price = fields.Float('Actual Price', PRICE_DIGITS, compute='_compute_actual_price')

    param_ids = fields.One2many('tianv.project.project.param', 'project_id', 'Params')

    record_ids = fields.One2many('tianv.project.project.record', 'project_id', 'Records')

    @api.multi
    @api.depends('contract_price', 'tax_id')
    def _compute_actual_price(self):
        for project in self:
            project.actual_price = project.tax_id.compute_all(project.contract_price, 1)['total']


class ProjectProjectParam(models.Model):
    _name = 'tianv.project.project.param'
    _rec_name = 'template_param_id'
    _description = 'Tianv Project Param'

    template_param_id = fields.Many2one('tianv.project.template.param', 'Related template Param', required=True)
    code = fields.Char('Code', related='template_param_id.code', readonly=True)
    price = fields.Float('Price', PRICE_DIGITS)
    project_id = fields.Many2one('tianv.project.project', 'Related Project', ondelete='cascade')
    project_template_id = fields.Many2one('tianv.project.template', 'Project Template')


class ProjectProjectRecord(models.Model):
    _name = 'tianv.project.project.record'
    _rec_name = 'name'
    _description = 'Tianv Project Record'

    name = fields.Char('Name', required=True)
    template_line_id = fields.Many2one('tianv.project.template.line', 'Related Template Line')
    type_id = fields.Many2one('tianv.project.deduct.type', 'Type', required=True)
    price = fields.Float('Price', PRICE_DIGITS)
    comment = fields.Text('Comment')
    user_id = fields.Many2one('res.partner', 'Partner', required=True)
    project_id = fields.Many2one('tianv.project.project', 'Related Project', required=True)
