from openerp import models, api, fields

class account_invoice(models.Model):
	_inherit = 'account.invoice'

	@api.one
	def _compute_monto_otros_impuestos(self):
		monto_otros_impuestos = 0
		for tax_line in self.tax_line:
			if tax_line.tax_code_id and ('IVA' not in tax_line.tax_code_id.name):
				# import pdb;pdb.set_trace()
				monto_otros_impuestos = monto_otros_impuestos + tax_line.amount
		self.monto_otros_impuestos = monto_otros_impuestos

	@api.one
	def _compute_monto_neto(self):
		monto_neto = 0
		for tax_line in self.tax_line:
			if tax_line.tax_code_id and ('IVA Ventas 0%' in tax_line.tax_code_id.name):
				monto_neto = monto_neto + tax_line.base_amount
		self.monto_neto = monto_neto

	@api.one
	def _compute_monto_iva(self):
		monto_iva = 0
		for tax_line in self.tax_line:
			if tax_line.tax_code_id and ('IVA' in tax_line.tax_code_id.name):
				monto_iva = monto_iva + tax_line.amount
		self.monto_iva = monto_iva

	monto_neto = fields.Float(string='Monto neto',compute=_compute_monto_neto)
	monto_iva = fields.Float(string='Monto IVA',compute=_compute_monto_iva)
	monto_otros_impuestos = fields.Float(string='Monto Otros Impuestos',compute=_compute_monto_otros_impuestos)

class account_fiscal_period(models.Model):
	_inherit = "account.period"

	@api.one
	def _compute_sum_total_iva(self):
		lineas_reporte_iva = self.env['account.reporte.iva'].search([('period_id','=',self.id)])
		total_iva = 0
		for linea in lineas_reporte_iva:
			total_iva += linea.monto_iva
		self.sum_total_iva = total_iva

	@api.one
	def _compute_sum_total_ventas(self):
		lineas_reporte_iva = self.env['account.reporte.iva'].search([('period_id','=',self.id)])
		total_ventas = 0
		for linea in lineas_reporte_iva:
			total_ventas += linea.monto_total
		self.sum_total_ventas = total_ventas

	@api.one
	def _compute_sum_total_gravado(self):
		lineas_reporte_iva = self.env['account.reporte.iva'].search([('period_id','=',self.id)])
		total_gravado = 0
		for linea in lineas_reporte_iva:
			total_gravado += linea.monto_gravado
		self.sum_total_gravado = total_gravado

	@api.one
	def _compute_sum_total_no_gravado(self):
		lineas_reporte_iva = self.env['account.reporte.iva'].search([('period_id','=',self.id)])
		total_no_gravado = 0
		for linea in lineas_reporte_iva:
			total_no_gravado += linea.monto_no_gravado
		self.sum_total_no_gravado = total_no_gravado

	@api.one
	def _compute_sum_total_otros_impuestos(self):
		lineas_reporte_iva = self.env['account.reporte.iva'].search([('period_id','=',self.id)])
		total_otros_impuestos = 0
		for linea in lineas_reporte_iva:
			total_otros_impuestos += linea.monto_otros_impuestos
		self.sum_total_otros_impuestos = total_otros_impuestos

	invoices_id = fields.One2many(comodel_name='account.reporte.iva',inverse_name='period_id')
	sum_total_iva = fields.Float(string='Total IVA',compute=_compute_sum_total_iva)
	sum_total_ventas = fields.Float(string='Total Ventas',compute=_compute_sum_total_ventas)
	sum_total_gravado = fields.Float(string='Total Gravado',compute=_compute_sum_total_gravado)
	sum_total_no_gravado = fields.Float(string='Total No Gravado',compute=_compute_sum_total_no_gravado)
	sum_total_otros_impuestos = fields.Float(string='Total Otros Impuestos',compute=_compute_sum_total_otros_impuestos)

