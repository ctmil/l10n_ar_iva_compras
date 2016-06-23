from openerp import models, api, fields

class account_reporte_iva_compras(models.Model):
	_name = "account.reporte.iva.compras"
	_description = 'Reporte de IVA Compras'

	mes_carga = fields.Char(string='Mes de carga')
        invoice_id = fields.Many2one('account.invoice', string='Comprobante')
	invoice_number = fields.Char(string='Comprobante')
        date = fields.Date(string="Fecha del comprobante")
	mes = fields.Char(string='Mes Comprobante')
	doc_type = fields.Selection(string='Tipo de Comprobante',selection=[('FAC','FAC'),('RET','RET'),('NC','NC')])
	doc_type_description = fields.Char(string='Desc. Comprobante')
        period_id = fields.Many2one('account.period', string='Periodo Fiscal')
        partner_id = fields.Many2one('res.partner', string='Cliente/Proveedor')
        responsability_id = fields.Many2one('afip.responsability', string='Responsabilidad AFIP')
        document_number = fields.Char(string='CUIT')
	monto_neto_gravado = fields.Float(string='Monto Neto Gravado') 
	monto_iva_105 = fields.Float(string='Monto IVA 10.5%')
	monto_iva_21 = fields.Float(string='Monto IVA 21%')
	monto_iva_27 = fields.Float(string='Monto IVA 27%')
	monto_total = fields.Float(string='Monto Total') 
	monto_exento = fields.Float(string='Monto Exento')
	monto_percepcion_iibb = fields.Float(string='Monto Perc. IIBB')
	monto_percepcion_iva = fields.Float(string='Monto Perc. IVA')
	monto_retencion_ganan = fields.Float(string='Retencion Ganancias')
	monto_retencion_iibbmis = fields.Float(string='Retencion IIBB Misiones')
	monto_retencion_iibbcor = fields.Float(string='Retencion IIBB Cordoba')
	monto_retencion_iva = fields.Float(string='Retencion IVA')
	monto_retencion_suss = fields.Float(string='Retencion SUSS')
	monto_retencion_iibbstafe = fields.Float(string='Retencion IIBB Sta Fe')
	monto_retencion_iibbstacruz = fields.Float(string='Retencion IIBB Santa Cruz')
	monto_retencion_iibbchubut = fields.Float(string='Retencion IIBB Chubut')
	monto_retencion_iibbba = fields.Float(string='Retencion IIBB Buenos Aires')

	@api.model
        def _update_reporte_iva_compras(self):
		# Borra los movimientos de IVA
		self.search([]).unlink()
		invoices = self.env['account.invoice'].search([('state','in',['open','paid']),('type','in',['in_refund','in_invoice'])])
		for invoice in invoices:
			monto_iva_105 = 0
			monto_iva_21 = 0
			monto_iva_27 = 0
			monto_exento = 0
			monto_percepcion_iibb = 0
			monto_percepcion_iva = 0
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
				'doc_type_description': invoice.journal_id.name,
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
					if '0%' in tax_line.tax_code_id.name:
						monto_exento = monto_exento + tax_line.base_amount	
				if tax_line.name:
					if 'IIBB' in tax_line.name or 'ii bb' in tax_line.name:
						monto_percepcion_iibb = monto_percepcion_iibb + tax_line.tax_amount
					if 'per' in tax_line.name and 'iva' in tax_line.name:
						monto_percepcion_iva = monto_percepcion_iva + tax_line.tax_amount
					if 'PER' in tax_line.name and 'IVA' in tax_line.name:
						monto_percepcion_iva = monto_percepcion_iva + tax_line.tax_amount
						
			vals['monto_iva_105'] = monto_iva_105
			vals['monto_iva_21'] = monto_iva_21
			vals['monto_iva_27'] = monto_iva_27
			vals['monto_exento'] = monto_exento
			vals['monto_percepcion_iibb'] = monto_percepcion_iibb
			vals['monto_percepcion_iva'] = monto_percepcion_iva
			self.create(vals)
		vouchers = self.env['account.voucher'].search([('state','in',['posted']),('type','in',['receipt'])])
		for voucher in vouchers:
			monto_retencion_ganan = 0
			monto_retencion_iibbmis = 0
			monto_retencion_iibbcor = 0
			monto_retencion_iva = 0
			monto_retencion_suss = 0
			monto_retencion_iibbstafe = 0
			monto_retencion_iibbstacruz = 0
			monto_retencion_iibbchubut = 0
			monto_retencion_iibbba = 0
			create_record = False	
			if voucher.journal_id.code == 'RET_GANAN':
				monto_retencion_ganan = monto_retencion_ganan + voucher.amount
				create_record = True
			if voucher.journal_id.code == 'RETIIBBMIS':
				monto_retencion_iibbmis = monto_retencion_iibbmis + voucher.amount
				create_record = True
			if voucher.journal_id.code == 'RETIIBBCOR':
				monto_retencion_iibbcor = monto_retencion_iibbcor + voucher.amount
				create_record = True
			if voucher.journal_id.code == 'RET_IVA':
				monto_retencion_iva = monto_retencion_iva + voucher.amount
				create_record = True
			if voucher.journal_id.code == 'RET_SUSS':
				monto_retencion_suss = monto_retencion_suss + voucher.amount
				create_record = True
			if voucher.journal_id.code == 'RETIIBBSTA':
				monto_retencion_iibbstafe = monto_retencion_iibbstafe + voucher.amount
				create_record = True
			if voucher.journal_id.code == 'RETIIBBSCR':
				monto_retencion_iibbstacruz = monto_retencion_iibbstacruz + voucher.amount
				create_record = True
			if voucher.journal_id.code == 'RETCHUBUT':
				monto_retencion_iibbchubut = monto_retencion_iibbchubut + voucher.amount
				create_record = True
			if voucher.journal_id.code == 'RET_IIBBBA':
				monto_retencion_iibbba = monto_retencion_iibbba + voucher.amount
				create_record = True
			vals = {
				'mes_carga': voucher.create_date[:7],
				'invoice_number': voucher.reference,
				'date': voucher.date,
				'doc_type': 'RET',
				'doc_type_description': 'Retencion',
				'mes': voucher.date[:7],
				'period_id': voucher.period_id.id,
				'partner_id': voucher.partner_id.id,
				'responsability_id': voucher.partner_id.responsability_id.id,
				'document_number': voucher.partner_id.document_number,
				'monto_total': 0,
				'monto_retencion_ganan': monto_retencion_ganan,
				'monto_retencion_iibbmis': monto_retencion_iibbmis,
				'monto_retencion_iibbcor': monto_retencion_iibbcor,
				'monto_retencion_iva': monto_retencion_iva,
				'monto_retencion_suss': monto_retencion_suss,
				'monto_retencion_iibbstafe': monto_retencion_iibbstafe,
				'monto_retencion_iibbstacruz': monto_retencion_iibbstacruz,
				'monto_retencion_iibbchubut': monto_retencion_iibbchubut,
				'monto_retencion_iibbba': monto_retencion_iibbba,
				}
			if create_record:
				self.create(vals)
			
