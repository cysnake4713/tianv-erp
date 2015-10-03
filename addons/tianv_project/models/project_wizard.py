# -*- coding: utf-8 -*-
# author: cysnake4713
#
from openerp import tools, exceptions
from openerp import models, fields, api
from openerp.tools.translate import _


class ServiceRecordWizard(models.TransientModel):
    _inherit = 'tianv.service.service.wizard'

    project_ids = fields.Many2many('tianv.project.project', column1='wizard_id', column2='project_id', string='Projects')

    @api.model
    def default_get(self, fields_list):
        res = super(ServiceRecordWizard, self).default_get(fields_list)
        if self.env.context['active_model'] == 'tianv.project.project':
            project_ids = self.env['tianv.project.project'].search([('id', 'in', self.env.context['active_ids']), ('state', '!=', 'draft')])
            res['project_ids'] = [(6, 0, [p.id for p in project_ids])]
        return res

    @api.multi
    def generate_order(self):
        partner_id = set([r.service_id.partner_id.id for r in self.record_ids]) | set([p.partner_id.id for p in self.project_ids])
        if len(partner_id) != 1:
            raise exceptions.ValidationError(_('Selected Service have multi or have no partner!'))
        else:
            partner_id = partner_id.pop()
        # create order
        order_info = {
            'partner_id': partner_id,
            'user_id': self.env.uid,
        }
        order_id = self.env['sale.order'].create(order_info)
        self.write({'state': 'confirm', 'order_id': order_id.id})
        # create service item
        if self.record_ids:
            self.order_id.write({'order_line': [(0, 0, {'product_id': r.product_id.id, 'price_unit': r.price}) for r in self.record_ids]})
            # write back to service
            for record in self.record_ids:
                service = record.service_id
                service.write({'date': record.end_date})
                self.env['tianv.service.service.record'].create({
                    'start_date': record.start_date,
                    'end_date': record.end_date,
                    'price': record.price,
                    'service_id': service.id,
                    'order_id': self.order_id.id,
                })
        # create project item
        if self.project_ids:
            self.order_id.write({'order_line': [(0, 0, {'product_id': p.product_id.id,
                                                        'price_unit': p.contract_price,
                                                        'tax_id': [(6, 0, [p.tax_id.id] if p.tax_id.id else [])],
                                                        'name': p.name}) for p
                                                in self.project_ids]})
            # write back to project
            self.project_ids.order_id = self.order_id.id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'tianv.service.service.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
