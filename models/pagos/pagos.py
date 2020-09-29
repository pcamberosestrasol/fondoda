from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

class FondodaPagos(models.Model):
    _name = 'fondoda.pagos'


    cantidad_pagada = fields.Float('Pagado', digits=(32, 2))
    fecha_pago = fields.Date('Fecha')
    num_pago = fields.Integer('Número de pago')
    prestamo_id = fields.Many2one('fondoda.prestamo','Pestramo')
    cantidad_pagar = fields.Float('Por Pagar', digits=(32, 2))
    numero = fields.Char('Número')
    day = fields.Integer('Día')
    month = fields.Char('Mes')
    year = fields.Char('Año')
    cantidad_letra = fields.Char('Cantidad')
    capital = fields.Float('Capital', digits=(32, 2))
    interes = fields.Float('Interes', digits=(32, 2))
    num_tipo = fields.Char('Número de pago')