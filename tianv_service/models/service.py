# coding=utf-8
import datetime
import logging
import time
from openerp import models, fields, api, _

__author__ = 'cysnake4713'
_logger = logging.getLogger(__name__)


class Service(models.Model):
    _name = "tianv.service.service"
    _description = "Service"
    _inherits = {'account.analytic.account': "analytic_account_id"}
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'

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

    _track = {
        'state': {
            'tianv_service.mt_account_pending': lambda self, cr, uid, obj, ctx=None: obj.state == 'pending',
            'tianv_service.mt_account_closed': lambda self, cr, uid, obj, ctx=None: obj.state == 'close',
            'tianv_service.mt_account_opened': lambda self, cr, uid, obj, ctx=None: obj.state == 'open',
        },
    }

    product_id = fields.Many2one('product.product', string='Product', track_visibility='onchange')
    importance = fields.Selection(_importance_selection, 'Importance')
    # 账号个数
    account_number = fields.Integer('Account Number')
    # 服务价格
    product_price = fields.Float('Product Price', (10, 2), track_visibility='onchange')
    # 服务等级
    service_level = fields.Selection(_service_level_selection, 'Service Level')
    # 服务状态
    service_status = fields.Selection(_status_selection, 'Service Status', track_visibility='onchange')
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
    # 历史记录
    record_ids = fields.One2many('tianv.service.service.record', 'service_id', 'History Records')

    _defaults = {
        'type': 'contract',
        'service_status': 'normal',
        'manager_id': lambda self, cr, uid, *args: uid,
    }

    @api.one
    @api.depends('service_status')
    def _compute_service_status(self):
        self.service_status_function = self.service_status

    @api.one
    @api.onchange('service_level', 'product_id')
    def _onchange_name(self):
        name = [
            dict(self._service_level_selection)[self.service_level] if self.service_level else '',
            self.product_id.name_get()[0][1] if self.product_id and len(self.product_id.name_get()[0]) > 1 else '',
        ]
        self.name = ''.join(name)

    @api.multi
    def set_close(self):
        return self.write({'state': 'close'})

    @api.multi
    def set_cancel(self):
        return self.write({'state': 'cancelled'})

    @api.multi
    def set_open(self):
        return self.write({'state': 'open'})

    @api.multi
    def set_pending(self):
        return self.write({'state': 'pending'})

    @api.multi
    def open_service(self):
        return self.write({'service_status': 'normal'})

    @api.multi
    def close_service(self):
        return self.write({'service_status': 'stop'})

    @api.multi
    def pause_service(self):
        return self.write({'service_status': 'pause'})

    @api.model
    def cron_computer_explore(self):
        remind = {}

        def fill_remind(key, domain, write_pending=False):
            base_domain = [
                ('type', '=', 'contract'),
                ('partner_id', '!=', False),
                ('manager_id', '!=', False),
                ('manager_id.email', '!=', False),
            ]
            base_domain.extend(domain)

            accounts = self.search(base_domain, order='name asc')
            for account in accounts:
                if write_pending:
                    account.write({'state': 'pending'})
                remind_user = remind.setdefault(account.manager_id.id, {})
                remind_type = remind_user.setdefault(key, {})
                remind_partner = remind_type.setdefault(account.partner_id, []).append(account)

        # Already expired
        fill_remind("old", [('state', 'in', ['pending'])])

        # Expires now
        fill_remind("new", [('state', 'in', ['draft', 'open']), '&', ('date', '!=', False), ('date', '<=', time.strftime('%Y-%m-%d'))], True)

        # Expires in less than 30 days
        fill_remind("future", [('state', 'in', ['draft', 'open']), ('date', '!=', False),
                               ('date', '<', (datetime.datetime.now() + datetime.timedelta(30)).strftime("%Y-%m-%d"))])
        ctx = {
            'base_url': self.env['ir.config_parameter'].get_param('web.base.url'),
            'action_id': self.env['ir.model.data'].get_object_reference('tianv_service', 'action_service_service_all')[1],
        }
        template_id = self.env['ir.model.data'].get_object('tianv_service', 'service_cron_email_template')
        # 特别通知黄总
        huang = self.env['res.users'].search([('login', '=', 'jiaolg@tianv.com')])
        for user_id, data in remind.items():
            ctx["data"] = data
            _logger.debug("Sending reminder to uid %s", user_id)
            template_id.with_context(ctx).send_mail(user_id, force_send=False)
            if huang:
                template_id.with_context(ctx).send_mail(huang[0].id, force_send=False)
        return True

    def _message_get_auto_subscribe_fields(self, cr, uid, updated_fields, auto_follow_fields=None, context=None):
        if auto_follow_fields is None:
            auto_follow_fields = ['user_id']
        auto_follow_fields = auto_follow_fields + ['manager_id']
        return super(Service, self)._message_get_auto_subscribe_fields(cr, uid, updated_fields, auto_follow_fields, context)


class ServiceRecord(models.Model):
    _name = "tianv.service.service.record"
    _description = "Service record"
    _rec_name = 'end_date'
    _order = 'end_date desc'

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    price = fields.Float('Service Price', (10, 2), required=True)
    service_id = fields.Many2one('tianv.service.service', 'Service', ondelete='cascade', required=True)
    order_id = fields.Many2one('sale.order', 'Order')


class ServiceRecordWizard(models.TransientModel):
    _inherit = 'tianv.service.service.record'
    _name = 'tianv.service.service.wizard'

    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], 'State')

    @api.model
    def default_get(self, fields_list):
        """
        This function gets default values
        """
        res = super(ServiceRecordWizard, self).default_get(fields_list)
        res['service_id'] = self.env.context['active_id']
        last_record = self.env['tianv.service.service.record'].search([('service_id', '=', res['service_id'])], order='end_date desc')
        if last_record:
            res['price'] = last_record[0].price
        return res

    _defaults = {
        'state': 'draft',
        'start_date': lambda *a: fields.Date.today(),
    }

    @api.multi
    def generate_order(self):
        service = self.service_id
        order_info = {
            'partner_id': service.partner_id.id,
            'project_id': service.analytic_account_id.id,
            'order_line': [(0, 0, {'product_id': service.product_id.id, 'price_unit': self.price})],
            'user_id': service.manager_id.id,
        }
        order_id = self.env['sale.order'].create(order_info)
        self.write({'state': 'confirm', 'order_id': order_id.id, 'end_date': self.end_date})
        service.write({'date': self.end_date})
        self.env['tianv.service.service.record'].create({
            'start_date': self.start_date,
            'end_date': self.end_date,
            'price': self.price,
            'service_id': self.service_id.id,
            'order_id': self.order_id.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'tianv.service.service.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @api.multi
    def view_order(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.order_id.id,
            'views': [(False, 'form')],
            'target': 'current',
        }


class AccountInvoiceInherit(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    _order = "id desc"

    state = fields.Selection([('draft', 'Draft'),
                              ('proforma', 'Pro-forma'),
                              ('proforma2', 'Pro-forma'),
                              ('open', 'Open'),
                              ('paid', 'Paid'),
                              ('cancel', 'Cancelled'),
                              ('passed', u'已审批'), ], string='Status', index=True, readonly=True, default='draft',
                             track_visibility='onchange', copy=False,
    )

    @api.multi
    def button_passed(self):
        self.state = 'passed'
        return True

    @api.multi
    def button_return_passed(self):
        self.state = 'paid'
        return True
