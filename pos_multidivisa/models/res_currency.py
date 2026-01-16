from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    @api.model
    def update_bcv_rates(self):
        """Fetch USD and EUR rates from BCV and update currency records. Performs 5% discrepancy check for manual rates."""
        try:
            from pydolarvzla import Monitor
            monitor = Monitor()
            rates = monitor.get_all()
            usd_rate = rates.get('usd', {}).get('price')
            eur_rate = rates.get('eur', {}).get('price')
        except Exception as e:
            _logger.error("Failed to fetch BCV rates: %s", e)
@api.model
    def get_pos_currency_rates(self):
        """Return primary and secondary currency rates and mode for POS widget"""
        config = self.env['res.config.settings'].sudo().get_values()
        primary_id = config.get('operational_currency_id')
        primary_currency = self.browse(primary_id) if primary_id else self.env.ref('base.USD')
        secondary_currency = self.env.ref('base.EUR') if primary_currency.name == 'USD' else self.env.ref('base.USD')
        mode = 'auto'
        if primary_currency.name == 'USD':
            if config.get('currency_usd_manual'):
                mode = 'manual'
        elif primary_currency.name == 'EUR':
            if config.get('currency_eur_manual'):
                mode = 'manual'
        return {
            'primary_rate': primary_currency.rate,
            'secondary_rate': secondary_currency.rate,
            'mode': mode,
            'primary_currency': primary_currency.name,
            'secondary_currency': secondary_currency.name,
        }

    @api.model
    def toggle_pos_currency_mode(self):
        """Toggle auto/manual mode for the current operational currency"""
        config_model = self.env['res.config.settings']
        config = config_model.sudo().get_values()
        primary_id = config.get('operational_currency_id')
        primary_currency = self.browse(primary_id) if primary_id else self.env.ref('base.USD')
        if primary_currency.name == 'USD':
            current = config.get('currency_usd_manual', False)
            config_model.sudo().set_values({'currency_usd_manual': not current})
        elif primary_currency.name == 'EUR':
            current = config.get('currency_eur_manual', False)
            config_model.sudo().set_values({'currency_eur_manual': not current})
        return True

    @api.model
    def set_pos_currency_rate(self, rate):
        """Set manual rate for current operational currency"""
        config_model = self.env['res.config.settings']
        config = config_model.sudo().get_values()
        primary_id = config.get('operational_currency_id')
        primary_currency = self.browse(primary_id) if primary_id else self.env.ref('base.USD')
        if primary_currency.name == 'USD':
            config_model.sudo().set_values({'manual_usd_rate': rate})
        elif primary_currency.name == 'EUR':
            config_model.sudo().set_values({'manual_eur_rate': rate})
        return True

            return
        # Update USD rate
        if usd_rate:
            usd_currency = self.search([('name', '=', 'USD')], limit=1)
            if usd_currency:
                new_rate = 1 / float(usd_rate) if float(usd_rate) else 0.0
                if usd_currency.rate and abs(usd_currency.rate - new_rate) / usd_currency.rate > 0.05:
                    _logger.warning("USD rate difference >5% requires supervisor approval")
                else:
                    usd_currency.rate = new_rate
        # Update EUR rate
        if eur_rate:
            eur_currency = self.search([('name', '=', 'EUR')], limit=1)
            if eur_currency:
                new_rate = 1 / float(eur_rate) if float(eur_rate) else 0.0
                if eur_currency.rate and abs(eur_currency.rate - new_rate) / eur_currency.rate > 0.05:
                    _logger.warning("EUR rate difference >5% requires supervisor approval")
                else:
                    eur_currency.rate = new_rate
