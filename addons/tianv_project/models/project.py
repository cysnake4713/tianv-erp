# -*- coding: utf-8 -*-
# author: cysnake4713
#
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _

PRICE_DIGITS = (10, 2)


class ProjectProject(models.Model):
    _name = 'tianv.project.project'
    _rec_name = 'name'
    _description = 'Tianv Project'
    _inherit = 'odoosoft.workflow.abstract'
    _order = 'id desc'

    name = fields.Char('Name', required=True)
    # 状态
    state = fields.Selection([('draft', 'Draft'),
                              ('processing', 'Processing'),
                              ('finished', 'Finished'),
                              ('canceled', 'Canceled'),
                              ('pause', 'Pause'), ],
                             'State', default='draft', track_visibility='onchange')
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
    # 含税金额
    tax_price = fields.Float('Tax Price', PRICE_DIGITS, compute='_compute_actual_price')

    param_ids = fields.One2many('tianv.project.project.param', 'project_id', 'Params')

    record_ids = fields.One2many('tianv.project.project.record', 'project_id', 'Records')

    @api.multi
    @api.depends('contract_price', 'tax_id')
    def _compute_actual_price(self):
        for project in self:
            project.actual_price = project.tax_id.compute_all(project.contract_price, 1)['total']
            project.tax_price = project.tax_id.compute_all(project.contract_price, 1)['total_included']

    @api.multi
    def button_init_template(self):
        for project in self:
            if project.template_id:
                # clear current param
                project.param_ids.unlink()
                # update project param
                for param in project.template_id.param_ids:
                    value = {
                        'code': param.code,
                        'name': param.name,
                        'project_id': project.id,
                    }
                    if param.default_proportion:
                        value['price'] = (project.tax_price if param.is_tax else project.actual_price) * param.default_proportion
                    elif param.default_value and param.default_value < project.actual_price:
                        value['price'] = param.default_value
                    self.env['tianv.project.project.param'].create(value)
                # clear current record
                project.record_ids.unlink()
                # update record
                for line in project.template_id.line_ids:
                    value = {
                        'name': line.name,
                        'template_line_id': line.id,
                        'type_id': line.type_id.id,
                        'project_id': project.id,
                    }
                    self.env['tianv.project.project.record'].create(value)
                    # self.button_compute_record()

    @api.multi
    def get_custom_context(self):
        custom_context = {
            'TOTAL': self.tax_price,
            'ACTUAL_TOTAL': self.actual_price,
        }
        for param in self.template_id.param_ids:
            custom_context[param.code] = 0
        for param in self.param_ids:
            custom_context[param.code] = param.price
        return custom_context

    @api.multi
    def button_compute_record(self):
        for project in self:
            project.record_ids.with_context(custom_context=project.get_custom_context()).button_compute_value()

    @api.multi
    def button_start_process(self):
        for project in self.sudo():
            for record in project.record_ids:
                if record.state == 'processing':
                    record.button_resend_message()
            project.common_apply()

    @api.multi
    def button_reset_draft(self):
        # for project in self:
        #     project.record_ids.button_reset_draft()
        project.common_reject()


class ProjectProjectParam(models.Model):
    _name = 'tianv.project.project.param'
    _rec_name = 'name'
    _description = 'Tianv Project Param'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    price = fields.Float('Price', PRICE_DIGITS)
    project_id = fields.Many2one('tianv.project.project', 'Related Project', ondelete='cascade')


