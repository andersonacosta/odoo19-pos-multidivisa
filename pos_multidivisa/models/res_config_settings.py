from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    operational_currency_id = fields.Many2one(
        'res.currency',
        string='Moneda Operativa Principal',
        config_parameter='pos_multidivisa.operational_currency_id'
    )
    currency_usd_manual = fields.Boolean(
        string='USD Modo Manual',
        config_parameter='pos_multidivisa.currency_usd_manual'
    )
    manual_usd_rate = fields.Float(
        string='Tasa USD Manual',
        config_parameter='pos_multidivisa.manual_usd_rate'
    )
    currency_eur_manual = fields.Boolean(
        string='EUR Modo Manual',
        config_parameter='pos_multidivisa.currency_eur_manual'
    )
    manual_eur_rate = fields.Float(
        string='Tasa EUR Manual',
        config_parameter='pos_multidivisa.manual_eur_rate'
    )
    igft_enabled = fields.Boolean(
        string='Habilitar Cobro IGTF',
        config_parameter='pos_multidivisa.igft_enabled'
    )

    def set_values(self):
        super().set_values()
        # Aquí se puede agregar la lógica de persistencia adicional

    @api.onchange('operational_currency_id')
    def _onchange_operational_currency_id(self):
        """Dispara la reconfiguración masiva de listas de precios y visualización."""
        # Lógica para ajustar listas de precios y visualización basada en la moneda operativa
        pass
