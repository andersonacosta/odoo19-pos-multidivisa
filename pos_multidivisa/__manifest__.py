# -*- coding: utf-8 -*-
{
    'name': 'POS Multi Divisa Dinamico',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'POS multi-divisa dinámico con cambio de moneda principal',
    'description': """
Sistema POS Multi-Divisa Dinámico para Odoo 19 CE.
Permite cambiar la moneda operativa principal (USD/EUR) con un clic,
ajustando listas de precios, visualización y referencias BCV sin afectar la contabilidad en VES.
""",
    'author': 'Desarrollador',
    'license': 'LGPL-3',
    'depends': ['point_of_sale', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/res_config_settings_views.xml',
        'views/fiscal_book_views.xml',
    ],
    'qweb': [
        'static/src/xml/pos_currency_widget.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_multidivisa/static/src/js/pos_currency_widget.js',
        ],
    },
    'installable': True,
    'auto_install': False,
}
