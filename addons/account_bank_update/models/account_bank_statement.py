__author__ = 'cysnak4713'
# coding=utf-8
from openerp import tools, exceptions
from openerp import models, fields, api
from openerp.tools.translate import _, _logger
import base64


# class AccountBankStatementInherit(models.Model):
#     _inherit = 'account.bank.statement'
#     _rec_name = 'timetable_id'


class AccountBankStatementImport(models.TransientModel):
    _name = 'account.bank.statement.import'
    _rec_name = 'statement_id'

    data = fields.Binary('Data')
    message = fields.Html('Error Message')
    statement_id = fields.Integer('Statement Id')
    state = fields.Selection([('draft', 'Draft'), ('finish', 'Finish')], 'State', default='draft')
    code = fields.Selection([('utf-8', 'UTF-8'), ('gbk', 'GBK')], 'Code', required=True, default='gbk')

    @api.multi
    def button_import(self):
        if not self.statement_id:
            self.statement_id = self.env.context['statement_id']
        if self.env['account.bank.statement'].browse(self.statement_id).line_ids.filtered(lambda l: l.journal_entry_id):
            raise exceptions.Warning(_('Already Have Reconcile Lines, if you want to redo import, please reverse current lines and import again.'))
        """
        try:
            datas = self._read_csv(base64.decodestring(self[0].data), self[0].code)
            data, import_fields = self._convert_import_data(datas, self[0].timetable_id)
        except UnicodeDecodeError:
            raise exceptions.Warning(_('Code Error, please select correct code to import file.'))

        _logger.info('importing %d rows...', len(data))
        self.env.cr.execute('SAVEPOINT import')
        results = self.pool['school.timetable.cell'].load(self.env.cr, self.env.uid, import_fields, data, context=self.env.context)
        if results and results['messages']:
            messages = ['<p style="color:red">%s</p>' % r['message'] for r in results['messages']]
            _logger.info('Error occur during import!')
            self.env.cr.execute('ROLLBACK TO SAVEPOINT import')
            self.message = ''.join(messages)
        else:
            self.env.cr.execute('RELEASE SAVEPOINT import')
            self.message = '<p style="color: green">%s</p>' % u'成功'
            self.state = 'finish'
            _logger.info('done')
        """
        res = self.env['ir.actions.act_window'].for_xml_id('account_bank_update', 'action_bank_statement_import')
        res['res_id'] = self[0].id
        return res
