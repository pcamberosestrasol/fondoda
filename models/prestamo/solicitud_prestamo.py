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
    prestamos_activos = fields.Boolean('¿Tienes prestamos activos?',compute="verify_prestamos")
    cantidad = fields.Float('Cantidad solicitada',digits=(32, 2),default=1000)
    cantidad_letra = fields.Char('Cantidad solicitada',default='Mil pesos mexicanos')
    pagos = fields.Integer('Número de pagos', default=1)
    descuento = fields.Selection([
        ('semanal', 'Semanal'),
        ('quincena', 'Quincenal'),
        ('mensual','Mensual')],
        'Tipo descuento',related='partner_id.payroll',)
    monto = fields.Float('Monto de los descuentos',compute='compute_total_monto',digits=(32, 2))
    interes = fields.Float('Interés(%)',default=12.00,digits=(32, 2))
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

    comentario = fields.Text('Comentario')
    pagos_ids = fields.One2many('fondoda.pagos','prestamo_id',string='Pagos')
    total_pago = fields.Float('Total',compute='compute_total_pay',digits=(32, 2))
    tipo = fields.Selection([('ordinario', 'Ordinario'),('extra', 'Extraordinario')])
    motivo = fields.Selection([('muerte', 'Muerte de Familiar Directo'),('accidente','Accidente')])
    evidencia = fields.Boolean('Evidencia entregada')

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).estatus.selection]

    
    @api.depends('cantidad','pagos_ids')
    def compute_total_pay(self):
        for p in self:
            pagado = 0
            monto = 0
            interes2 = 0
            if p.pagos_ids:
                for pagos in p.pagos_ids:
                    pagado+=pagos.cantidad_pagada
                    monto+= pagos.cantidad_pagar
                    interes2 += pagos.interes2
                p.total_pago = monto - pagado - interes2
            else:
                p.total_pago = p.cantidad

    @api.depends('pagos_ids')
    def compute_total_monto(self):
        for prestamo in self:
            if prestamo.pagos_ids:
                pagar = 0
                for pago in prestamo.pagos_ids:
                    pagar+= pago.sum_interes_total
                prestamo.monto = (pagar/prestamo.pagos)
                for p in prestamo.pagos_ids:
                    p.cantidad_pagar = prestamo.monto
            else:
                prestamo.monto = 0


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
            raise ValidationError(('Error!! No se puede crear la solicitud, debido a que tiene un préstamo activo'))
        else:
            alta = res.partner_id.fecha_alta+timedelta(days=90)
            _logger.info('Alta = '+str(alta))
            if alta < date.today():
                return res
            else:
                raise ValidationError(('Debe tener al menos 3 meses que lo dieron de alta en el IMSS para poder solicitar un préstamo'))
    
    def write(self, vals):
        previo_estatus = self.estatus
        res = super(FondodaPrestamo, self).write(vals)
        if 'estatus' in vals:
            if self.prestamos_activos == True and self.tipo == 'ordinario' and self.estatus == '2':
                raise ValidationError(('El colaborador cuenta con un préstamo activo'))
            elif previo_estatus == '3' and self.estatus == '2':
                raise ValidationError(('No puede cambiar el estatus de una solicitud que ya ha sido pagada'))
            else:
                return res
        else:
            return res
    

    def autorizar(self):
        if self.pagos > 0:
            self.estatus = '2'
            self.create_pagos()
            self.send_mail_aprobado()
        else:
            raise ValidationError(('No se puede aprobar, no cuenta con algún número de pagos'))
        
    
    def pagado(self):
        self.estatus = '3'
        self.pagar_todo()

    def open_wizard_terms(self):
        information = int(self.env['ir.config_parameter'].sudo().get_param('fondoda.fda_reglamento'))
        view_id = self.env.ref('fondoda.document_view_form2').id
        view = {
            'name': ('Reglamento Fondo de Ahorro'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fondoda.document',
            'views':[(view_id,'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': information,
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
        capital = self.cantidad
        fecha = fields.Date.today()
        for p in range(self.pagos):
            if self.descuento == 'semanal':
                fecha = fecha +timedelta(days=7)
            elif self.descuento =='quincena':
                if self.fecha.day == 14 or self.fecha.day == 29:
                    fecha = fecha+timedelta(days=2)
                day_range = calendar.monthrange(fecha.year,fecha.month)
                if fecha.day < 15:
                    dias = 15 - fecha.day
                    fecha = fecha +timedelta(days=dias)
                    day_week = calendar.day_name[fecha.weekday()]
                    if day_week == 'sábado':
                        fecha = fecha-timedelta(days=1)
                    elif day_week == 'domingo':
                        fecha = fecha-timedelta(days=2)
                    else:
                        pass
                elif fecha.day >=15 and fecha.day < int(day_range[1]):
                    dias = int(day_range[1]) - fecha.day
                    fecha = fecha +timedelta(days=dias)
                    day_week = calendar.day_name[fecha.weekday()]
                    if day_week == 'sábado':
                        fecha = fecha-timedelta(days=1)
                    elif day_week == 'domingo':
                        fecha = fecha-timedelta(days=2)
                    else:
                        pass
            elif self.descuento=='mensual':
                day_range: calendar.monthrange(fecha.year,fecha.month)
                if self.fecha.day == 29:
                    fecha = fecha+timedelta(days=2)
                if fecha.day < int(day_range[1]):
                    dias = int(day_range[1]) - fecha.day
                    fecha = fecha +timedelta(days=dias)
                    day_week = calendar.day_name[fecha.weekday()]
                    if day_week == 'sábado':
                        fecha = fecha-timedelta(days=1)
                    elif day_week == 'domingo':
                        fecha = fecha-timedelta(days=2)
                    else:
                        pass
            if p == self.pagos-1:
                lista.append((0,0,{
                    'fecha_pago': fecha,
                    'num_pago': p+1,
                    'num_tipo': str(p+1)+'-'+self.descuento,
                    'prestamo_id':self.id,
                    'day': fecha.day,
                    'month':meses[fecha.month-1],
                    'saldo': capital,
                    'interes': capital*(1/100),
                    'capital': capital 
                }))
            else:
                lista.append((0,0,{
                    'fecha_pago': fecha,
                    'num_pago': p+1,
                    'num_tipo': str(p+1)+'-'+self.descuento,
                    'prestamo_id':self.id,
                    'day': fecha.day,
                    'month':meses[fecha.month-1],
                    'year': str(fecha.year),
                    'saldo': capital,
                    'interes': capital*(1/100),
                    'capital':  self.cantidad/self.pagos
                }))
            if fecha.day >15:
                while fecha.day != 1:
                    fecha = fecha+timedelta(days=1)
            if fecha.day >1 and fecha.day<15:
                 while fecha.day != 15:
                    fecha = fecha+timedelta(days=1)
            
            capital = capital - (self.cantidad/self.pagos)
          
            
           
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
            contador = 0
            for p in self.pagos_ids:
                if p.cantidad_pagada == 0:
                    if contador == 1:
                        p.cantidad_pagada = p.capital
                        p.interes2 = p.cantidad_pagar - p.capital
                    else:
                        p.cantidad_pagada = p.cantidad_pagar
                        contador+=1

    def send_mail_aprobado(self):
        mail_search = self.env.ref('fondoda.mail_prestamo_aprobado').id
        template = self.env['mail.template'].browse(mail_search)
        template.send_mail(self.id,force_send=True)

    def send_mail_rechazado(self):
        mail_search = self.env.ref('fondoda.mail_prestamo_rechazado').id
        template = self.env['mail.template'].browse(mail_search)
        template.send_mail(self.id,force_send=True)


    @api.onchange('cantidad')
    def validasi_form(self):
        if self.cantidad != 1000:
            self.cantidad_letra = ''