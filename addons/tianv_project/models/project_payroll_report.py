# -*- coding: utf-8 -*-
# author: cysnake4713
#

from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _


class ProjectPayrollReport(models.Model):
    _name = 'project.payroll.report'
    _rec_name = 'partner_id'
    _description = 'Analytic Project Paid Statistics'
    _auto = False

    partner_id = fields.Many2one('res.partner', 'Partner')
    period = fields.Date('Period')
    need_paid = fields.Float('Need Paid')
    total_paid = fields.Float('Total Paid')
    left_paid = fields.Float('Left Paid')

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'project_payroll_report')
        cr.execute("""
create or replace view project_payroll_report as (
    select payslip.id as id, payslip.partner_id as partner_id, payslip.period as period, task.need_paid as need_paid, payslip.paid_total as total_paid,
    COALESCE(task.need_paid,0)-COALESCE(payslip.paid_total,0) as left_paid from
        (
        select l.slip_id as id, e.address_home_id as partner_id, date_trunc( 'month', p.date_from)::date as period ,l.paid_total  as paid_total from
            (
            select employee_id, slip_id,  sum(total) as paid_total from hr_payslip_line
            where code='BUSINESS_COMMISSION' or code = 'PROJECT_COMMISSION' or code = 'SERVICE_COMMISSION'  or code = 'BALANCE'
            group by slip_id, employee_id
            ) as l,  hr_employee as e, hr_payslip as p
        where e.id = l.employee_id and p.id = l.slip_id and e.address_home_id is not null
        ) as payslip  LEFT JOIN
        (
        select  partner_id, date_trunc( 'month', finish_date)::date  as period, sum(price) as need_paid from tianv_project_project_record
        group by partner_id, date_trunc( 'month', finish_date)::date
        ) as task
    on payslip.partner_id =  task.partner_id and payslip.period =  task.period
    order by period, partner_id
)
""")
