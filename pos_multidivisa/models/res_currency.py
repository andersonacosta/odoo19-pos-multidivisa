from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ResCurrency(models.Model):
    _inherit = 'res.currency'

    @api.model
    def update_bcv_rates(self):
        """Fetches the USD and EUR rates from BCV and updates the currency rates."""
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
            usd = self.search([('name', '=', 'USD')], limit=1)
            if usd:
                try:
                    usd.rate = 1 / float(usd_rate) if float(usd_rate) else 0.0
                except Exception:
                    pass
        # Update EUR rate
        if eur_rate:
            eur = self.search([('name', '=', 'EUR')], limit=1)
            if eur:
                try:
                    eur.rate = 1 / float(eur_rate) if float(eur_rate) else 0.0
                except Exception:
                    pass
