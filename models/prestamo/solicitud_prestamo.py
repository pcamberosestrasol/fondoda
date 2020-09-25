from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError
from datetime import datetime, date, time, timedelta
import calendar

import logging
_logger = logging.getLogger(__name__)



class FondodaPrestamo(models.Model):
    _name = 'fondoda.prestamo'
    _rec_name = 'name'
    _inherit = ['mail.thread','mail.activity.mixin']

    name = fields.Char('Folio',default='Nuevo')
    partner_id = fields.Many2one('res.partner','Colaborador',default=lambda self: self.env.user.partner_id)
    prestamos_activos = fields.Boolean('¿Tienes prestamos activos?',compute="verify_prestamos" )
    cantidad = fields.Float('Cantidad solicitada',digits=(32, 2),default=1000)
    cantidad_letra = fields.Char('Cantidad solicitada',default='Mil pesos')
    pagos = fields.Integer('Número de pagos')
    descuento = fields.Selection([
        ('semanal', 'Semanal'),
        ('quincena', 'Quincenal'),
        ('mensual','Mensual')],
        'Tipo descuento',related='partner_id.payroll',)
    monto = fields.Float('Monto de los descuentos',compute='compute_total_monto',digits=(32, 2))
    interes = fields.Float('Interés(%)',default=12.00)
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
    total_pago = fields.Float('Total',compute='compute_total_pay')
    tipo = fields.Selection([('ordinario', 'Ordinario'),('extra', 'Extraordinario')])
    interes_generado = fields.Float('Interes generado',compute="compute_total_interes")
    motivo = fields.Selection([('muerte', 'Muerde de Familiar Directo'),('accidente','Accidente')])


    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).estatus.selection]

    @api.depends('cantidad','interes')
    def compute_total_interes(self):
        for p in self:
            p.interes_generado = p.cantidad * (p.interes/100)
            

    @api.depends('cantidad','interes','pagos_ids')
    def compute_total_pay(self):
        for p in self:
            pagado = 0
            if p.pagos_ids:
                for pagos in p.pagos_ids:
                    pagado+=pagos.cantidad_pagada
            p.total_pago = p.cantidad + (p.cantidad * (p.interes/100)) - pagado

    @api.depends('total_pago','pagos','cantidad','interes')
    def compute_total_monto(self):
        for prestamo in self:
            total = prestamo.cantidad + (prestamo.cantidad * (prestamo.interes/100))
            if prestamo.pagos > 0:
                prestamo.monto = total/prestamo.pagos
            else:
                prestamo.monto = total


    @api.depends('partner_id','estatus')
    def verify_prestamos(self):
        for p in self:
            if p.partner_id and p.partner_id.prestamos_id:
                p_value = p.partner_id.prestamos_id.filtered(lambda x: x.estatus == '2')
                if len(p_value)>1:
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
        previo_estatus = self.estatus
        res = super(FondodaPrestamo, self).write(vals)
        if 'estatus' in vals:
            if self.aceptar == False and self.estatus == '2':
                raise ValidationError(('El colaborador no ha aceptado el reglamento,favor de aceptar el reglamento para continuar con el proceso'))
            elif self.prestamos_activos == True and self.tipo == 'ordinario' and self.estatus == '2':
                raise ValidationError(('El colaborador cuenta con un préstamo activo'))
            elif previo_estatus == '3' and self.estatus == '2':
                raise ValidationError(('No puede cambiar el estatus de una solicitud que ya ha sido pagada'))
            else:
                return res
        else:
            return res
    

    def autorizar(self):
        self.estatus = '2'
        self.create_pagos()
        self.send_mail_aprobado()
    
    def pagado(self):
        self.estatus = '3'
        self.pagar_todo()

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
        self.send_mail_rechazado()
        return {'type': 'ir.actions.act_window_close'}
         

    def cancelar_cambios(self):
        return {'type': 'ir.actions.act_window_close'}

    def create_pagos(self):
        meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
        lista = []
        total = self.total_pago
        interes = self.interes_generado
        capital = self.cantidad
        fecha = fields.Date.today()
        for p in range(self.pagos):
            if self.descuento == 'semanal':
                fecha = fecha +timedelta(days=7)
            elif self.descuento =='quincena':
                day_range = calendar.monthrange(fecha.year,fecha.month)   
                if fecha.day < 15:
                    dias = 15 - fecha.day
                    fecha = fecha +timedelta(days=dias)
                    day_week = calendar.day_name[fecha.weekday()]
                    if day_week == 'Saturday':
                        fecha = fecha-timedelta(days=1)
                    elif day_week == 'Sunday':
                        fecha = fecha-timedelta(days=2)
                    else:
                        pass
                elif fecha.day >=15 and fecha.day < int(day_range[1]):
                    dias = int(day_range[1]) - fecha.day
                    fecha = fecha +timedelta(days=dias)
                    day_week = calendar.day_name[fecha.weekday()]
                    if day_week == 'Saturday':
                        fecha = fecha-timedelta(days=1)
                    elif day_week == 'Sunday':
                        fecha = fecha-timedelta(days=2)
                    else:
                        pass
            elif self.descuento=='mensual':
                day_range: calendar.monthrange(fecha.year,fecha.month)
                if fecha.day < int(day_range[1]):
                    dias = int(day_range[1]) - fecha.day
                    fecha = fecha +timedelta(days=dias)
                    day_week = calendar.day_name[fecha.weekday()]
                    if day_week == 'Saturday':
                        fecha = fecha-timedelta(days=1)
                    elif day_week == 'Sunday':
                        fecha = fecha-timedelta(days=2)
                    else:
                        pass
            
            if p == self.pagos-1:
                lista.append((0,0,{
                    'fecha_pago': fecha,
                    'num_pago': p+1,
                    'prestamo_id': self.id,
                    'cantidad_pagar': total,
                    'day': fecha.day,
                    'month': meses[fecha.month-1],
                    'year': str(fecha.year),
                    'num_tipo': str(p+1)+'-'+self.descuento,
                    'capital': capital,
                    'interes': interes,
                }))
            else:
                lista.append((0,0,{
                    'fecha_pago': fecha,
                    'num_pago': p+1,
                    'prestamo_id': self.id,
                    'cantidad_pagar': self.monto,
                    'day': fecha.day,
                    'month': meses[fecha.month-1],
                    'year': str(fecha.year),
                    'num_tipo': str(p+1)+'-'+self.descuento,
                    'capital': self.cantidad/self.pagos,
                    'interes': self.interes_generado/self.pagos,
                }))
            if fecha.day >15:
                while fecha.day != 1:
                    fecha = fecha+timedelta(days=1)
            total = total - self.monto
            capital = capital - (self.cantidad/self.pagos)
            interes = interes - self.interes_generado/self.pagos
        _logger.info('Resultado = '+str(lista))
        self.pagos_ids = lista
        

    @api.onchange('pagos','descuento')
    def onchange_value_rango(self):
        if self.descuento == 'semanal':
            if self.pagos > 52:
                self.pagos = 52
        if self.descuento == 'quincena':
            if self.pagos > 24:
                self.pagos = 24
        if self.descuento == 'mensual':
            if self.pagos > 12:
                self.pagos = 12
    
    @api.onchange('cantidad')
    def onchange_value_cantidad(self):
        if self.cantidad < 1000:
            self.cantidad = 1000
        
    def pagar_todo(self):
        if self.pagos_ids:
            for p in self.pagos_ids:
                if p.cantidad_pagada == 0:
                    p.cantidad_pagada = p.cantidad_pagar


    def send_mail_aprobado(self):
        mail_search = self.env.ref('fondoda.mail_prestamo_aprobado').id
        template = self.env['mail.template'].browse(mail_search)
        template.send_mail(self.id,force_send=True)

    def send_mail_rechazado(self):
        mail_search = self.env.ref('fondoda.mail_prestamo_rechazado').id
        template = self.env['mail.template'].browse(mail_search)
        template.send_mail(self.id,force_send=True)
