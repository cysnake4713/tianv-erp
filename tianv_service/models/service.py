# coding=utf-8
from openerp import models, fields, api

__author__ = 'cysnake4713'


class Service(models.Model):
    _name = "tianv.service.service"
    _description = "Service"
    _inherits = {'account.analytic.account': "analytic_account_id"}
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _status_selection = [('normal', 'Normal'), ('pause', 'Pause'), ('stop', 'Stop')]
    _service_level_selection = [('stand', u'标准I型'), ('pro', u'专业I型'), ('pro_iv', u'专业IV型')]
    _product_unit_selection = [('MB', 'MB'), ('GB', 'GB'), ('year', u'年')]
    _importance_selection = [('very_important', 'Very Important'), ('important', 'Important'), ('less_important', 'Less Important'),
                             ('not_important', 'Not Important')]

    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Contract/Analytic',
        help="Link this service to an analytic account if you need financial management on services. "
             "It enables you to connect services with budgets, planning, cost and revenue analysis, timesheets on services, etc.",
        ondelete="cascade", required=True, auto_join=True)

    product_id = fields.Many2one('product.product', string='Product')
    importance = fields.Selection(_importance_selection, 'Importance')
    # 账号个数
    account_number = fields.Integer('Account Number')
    # 服务大小
    product_size = fields.Integer('Product Size')
    # 服务价格
    product_price = fields.Float('Product Price', (10, 2))
    # 服务等级
    service_level = fields.Selection(_service_level_selection, 'Service Level')
    # 产品单位
    product_unit = fields.Selection(_product_unit_selection, 'Product Unit')
    # 服务状态
    service_status = fields.Selection(_status_selection, 'Service Status')
    service_status_function = fields.Selection(_status_selection, string='Service Status Function', compute='_compute_service_status')
    # 唯一标签
    identification = fields.Char('Identification')
    # 服务密码
    password = fields.Char('Password')
    # 服务端口
    port = fields.Integer('Port')
    # 域名信息
    domain_info = fields.Char('Domain Info')
    # 联系信息
    connect_info = fields.Char('Connect Info')
    # 备注信息
    comment = fields.Text('Comment')

    _defaults = {
        'type': 'contract',
        'service_status': 'normal',
    }

    @api.one
    @api.depends('service_status')
    def _compute_service_status(self):
        self.service_status_function = self.service_status

    @api.one
    @api.onchange('service_level', 'product_size', 'product_unit', 'product_id')
    def _onchange_name(self):
        name = [
            dict(self._service_level_selection)[self.service_level] if self.service_level else '',
            str(self.product_size or 0),
            dict(self._product_unit_selection)[self.product_unit] if self.product_unit else '',
            self.product_id.name if self.product_id else '',
            self.product_id.categ_id.name if self.product_id and self.product_id.categ_id else ''
        ]
        self.name = ''.join(name)
