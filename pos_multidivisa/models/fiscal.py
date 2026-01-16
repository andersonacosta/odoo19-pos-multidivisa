from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    rif = fields.Char(string='Identificador Fiscal (RIF)')


class AccountMove(models.Model):
    _inherit = 'account.move'

    withholding_rate = fields.Float(string='Tasa de Retencion', default=0.0)
    fiscal_book_id = fields.Many2one('fiscal.book', string='Libro Fiscal')

    def compute_withholdings(self):
        """Calcular retencion basada en la tasa de retencion."""
        for move in self:
            rate = move.withholding_rate or 0.0
            if rate > 0:
                base_amount = move.amount_total
                withholding_amount = base_amount * rate / 100.0
                # Devuelve el monto de la retencion; en un entorno real se crearia una linea de diario negativa
                return withholding_amount
        return 0.0


class FiscalBook(models.Model):
    _name = 'fiscal.book'
    _description = 'Libro Fiscal'

    name = fields.Char(string='Nombre')
    date_start = fields.Date(string='Fecha de Inicio')
    date_end = fields.Date(string='Fecha de Fin')
    move_ids = fields.One2many('account.move', 'fiscal_book_id', string='Facturas')
    total_amount = fields.Monetary(string='Monto Total', compute='_compute_total_amount', currency_field='company_currency_id')
    company_currency_id = fields.Many2one('res.currency', string='Moneda de la Compañia', related='company_id.currency_id', readonly=True)
    company_id = fields.Many2one('res.company', string='Compania', default=lambda self: self.env.company)

    @api.depends('move_ids.amount_total')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(move.amount_total for move in record.move_ids)
