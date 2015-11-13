# coding=utf-8
__author__ = 'cysnake4713'
from openerp import tools, exceptions
from openerp import models, fields, api
from openerp.tools.translate import _, _logger
import base64, StringIO, csv, itertools, re


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

    @staticmethod
    def _read_csv(record, encoding):
        """ Returns a CSV-parsed iterator of all empty lines in the file

        :throws csv.Error: if an error is detected during CSV parsing
        :throws UnicodeDecodeError: if ``options.encoding`` is incorrect
        """
        csv_iterator = csv.reader(
            StringIO.StringIO(record))
        csv_nonempty = itertools.ifilter(None, csv_iterator)
        return itertools.imap(
            lambda row: [item.decode(encoding) for item in row],
            csv_nonempty)

    def _convert_import_data(self, import_datas, statement_id):
        import_fields = head_map = import_datas.next()
        import_fields += ['partner_id/.id', 'statement_id/.id']
        if 'name' not in head_map or 'date' not in head_map or 'amount' not in head_map:
            raise exceptions.Warning(_('Name or Date not in the import file!'))

        results = []
        for row in import_datas:
            name_rows = [n for n in row[head_map.index('name')].split(' ') if n]

            domain = [('name', '=', n) for n in name_rows]
            domain = ['|' for l in range(len(name_rows) - 1)] + domain
            partner_id = self.env['res.partner'].search(domain)
            if len(partner_id) == 1:
                partner_id = partner_id.id
            else:
                partner_id = False
            results += [row + [partner_id, statement_id]]
        return results, import_fields

    @api.multi
    def button_import(self):
        if not self.statement_id:
            self.statement_id = self.env.context['statement_id']
        if self.env['account.bank.statement'].browse(self.statement_id).line_ids.filtered(lambda l: l.journal_entry_id):
            raise exceptions.Warning(_('Already Have Reconcile Lines, if you want to redo import, please reverse current lines and import again.'))

        try:
            datas = self._read_csv(base64.decodestring(self.data), self.code)
            data, import_fields = self._convert_import_data(datas, self.statement_id)
            pass
        except UnicodeDecodeError:
            raise exceptions.Warning(_('Code Error, please select correct code to import file.'))

        _logger.info('importing %d rows...', len(data))
        self.env.cr.execute('SAVEPOINT bank_statement_import')
        results = self.pool['account.bank.statement.line'].load(self.env.cr, self.env.uid, import_fields, data, context=self.env.context)
        if results and results['messages']:
            messages = ['<p style="color:red">%s</p>' % r['message'] for r in results['messages']]
            _logger.info('Error occur during import!')
            self.env.cr.execute('ROLLBACK TO SAVEPOINT bank_statement_import')
            self.message = ''.join(messages)
        else:
            self.env.cr.execute('RELEASE SAVEPOINT bank_statement_import')
            self.message = '<p style="color: green">%s</p>' % u'成功'
            self.state = 'finish'
            _logger.info('done')
        res = self.env['ir.actions.act_window'].for_xml_id('account_bank_update', 'action_bank_statement_import')
        res['res_id'] = self[0].id
        return res
