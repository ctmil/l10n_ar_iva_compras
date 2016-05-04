from openerp import models, api, fields

class account_reporte_iva_compras(models.Model):
	_name = "account.reporte.iva.compras"
	_description = 'Reporte de IVA Compras'

        invoice_id = fields.Many2one('account.invoice', string='Comprobante')
        date = fields.Date(string="Fecha del comprobante")
	mes = fields.Char(string='Mes Comprobante')
	doc_type = fields.Selectioni(string='Tipo de Comprobante',selection=[('FAC','FAC'),('RET','RET'),('NC','NC')])
        period_id = fields.Many2one('account.period', string='Periodo Fiscal')
        partner_id = fields.Many2one('res.partner', string='Cliente/Proveedor')
        responsability_id = fields.Many2one('afip.responsability', string='Responsabilidad AFIP')
        document_number = fields.Char(string='CUIT')
	monto_total = fields.Float(string='Monto Total') 

	@api.model
        def _update_reporte_iva_compras(self):
		# Borra los movimientos de IVA
		self.search([]).unlink()
		invoices = self.env['account.invoice'].search([('state','in',['open','paid']),('type','in',['in_refund','in_invoice'])])
		for invoice in invoices:
			if invoice.journal_id.code in ('CCA0005','CCB0005'):
				doc_type = 'NC'
			else:
				doct_type = 'FAC'
			vals = {
				'invoice_id': invoice.id,
				'date': invoice.date_invoice,
				'doc_type': doc_type,
				'mes': invoice.date_invoice[:7],
				'period_id': invoice.period_id.id,
				'partner_id': invoice.partner_id.id,
				'responsability_id': invoice.partner_id.responsability_id.id,
				'document_number': invoice.partner_id.document_number,
				'monto_total': invoice.amount_total,
				}
			self.create(vals)
