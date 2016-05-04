from openerp import models, api, fields

class account_reporte_iva_compras(models.Model):
	_name = "account.reporte.iva.compras"
	_description = 'Reporte de IVA Compras'

	mes_carga = fields.Char(string='Mes de carga')
        invoice_id = fields.Many2one('account.invoice', string='Comprobante')
	invoice_number = fields.Char(string='Nro. Factura')
        date = fields.Date(string="Fecha del comprobante")
	mes = fields.Char(string='Mes Comprobante')
	doc_type = fields.Selection(string='Tipo de Comprobante',selection=[('FAC','FAC'),('RET','RET'),('NC','NC')])
        period_id = fields.Many2one('account.period', string='Periodo Fiscal')
        partner_id = fields.Many2one('res.partner', string='Cliente/Proveedor')
        responsability_id = fields.Many2one('afip.responsability', string='Responsabilidad AFIP')
        document_number = fields.Char(string='CUIT')
	monto_neto_gravado = fields.Float(string='Monto Neto Gravado') 
	monto_iva_105 = fields.Float(string='Monto IVA 10.5%')
	monto_iva_21 = fields.Float(string='Monto IVA 21%')
	monto_iva_27 = fields.Float(string='Monto IVA 27%')
	monto_total = fields.Float(string='Monto Total') 

	@api.model
        def _update_reporte_iva_compras(self):
		# Borra los movimientos de IVA
		self.search([]).unlink()
		invoices = self.env['account.invoice'].search([('state','in',['open','paid']),('type','in',['in_refund','in_invoice'])])
		for invoice in invoices:
			monto_iva_105 = 0
			monto_iva_21 = 0
			monto_iva_27 = 0
			if invoice.journal_id.code in ('CCA0005','CCB0005'):
				doc_type = 'NC'
			else:
				doc_type = 'FAC'
			vals = {
				'mes_carga': invoice.date_invoice[:7],
				'invoice_id': invoice.id,
				'invoice_number': invoice.supplier_invoice_number,
				'date': invoice.date_invoice,
				'doc_type': doc_type,
				'mes': invoice.date_invoice[:7],
				'period_id': invoice.period_id.id,
				'partner_id': invoice.partner_id.id,
				'responsability_id': invoice.partner_id.responsability_id.id,
				'document_number': invoice.partner_id.document_number,
				'monto_neto_gravado': invoice.amount_untaxed,
				'monto_total': invoice.amount_total,
				}
			for tax_line in invoice.tax_line:
				if tax_line.tax_code_id:
					if '10.5%' in tax_line.tax_code_id.name:
						monto_iva_105 = monto_iva_105 + tax_line.tax_amount	
					if '21%' in tax_line.tax_code_id.name:
						monto_iva_21 = monto_iva_21 + tax_line.tax_amount	
					if '27%' in tax_line.tax_code_id.name:
						monto_iva_27 = monto_iva_27 + tax_line.tax_amount	
			vals['monto_iva_105'] = monto_iva_105
			vals['monto_iva_21'] = monto_iva_21
			vals['monto_iva_27'] = monto_iva_27
			self.create(vals)
