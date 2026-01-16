odoo.define('pos_multidivisa.PosCurrencyWidget', function (require) {
    'use strict';
    const { useState, useRef } = owl.hooks;
    const PosComponent = require('point_of_sale.PosComponent');
    const rpc = require('web.rpc');

    class PosCurrencyWidget extends PosComponent {
        setup() {
            super.setup();
            this.state = useState({
                primaryRate: 0,
                secondaryRate: 0,
                mode: 'auto',
                statusIcon: '🟢',
            });
            this.inputRef = useRef('input');
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
                    this.state.statusIcon = result.mode === 'auto' ? '🟢' : '🟠';
                }
            } catch (error) {
                console.error(error);
                this.state.statusIcon = '🔴';
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

        async setManualRate(value) {
            const rate = parseFloat(value);
            if (!isNaN(rate)) {
                await rpc.query({
                    model: 'res.currency',
                    method: 'set_pos_currency_rate',
                    args: [rate],
                });
                await this.loadRates();
            }
        }
    }

    PosCurrencyWidget.template = 'PosCurrencyWidget';
    return PosCurrencyWidget;
});
