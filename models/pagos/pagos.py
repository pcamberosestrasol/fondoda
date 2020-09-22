from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

class FondodaPagos(models.Model):
    _name = 'fondoda.pagos'

    cantidad_pagada = fields.Float('Pagado')
    fecha_pago = fields.Date('Fecha')
    num_pago = fields.Integer('Número de pago')
    prestamo_id = fields.Many2one('Pestramo')
    cantidad_pagar = fields.Float('Por Pagar')
    numero = fields.Char('Número')