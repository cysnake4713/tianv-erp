__author__ = 'cysnake4713'

# coding=utf-8
from openerp import tools, exceptions
from openerp import models, fields, api
from openerp.tools.translate import _


class AttendanceWizard(models.TransientModel):
    _name = 'tianv.hr.attendance.wizard'
    _rec_name = 'period'
    _description = 'Attendance Create Wizard'

    state = fields.Selection([('period_select', 'Select Period'),
                              ('generate_social', 'Generate Social Insurance'),
                              ('generate_attendance', 'Generate Attendance'),
                              ('generate_payroll', 'Generate Payroll'),
                              ('done', 'Done')], 'State', default='period_select')
    period = fields.Many2one('account.period', 'Select Period', required=True)
    employees = fields.Many2many('hr.employee', 'atttendance_wizard_employee_rel', 'wizard_id', 'employee_id', 'Employees', required=True)
    contracts = fields.Many2many('hr.contract', 'atttendance_wizard_contract_rel', 'wizard_id', 'contract_id', 'Contracts', readonly=True)

    relative_social = fields.Many2many('tianv.social.insurance.record', 'attendance_wizard_insurance_rel', 'wizard_id', 'insurance_id',
                                       'Relative Social')

    relative_attendances = fields.Many2many('tianv.hr.attendance.record', 'attendance_wizard_record_rel', 'wizard_id', 'record_id',
                                            'Attendance Records')

    @api.multi
    def button_get_contract(self):
        for wizard in self:
            contract_ids = []
            for employee in wizard.employees:
                try:
                    contract_ids += [employee.contract_ids.filtered(
                        lambda c: c.date_start <= self.period.date_start and c.date_end >= self.period.date_stop).ensure_one().id]
                except Exception:
                    raise exceptions.Warning(
                        _("Related employee have find multi contract or have not match contract for employee: %s") % employee.name)
                wizard.contracts = [(6, 0, contract_ids)]


    @api.multi
    def button_period_to_social(self):
        self.relative_social = self.env['tianv.social.insurance.record'].search(
            [('period', '=', self.period.id), ('contract', 'in', [e.id for e in self.contracts])])
        self.state = 'generate_social'

    @api.multi
    def button_generate_social(self):
        need_process_contracts = self.contracts.filtered(lambda contract: contract not in [s.contract for s in self.relative_social])
        social_config = self.env['tianv.social.insurance.config'].search([('contract', 'in', [c.id for c in need_process_contracts])])
        social_config.with_context(period=self.period.id).generate_insurance_record()
        self.relative_social = self.env['tianv.social.insurance.record'].search(
            [('period', '=', self.period.id), ('contract', 'in', [e.id for e in self.contracts])])

    @api.multi
    def button_social_to_attendance(self):
        self.relative_attendances = self.env['tianv.hr.attendance.record'].search(
            [('period', '=', self.period.id), ('contract', 'in', [e.id for e in self.contracts])])
        self.state = 'generate_attendance'

    @api.multi
    def button_generate_attendance(self):
        need_process_contracts = self.contracts.filtered(lambda c: c not in [s.contract for s in self.relative_attendances])
        for contract in need_process_contracts:
            new_attendance_record = self.env['tianv.hr.attendance.record'].create({'contract': contract.id, 'period': self.period.id})
            new_attendance_record.button_generate_record()
        self.relative_attendances = self.env['tianv.hr.attendance.record'].search(
            [('period', '=', self.period.id), ('contract', 'in', [e.id for e in self.contracts])])

    @api.multi
    def button_attendance_payroll(self):
        pass