class ProjectProjectRecord(models.Model):
    _name = 'tianv.project.project.record'
    _inherit = 'odoosoft.workflow.abstract'
    _rec_name = 'name'
    _description = 'Tianv Project Record'

    state = fields.Selection(
        [('draft', 'Draft'), ('processing', 'Processing'), ('review', 'Review'), ('finished', 'Finished'), ('cancel', 'Cancel'), ('pause', 'Pause')],
        'State', default='draft', track_visibility='onchange')
    name = fields.Char('Name', required=True)
    template_line_id = fields.Many2one('tianv.project.template.line', 'Related Template Line')
    type_id = fields.Many2one('tianv.project.deduct.type', 'Type', required=True)
    price = fields.Float('Price', PRICE_DIGITS)
    comment = fields.Text('Comment')
    adjustment = fields.Float('Adjustment', PRICE_DIGITS, default=1)
    partner_id = fields.Many2one('res.partner', 'Partner')
    user_id = fields.Many2one('res.users', 'User', compute='_compute_user')
    project_id = fields.Many2one('tianv.project.project', 'Related Project', required=True)
    plan_finish_date = fields.Date('Plan Finish Date')
    finish_date = fields.Date('Finish Date')
    move_id = fields.Many2one('account.move')
    partner_finish_date = fields.Datetime('Partner Finish Date')

    @api.multi
    @api.depends('partner_id')
    def _compute_user(self):
        for record in self:
            partner_id = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
            record.user_id = partner_id[0] if partner_id else False

    @api.multi
    def button_compute_value(self):
        custom_context = self.env.context['custom_context'] if self.env.context.get('custom_context', False) else self.project_id.get_custom_context()
        for record in self:
            if record.template_line_id:
                record.price = record.template_line_id.compute_price(custom_context) * record.adjustment

    @api.multi
    def button_start_task(self):
        record = self
        record.with_context(state='processing',
                            message_users=[record.user_id.id] if record.user_id else [],
                            message=u'项目已经启动',
                            wechat_code=['tianv.project.project'],
                            wechat_template=self.env.ref('tianv_project.message_project_record').id,
                            ).common_apply()
        if record.type_id.commission_type == 'account':
            record.move_id = self.sudo().env['account.move'].create({
                'journal_id': record.type_id.journal_id.id,
                'date': record.project_id.sign_date or fields.Date.today(),
                'period_id': self.env['account.period'].find(dt=record.project_id.sign_date).id,
                'line_id': [(0, 0, {'name': record.name, 'account_id': record.type_id.debit_account_id.id, 'debit': record.price,
                                    'partner_id': record.partner_id.id}),
                            (0, 0, {'name': record.name, 'account_id': record.type_id.credit_account_id.id, 'credit': record.price,
                                    'partner_id': record.partner_id.id}),
                            ]
            })

    @api.multi
    def button_review_apply(self):
        for record in self:
            if not record.finish_date:
                record.finish_date = fields.Date.today()
        self.common_apply()

    @api.multi
    def button_reset_draft(self):
        for record in self:
            record.move_id.unlink()
        self.with_context(state='draft').common_apply()

    @api.multi
    def button_finished_apply(self):
        if not self.partner_finish_date:
            self.partner_finish_date = fields.Datetime.now()
        self.common_apply()

    @api.multi
    def button_resend_message(self):
        self.with_context(message_users=[self.user_id.id] if self.user_id else [],
                          message=u'任务已经启动',
                          wechat_code=['tianv.project.project'],
                          wechat_template=self.env.ref('tianv_project.message_project_record').id,
                          ).common_apply()

    @api.multi
    def button_act_window(self):
        res = self.env.ref('tianv_project.action_project_record').read()[0]
        res['view_mode'] = 'form'
        res['res_id'] = self.id
        res['target'] = 'new'
        del res['view_ids'], res['views']
        return res

    @api.model
    def cron_send_plan_warning(self):
        records = self.search([('state', '=', 'processing'), ('plan_finish_date', '<', fields.Date.today())])
        for record in records:
            record.with_context(message_users=[record.user_id.id] if record.user_id else [],
                                message=u'任务已超过计划完成时间，请尽快处理',
                                wechat_code=['tianv.project.project'],
                                wechat_template=self.env.ref('tianv_project.message_project_record').id,
                                ).common_apply()
        return True


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.model
    def get_commission(self, employee, commission_code, date_from, date_to):
        result = 0.0
        if employee and employee.user_id:
            records = self.sudo().env['tianv.project.project.record'].search(
                [('partner_id', '=', employee.user_id.partner_id.id), ('partner_finish_date', '>=', date_from), ('partner_finish_date', '<=', date_to),
                 ('type_id.commission_type', '=', 'employee'), ('type_id.commission_code', '=', commission_code),
                 ('state', '=', 'finished')])
            result = sum([r.price for r in records])
        return result
