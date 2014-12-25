__author__ = 'cysnake4713'
# coding=utf-8
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _


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

    @api.multi
    def button_list_related_service(self):
        # compute the number of invoices to display
        related_orders = self.env['sale.order'].search([('invoice_ids', '=', self.id)])
        service_records = self.env['tianv.service.service.record'].search([('order_id', 'in', [r.id for r in related_orders])])
        service_ids = set([s.service_id.id for s in service_records])
        # choose the view_mode accordingly
        return {
            'name': u'相关服务',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'tianv.service.service',
            'target': 'current',
            'domain': "[('id','in',[" + ','.join(map(str, service_ids)) + "])]",
            'context': self.env.context,
        }

    @api.multi
    def _approve_notify(self):
        template_id = self.env['ir.model.data'].get_object('tianv_service', 'invoice_reminder_email_template')
        group = self.env['ir.model.data'].get_object('account', 'group_invoice_passer')
        ctx = {'invoice': self}
        for user_id in [u.id for u in group.users]:
            template_id.sudo().with_context(ctx).send_mail(user_id, force_send=False)

    @api.multi
    def confirm_paid(self):
        self._approve_notify()
        return super(AccountInvoiceInherit, self).confirm_paid()