# coding=utf-8
from openerp import fields, api, models
from openerp.tools.translate import _

__author__ = 'cysnake4713'


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    number = fields.Char('Partner Number', size=128)
    # 公司类型
    company_type = fields.Many2one('res.partner.company.type', 'Company Type')
    # 主营类别
    main_category = fields.Many2one('res.partner.main.category', 'Main Category')
    # 产品类别
    product_category = fields.Many2one('res.partner.product.category', 'Product Category')
    # 行业类别
    sector = fields.Many2one('res.partner.sector', 'Sector')
    # 年收入额
    annual_income = fields.Many2one('res.partner.annual.income', 'Annual Income')
    # 注册资本
    registered_capital = fields.Many2one('res.partner.registered.capital', 'Registered Capital')
    # 营业执照
    business_license = fields.Char('Business License', size=64)
    # 企业规模
    scale = fields.Many2one('res.partner.scale', 'Scale')
    # 法定代表
    legal = fields.Many2one('res.partner', 'Legal')
    # 成立时间
    founded_date = fields.Date('Founded Date')

    # QQ & MSN
    qq = fields.Char('QQ & MSN', size=32)
    # 兴趣爱好
    hobby = fields.Char('Hobby', size=64)

    # 客户分类
    classification = fields.Selection(
        selection=[('common', 'Common Client'), ('partner', 'Partner'), ('proxy', 'Proxy Client'), ('suppler', 'Suppler'), ('else', 'Else')],
        string='Classification')
    # 客户来源
    source = fields.Many2one('res.partner.source', 'Source')
    # 客户类型
    customer_type = fields.Many2one('res.partner.customer.type', 'Type')
    # 热点客户
    hot = fields.Boolean('Hot Client')
    # 兴趣产品
    interest_product = fields.Many2many('res.partner.interest.product', 'rel_partner_interest_product', 'partner_id', 'interest_id',
                                        'Interest Product')
    # 登记时间
    create_date = fields.Datetime('Create Date')
    # 客户状态
    status = fields.Many2one('res.partner.status', 'Status')
    # 客户关系
    relation = fields.Selection(selection=[('very_good', 'Very Good'), ('good', 'Good'), ('bad', 'Bad'), ('very_bad', 'Very Bad')], string='Relation')
    # TODO:客户关系历史记录
    # 公司简介
    introduction = fields.Text('Introduction')


class BaseType(models.AbstractModel):
    _name = 'res.partner.base.type'
    name = fields.Char('Name', size=64, required=True)

    _sql_constraints = [('partner_base_type_unique', 'unique(name)', _('name must be unique !'))]


class RegisteredCapital(models.Model):
    _name = 'res.partner.registered.capital'
    _inherit = 'res.partner.base.type'


class AnnualIncome(models.Model):
    _name = 'res.partner.annual.income'
    _inherit = 'res.partner.base.type'


class CompanyType(models.Model):
    _name = 'res.partner.company.type'
    _inherit = 'res.partner.base.type'


class MainCategory(models.Model):
    _name = 'res.partner.main.category'
    _inherit = 'res.partner.base.type'


class CompanyPartnerType(models.Model):
    _name = 'res.partner.sector'
    _inherit = 'res.partner.base.type'


class ProductCategory(models.Model):
    _name = 'res.partner.product.category'
    _inherit = 'res.partner.base.type'

    parent_id = fields.Many2one('res.partner.main.category', 'Parent Category', required=True)


class Scale(models.Model):
    _name = 'res.partner.scale'
    _inherit = 'res.partner.base.type'


class CustomerType(models.Model):
    _name = 'res.partner.customer.type'
    _inherit = 'res.partner.base.type'


class Source(models.Model):
    _name = 'res.partner.source'
    _inherit = 'res.partner.base.type'


class Status(models.Model):
    _name = 'res.partner.status'
    _inherit = 'res.partner.base.type'


class InterestProduct(models.Model):
    _name = 'res.partner.interest.product'
    _inherit = 'res.partner.base.type'