class account_reporte_iva(models.Model):
	_name = "account.reporte.iva"
	_description = 'Reporte de IVA'

        invoice_id = fields.Many2one('account.invoice', string='Comprobante')
        date = fields.Date(string="Fecha del comprobante")
        journal_id = fields.Many2one('account.journal', string='Tipo de Comprobante')
        period_id = fields.Many2one('account.period', string='Periodo Fiscal')
        partner_id = fields.Many2one('res.partner', string='Cliente/Proveedor')
        responsability_id = fields.Many2one('afip.responsability', string='Responsabilidad AFIP')
        document_number = fields.Char(string='CUIT')
	monto_gravado = fields.Float(string='Gravado')
	monto_no_gravado = fields.Float(string='No Gravado')
	monto_iva = fields.Float(string='IVA')
	monto_otros_impuestos = fields.Float(string='Monto Otros Impuestos')
	monto_neto = fields.Float(string='Monto Neto')
	monto_total = fields.Float(string='Monto Total') 

	@api.model
        def _update_reporte_iva(self):
		# Borra los movimientos de IVA
		self.search([]).unlink()
		invoices = self.env['account.invoice'].search([('state','in',['open','paid']),('type','in',['out_refund','out_invoice'])])
		for invoice in invoices:
			if invoice.journal_id.code in ('CVA0005','CVB0005'):
				signo = -1
			else:
				signo = 1
			vals = {
				'invoice_id': invoice.id,
				'date': invoice.date_invoice,
				'journal_id': invoice.journal_id.id,
				'period_id': invoice.period_id.id,
				'partner_id': invoice.partner_id.id,
				'responsability_id': invoice.partner_id.responsability_id.id,
				'document_number': invoice.partner_id.document_number,
				'monto_gravado': invoice.amount_untaxed * signo,
				'monto_iva': invoice.monto_iva * signo,
				'monto_neto': invoice.monto_neto * signo,
				'monto_otros_impuestos': invoice.monto_otros_impuestos * signo,
				'monto_total': invoice.amount_total * signo,
				}
			self.create(vals)

class account_reporte_cobranzas(models.Model):
	_name = "account.reporte.cobranzas"
	_description = 'Reporte de Cobranzas'

	date = fields.Date('Fecha')
        invoice_id = fields.Many2one('account.invoice', string='Factura')
        period_id = fields.Many2one('account.period', string='Periodo Fiscal')
        journal_id = fields.Many2one('account.journal', string='Metodo de Pago')
        partner_id = fields.Many2one('res.partner', string='Cliente/Proveedor')
        voucher_id = fields.Many2one('account.voucher', string='Recibo Pago')
	check_id = fields.Many2one('account.check',string='Nro Cheque')
	deposit_date = fields.Date(string='Fecha Deposito Cheque',related='check_id.payment_date')
	bank_id = fields.Many2one('res.bank',string='Banco Cheque')
	check_amount = fields.Float(string='Monto Cheque')
	cash_amount = fields.Float(string='Monto Efectivo')
	bank_amount = fields.Float(string='Monto Transferencia')

	@api.model
        def _update_reporte_cobranzas(self):
		# Borra los movimientos de cobranzas
		self.search([]).unlink()
		vouchers = self.env['account.voucher'].search([('state','in',['posted'])])
		for voucher in vouchers:
			if voucher.journal_id.name in ['Banco','Efectivo']:
				for line in voucher.line_ids:
					move_line = self.env['account.move.line'].browse(line.move_line_id.id)
					invoice_id = move_line.invoice.id
					vals = {
						'voucher_id': voucher.id,
						'invoice_id': invoice_id,	
						'date': voucher.date,
						'period_id': move_line.move_id.period_id.id,
						'journal_id': voucher.journal_id.id,
						'period_id': move_line.move_id.period_id.id,
						'partner_id': voucher.partner_id.id,
						}
					if voucher.journal_id.name == 'Banco':
						vals['bank_amount'] = line.amount
					if voucher.journal_id.name == 'Efectivo':
						vals['cash_amount'] = line.amount
					if move_line.debit > 0:
						self.create(vals)
			if voucher.journal_id.name == 'Cheques de Terceros':
				for line in voucher.line_ids:
					move_line = self.env['account.move.line'].browse(line.move_line_id.id)
					invoice_id = move_line.invoice.id
				checks = self.env['account.check'].search([('voucher_id','=',voucher.id)])
				for check in checks:
					vals = {
						'voucher_id': voucher.id,
						'invoice_id': invoice_id,	
						'check_id': check.id,
						'bank_id': check.bank_id.id,
						'date': voucher.date,
						'period_id': move_line.move_id.period_id.id,
						'journal_id': voucher.journal_id.id,
						'period_id': move_line.move_id.period_id.id,
						'partner_id': voucher.partner_id.id,
						'check_amount': check.amount,
						}
					self.create(vals)
