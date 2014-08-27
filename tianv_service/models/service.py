# coding=utf-8
from openerp import models, fields

__author__ = 'cysnake4713'


class Service(models.Model):
    _name = "tianv.service.service"
    _description = "Service"
    _inherits = {'account.analytic.account': "analytic_account_id"}
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Contract/Analytic',
        help="Link this service to an analytic account if you need financial management on services. "
             "It enables you to connect services with budgets, planning, cost and revenue analysis, timesheets on services, etc.",
        ondelete="cascade", required=True, auto_join=True)

    product_id = fields.Many2one('product.product', string='Product')
    importance = fields.Selection(
        [('very_important', 'Very Important'), ('important', 'Important'), ('less_important', 'Less Important'), ('not_important', 'Not Important')],
        'Importance')
    # 账号个数
    account_number = fields.Integer('Account Number')
    # 服务大小
    service_size = fields.Integer('Service Size')
    # 服务价格
    service_price = fields.Float('Service Price', (10, 2))
    # 服务等级
    service_level = fields.Selection([('stand', 'Stand'), ('pro', 'Pro'), ('pro_iv', 'Pro IV')], 'Service Level')
    # 产品单位
    product_unit = fields.Selection([('MB', 'MB'), ('GB', 'GB'), ('year', 'Year')], 'Product Unit')
    #服务状态
    service_status = fields.Selection([('stop', 'Stop'), ('pause', 'Pause'), ('normal', 'Normal')], 'Service Status')
    #唯一标签
    identification = fields.Char('Identification')
    #服务密码
    password = fields.Char('Password')
    #服务端口
    port = fields.Integer('Port')
    #域名信息
    domain_info = fields.Char('Domain Info')
    #联系信息
    connect_info = fields.Char('Connect Info')
    #备注信息
    comment = fields.Text('Comment')

    _defaults = {
        'type': 'contract',
    }