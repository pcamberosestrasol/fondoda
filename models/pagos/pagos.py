from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

class FondodaPagos(models.Model):
    _name = 'fondoda.pagos'


    cantidad_pagada = fields.Float('Pagado', digits=(32, 2))
    fecha_pago = fields.Date('Fecha')
    num_pago = fields.Integer('Número de pago')
    prestamo_id = fields.Many2one('fondoda.prestamo','Pestramo')
    cantidad_pagar = fields.Float('Descuento', digits=(32, 2))
    numero = fields.Char('Número')
    
    
    
    
    capital = fields.Float('Capital', digits=(32, 4))
    interes = fields.Float('Interes', digits=(32, 4))
    num_tipo = fields.Char('Número de pago')
    sum_interes_total = fields.Float('Capital/Interes',digits=(32, 2),compute="compute_sum_interes_total")
    saldo = fields.Float('Saldo', digits=(32, 2))
    interes2 = fields.Float('Interes', digits=(32, 2))
    

    @api.depends('capital','interes')
    def compute_sum_interes_total(self):
        for value in self:
            value.sum_interes_total = value.capital + value.interes
    
