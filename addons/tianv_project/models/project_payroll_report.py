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
    balance_paid = fields.Float('Left Paid Balance')

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'project_payroll_report')
        cr.execute("""
create or replace view project_payroll_report as (
    WITH temp_result AS (
        SELECT payslip.id AS id, payslip.partner_id AS partner_id, payslip.period AS period, task.need_paid AS need_paid, payslip.paid_total AS total_paid,
        COALESCE(task.need_paid,0)-COALESCE(payslip.paid_total,0) AS left_paid FROM
            (
                SELECT l.slip_id AS id, e.address_home_id AS partner_id, date_trunc( 'month', p.date_from)::date AS period ,l.paid_total AS paid_total FROM
                    (
                        SELECT payslip_id AS slip_id, sum(amount) AS paid_total FROM hr_payslip_input
                        WHERE code='BUSINESS_COMMISSION' or code='PROJECT_COMMISSION' or code='SERVICE_COMMISSION' or code='BALANCE'
                        GROUP BY payslip_id
                    ) AS l,  hr_employee AS e, hr_payslip AS p
                WHERE e.id=p.employee_id and p.id=l.slip_id and e.address_home_id is not null
            ) AS payslip  LEFT JOIN
            (
                SELECT  partner_id, date_trunc( 'month', partner_finish_date)::date  AS period, sum(price) AS need_paid FROM tianv_project_project_record
                WHERE state='finished'
                GROUP BY partner_id, date_trunc( 'month', partner_finish_date)::date
            ) AS task
        ON payslip.partner_id=task.partner_id AND payslip.period=task.period
        ORDER BY period, partner_id
    )

    SELECT t.* , (SELECT sum(temp_result.left_paid) FROM temp_result WHERE temp_result.period<=t.period AND temp_result.partner_id=t.partner_id) AS balance_paid
    FROM temp_result  AS t
)
""")
