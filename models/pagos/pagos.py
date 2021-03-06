from calendar import day_abbr, month
from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

class FondodaPagos(models.Model):
    _name = 'fondoda.pagos'


    cantidad_pagada = fields.Float('Pagado', digits=(32, 2))
    fecha_pago = fields.Date('Fecha')
    num_pago = fields.Integer('Número de pago')
    prestamo_id = fields.Many2one('fondoda.prestamo','Pestramo')

    numero = fields.Char('Número')
    capital = fields.Float('Capital', digits=(32, 2))
    interes = fields.Float('Interes', digits=(32, 2))
    num_tipo = fields.Char('Número de pago')
    sum_interes_total = fields.Float('Capital/Interes',digits=(32, 2),compute="compute_sum_interes_total",store=True,)
    saldo = fields.Float('Saldo', digits=(32, 2))
    interes2 = fields.Float('Interes', digits=(32, 2))
    day = fields.Integer('Día')
    month = fields.Char('Mes')
    year = fields.Char('Year')
    dias = fields.Integer('Días')
    

    @api.depends('capital','interes')
    def compute_sum_interes_total(self):
        for value in self:
            value.sum_interes_total = value.capital + value.interes
    
