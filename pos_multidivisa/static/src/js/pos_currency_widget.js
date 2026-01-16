odoo.define('pos_multidivisa.PosCurrencyWidget', function(require){
    'use strict';
    const { useState } = owl.hooks;
    const { PosComponent } = require('point_of_sale.PosComponent');
    const rpc = require('web.rpc');

    class PosCurrencyWidget extends PosComponent {
        constructor() {
            super(...arguments);
            this.state = useState({
                primaryRate: 0,
                secondaryRate: 0,
                mode: 'auto',
            });
            this.loadRates();
        }
        async loadRates() {
            try {
                const result = await rpc.query({
                    model: 'res.currency',
                    method: 'get_pos_currency_rates',
                    args: [],
                });
                if (result) {
                    this.state.primaryRate = result.primary_rate;
                    this.state.secondaryRate = result.secondary_rate;
                    this.state.mode = result.mode;
                }
            } catch (error) {
                console.error(error);
            }
        }
        async toggleMode() {
            await rpc.query({
                model: 'res.currency',
                method: 'toggle_pos_currency_mode',
                args: [],
            });
            await this.loadRates();
        }
    }
    PosCurrencyWidget.template = 'PosCurrencyWidget';
    return PosCurrencyWidget;
});
