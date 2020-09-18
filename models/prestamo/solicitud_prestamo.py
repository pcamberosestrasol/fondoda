from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

class FondodaPrestamo(models.Model):
    _name = 'fondoda.prestamo'
    _rec_name = 'name'
    _inherit = ['mail.thread','mail.activity.mixin']

    name = fields.Char('Folio')
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
        ('1', 'Pendiente'),
        ('2', 'Activo'),
        ('3', 'Pagado'),
        ('4', 'Rechazado')],
        group_expand='_expand_states', index=True,
        default='1',
        string='Estatus')
    num_colab = fields.Char(related='partner_id.num_colab',string='Número empleado')
    fecha = fields.Date('Fecha',default=fields.Date.today())


    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).estatus.selection]

    @api.depends('cantidad','prestamos_activos','pagos','interes')
    def compute_total_descuento(self):
        for sp in self:
            if sp.prestamos_activos == False:
                total = sp.cantidad + (sp.cantidad/(sp.interes/100))
                sp.descuento = total/sp.pagos


    @api.depends('partner_id','estatus')
    def verify_prestamos(self):
        for p in self:
            if p.partner_id and p.partner_id.prestamos_id:
                p_value = p.partner_id.prestamos_id.filtered(lambda x: x.estatus == '2')
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
        previos_estatus = self.estatus
        res = super(FondodaPrestamo, self).write(vals)
        if 'estatus' in vals:
            if self.estatus == '2' and self.prestamos_activos == True:
                raise ValidationError(('Error!! No se puede aceptar la solicitud, debido a que tiene un prestamo activo'))
            else:
                return res
        else:
            return res
    

    def autorizar(self):
        self.estatus = '2'

    def rechazar(self):
        self.estatus = '4'
    
    def pagado(self):
        self.estatus = '3'