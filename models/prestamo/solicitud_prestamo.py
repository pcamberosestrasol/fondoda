from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

class FondodaPrestamo(models.Model):
    _name = 'fondoda.prestamo'
    _rec_name = 'name'
    _inherit = ['mail.thread','mail.activity.mixin']

    name = fields.Char('Folio',default='Nuevo')
    partner_id = fields.Many2one('res.partner','Colaborador',default=lambda self: self.env.user.partner_id)
    prestamos_activos = fields.Boolean('¿Tienes prestamos activos?')
    cantidad = fields.Float('Cantidad solicitada',digits=(32, 2))
    cantidad_letra = fields.Char('Cantidad solicitada')
    pagos = fields.Integer('Número de pagos')
    descuento = fields.Selection([
        ('semanal', 'Semanal'),
        ('quincena', 'Quincenal'),
        ('mensual','Mensual')],
        'Tipo descuento',related='partner_id.payroll',)
    monto = fields.Float('Monto de los descuentos',compute='compute_total_monto',digits=(32, 2))
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
    aceptar = fields.Boolean('Aceptar terminos y condiciones')
    comentario = fields.Text('Comentario')
    pagos_ids = fields.One2many('fondoda.pagos','prestamo_id',string='Pagos')
    total_pago = fields.Float('Total',compute='compute_total_pay',digits=(32, 2))


    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).estatus.selection]

    @api.depends('cantidad','interes')
    def compute_total_pay(self):
        for p in self:
            p.total_pago = p.cantidad + (p.cantidad * (p.interes/100))

    @api.depends('total_pago','pagos')
    def compute_total_monto(self):
        for p in self:
            p.monto = p.total_pago / p.pagos


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
        vals['name'] = self.env['ir.sequence'].next_by_code('fondoda.folio.sequence')
        res = super(FondodaPrestamo, self).create(vals)
        if res.prestamos_activos == True:
            raise ValidationError(('Error!! No se puede crear la solicitud, debido a que tiene un prestamo activo'))
        else:
            return res
    
    def write(self, vals):
        previos_estatus = self.estatus
        res = super(FondodaPrestamo, self).write(vals)
        if 'estatus' in vals:
            if self.estatus == '2' and self.prestamos_activos == True and self.aceptar == False:
                raise ValidationError(('Error!! No se puede aceptar la solicitud, Puede que tenga un prestamo activo o no haya aceptado los el reglamento del fondo de ahorro'))
            else:
                return res
        else:
            return res
    

    def autorizar(self):
        self.estatus = '2'
        self.create_pagos()

    def rechazar(self):
        self.estatus = '4'
    
    def pagado(self):
        self.estatus = '3'


    def open_wizard_terms(self):
        information = self.env['ir.config_parameter'].sudo().get_param('fondoda.description')
        view = {
            'name': ('Terminos y Condiciones'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fondoda.terms.conditions',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_prestamo_id':self.id,
                'default_description': information
            }
        }
        return view
    
    def rechazo_comentario(self):
        active_ids = self.ids
        if len(active_ids) == 1:
            view_id = self.env.ref('fondoda.prestamo_view_form2').id
            view = {
                'name': ('Motivo por cancelación'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'fondoda.prestamo',
                'views': [(view_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id':self.id,
                'no_create': True
            }
            return view
        else:
            raise ValidationError (('Error!!, solo debe escoger 1 registro para cancelar'))

    
    def guardar_cambios(self):
        self.estatus = '4'
        return {'type': 'ir.actions.act_window_close'}
         

    def cancelar_cambios(self):
        return {'type': 'ir.actions.act_window_close'}

    def create_pagos(self):
        for p in range(self.pagos):
            self.pagos_ids[(0,0,{
                'fecha_pago': self.fecha,
                'num_pago': p,
                'prestamo_id': self.id,
                'cantidad_pagar': self.monto
            })]
        
    
    


    