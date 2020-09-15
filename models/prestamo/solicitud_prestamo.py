from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FondodaPrestamo(models.Model):
    _name = 'fondoda.prestamo'

    name = fields.Char('Nombre')
    partner_id = fields.Many2one('res.partner','Colaborador')
    prestamos_activos = fields.Boolean('¿Tienes prestamos activos?')
    cantidad = fields.Float('Cantidad solicitada',digits=(32, 2))
    cantidad_letra = fields.Char('Cantidad solicitada')
    pagos = fields.Integer('Número de pagos')
    descuento = fields.Selection([
        ('semanal', 'Semanal'),
        ('quincena', 'Quincenal'),
        ('mensual','Mensual')],
        'Tipo descuento',tracking=True,default='quincena')
    monto = fields.Float('Monto de los descuentos',digits=(32, 2))
    interes = fields.Float('Interés(%)')


    