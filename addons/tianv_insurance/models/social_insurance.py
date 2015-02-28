# coding=utf-8
__author__ = 'cysnak4713'
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _
from openerp import exceptions


class SocialInsuranceType(models.Model):
    _name = 'tianv.social.insurance.type'

    name = fields.Char('Name', required=True)

    _sql_constraints = [('social_insurance_type_name_unique', 'unique(name)', _('name must be unique !'))]


class SocialInsuranceConfig(models.Model):
    _name = 'tianv.social.insurance.config'
    _rec_name = 'computer_code'

    _inherit = 'mail.thread'

    contract = fields.Many2one('hr.contract', 'Hr Contract', track_visibility='onchange')
    computer_code = fields.Char('Computer Code', track_visibility='onchange')
    census_type = fields.Selection([('city', u'市内城镇'), ('country', u'市外农村')], 'Census Type', track_visibility='onchange')
    lines = fields.One2many('tianv.social.insurance.line', 'config', 'Config Lines')

    personal_total = fields.Float('Personal Total', (10, 2), compute='_compute_total')
    company_total = fields.Float('Company Part', (10, 2), compute='_compute_total')
    total = fields.Float('Total', (10, 2), compute='_compute_total')

    active = fields.Boolean('Is Active', track_visibility='onchange')

    @api.multi
    def _compute_total(self):
        for config in self:
            personal_total = 0
            company_total = 0
            for line in config.lines:
                personal_total += line.personal_part
                company_total += line.company_part
            config.personal_total = personal_total
            config.company_total = company_total
            config.total = config.personal_total + config.company_total

    _defaults = {
        'active': True,
    }

    @api.one
    @api.constrains('contract', 'active')
    def _check_contract(self):
        if self.contract and self.search([('id', '!=', self.id), ('contract', '=', self.contract.id), ('active', '=', True)]):
            raise Warning(_('Contract already have a active social insurance config, please inactive old one or change the contract'))

    @api.multi
    def name_get(self):
        """ name_get() -> [(id, name), ...]

        Returns a textual representation for the records in ``self``.
        By default this is the value of the ``display_name`` field.

        :return: list of pairs ``(id, text_repr)`` for each records
        :rtype: list(tuple)
        """
        result = []
        for record in self:
            name = u'总额:%s (公司:%s|个人:%s)'
            result.append((record.id, name % (record.total, record.company_total, record.personal_total)))
        return result


    @api.multi
    def generate_insurance_record(self):
        if 'period' not in self.env.context:
            period = self.env['account.period'].search([('date_start', '<=', fields.Datetime.now()), ('date_stop', '>=', fields.Datetime.now())])
            period = period.id if period else None
        else:
            period = self.env.context['period']
        for config in self:
            data = {
                'contract': config.contract.id,
                'computer_code': config.computer_code,
                'census_type': config.census_type,
                'period': period,
            }
            record = self.env['tianv.social.insurance.record'].create(data)
            for line in config.lines:
                line_data = {
                    'type': line.type.id,
                    'company_part': line.company_part,
                    'personal_part': line.personal_part,
                    'record': record.id,
                }
                record.lines.create(line_data)
        return True

    @api.multi
    def write(self, vals):
        result = super(SocialInsuranceConfig, self).write(vals)
        if 'lines' in vals:
            for record in self:
                names = [("<div>" + l.name_get()[0][1] + "</div>") for l in record.lines]
                message = u"""
<span>社保金额变更为</span>
%s
""" % (''.join(names))
                record.message_post(body=message)
        return result

    @api.model
    def create(self, vals):
        result = super(SocialInsuranceConfig, self).create(vals)

        names = [("<div>" + l.name_get()[0][1] + "</div>") for l in result.lines]
        message = u"""
<span>社保金额:</span>
%s
""" % (''.join(names))
        result.message_post(body=message)
        return result


class SocialInsuranceLine(models.Model):
    _name = 'tianv.social.insurance.line'
    _rec_name = 'type'

    type = fields.Many2one('tianv.social.insurance.type', 'Insurance Type', required=True)
    company_part = fields.Float('Company Part', (10, 2))
    personal_part = fields.Float('Personal Part', (10, 2))
    config = fields.Many2one('tianv.social.insurance.config', 'Related Config')

    @api.multi
    def name_get(self):
        """ name_get() -> [(id, name), ...]

        Returns a textual representation for the records in ``self``.
        By default this is the value of the ``display_name`` field.

        :return: list of pairs ``(id, text_repr)`` for each records
        :rtype: list(tuple)
        """
        result = []
        for record in self:
            name = u'类型:%s (公司:%s|个人:%s)'
            result.append((record.id, name % (record.type.name, record.company_part, record.personal_part)))
        return result


class SocialInsuranceRecord(models.Model):
    _name = 'tianv.social.insurance.record'
    _inherit = 'tianv.social.insurance.config'

    _order = 'period desc, contract desc'

    lines = fields.One2many('tianv.social.insurance.record.line', 'record', 'Record Lines')
    period = fields.Many2one('account.period', 'Account Period')

    @api.one
    @api.constrains('contract', 'period', 'active')
    def _check_contract(self):
        if self.contract and self.period and \
                self.search([('id', '!=', self.id), ('contract', '=', self.contract.id), ('period', '=', self.period.id), ('active', '=', True)]):
            raise Warning(_('A active same period and contract insurance record exist! remove or inactive old one before create'))

    @api.multi
    def write_back_info(self):
        for record in self:
            config = self.env['tianv.social.insurance.config'].search([('contract', '=', record.contract.id), ('active', '=', True)])
            if config:
                data = {
                    'contract': record.contract.id,
                    'computer_code': record.computer_code,
                    'census_type': record.census_type,
                }
                config.write(data)
                config.lines.unlink()
                for line in record.lines:
                    line_data = {
                        'type': line.type.id,
                        'company_part': line.company_part,
                        'personal_part': line.personal_part,
                        'config': config.id,
                    }
                    config.lines.create(line_data)
            else:
                raise exceptions.Warning(_("Can't find related insurance config!"))
        return True


class SocialInsuranceRecordLine(models.Model):
    _name = 'tianv.social.insurance.record.line'
    _inherit = 'tianv.social.insurance.line'

    record = fields.Many2one('tianv.social.insurance.record', 'Related Record')


