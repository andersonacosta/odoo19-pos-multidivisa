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
