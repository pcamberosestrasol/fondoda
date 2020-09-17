from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

class FondodaPrestamo(models.Model):
    _name = 'fondoda.prestamo'

    name = fields.Char('Nombre')
    partner_id = fields.Many2one('res.partner','Colaborador',default=lambda self: self.env.user.partner_id)
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
    estatus = fields.Selection([
        ('solicitud', 'Solicitud'),
        ('aceptada', 'Aceptada'),
        ('rechazada','Rechazada'),
        ('pagado','Pagado')],
        string='Estatus')

    @api.depends('cantidad','prestamos','pagos','interes')
    def compute_total_descuento(self):
        for sp in self:
            if sp.prestamos_activos == False:
                total = sp.cantidad + (sp.cantidad/(sp.interes/100))
                sp.descuento = total/sp.pagos


    @api.depends('partner_id','estatus')
    def verify_prestamos(self):
        for p in self:
            if p.partner_id and p.partner_id.prestamos_id:
                p_value = p.partner_id.prestamos_id.filtered(lambda x: x.estatus == 'aceptada')
                if p_value:
                    p.prestamos_activos = True
                else:
                    p.prestamos_activos = False
            else:
                p.prestamos_activos = False


    @api.model
    def create(self, vals):
        res = super(FondodaPrestamo, self).create(vals)
        if res.prestamos_activos == True:
            raise ValidationError(('Error!! No se puede crear la solicitud, debido a que tiene un prestamo activo'))
        else:
            return res
    
    def write(self, vals):
        res = super(FondodaPrestamo, self).write(vals)
        if 'estatus' in vals:
            if self.estatus == 'aceptada' and self.prestamos_activos == True:
                raise ValidationError(('Error!! No se puede aceptar la solicitud, debido a que tiene un prestamo activo'))
            else:
                return res
        else:
            return res
                