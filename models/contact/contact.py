# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime,date,time
import re
from odoo.exceptions import UserError,ValidationError
import logging
_logger = logging.getLogger(__name__)

class FondoContact(models.Model):
    
    _inherit = 'res.partner'

    num_colab = fields.Char('Número de colaborador',tracking=True,default='0' )
    father_name = fields.Char('Apellido paterno',tracking=True)
    mother_name = fields.Char('Apellido materno',tracking=True)
    payroll = fields.Selection([
        ('semanal', 'Semanal'),
        ('quincena', 'Quincenal'),
        ('mensual','Mensual')],
        'Tipo de nómina',tracking=True,default='quincena')

    colab_status = fields.Selection([('activo', 'Activo'),('inactivo', 'Inactivo')], 'Estatus',tracking=True)

    benef_firstname = fields.Char('Nombre del beneficiario',tracking=True)
    benef_fathername = fields.Char('Apellido paterno del beneficiario',tracking=True)
    benef_mothername = fields.Char('Apellido materno del beneficiario',tracking=True)
    benef_relation = fields.Char('Parentesco del beneficiario',tracking=True)
    benef_birth = fields.Date('Fecha de nacimiento del beneficiario',tracking=True)
    benef_phone = fields.Char('Número telefónico del beneficiario',tracking=True)
    is_colaborator = fields.Boolean('Colaborador',compute='define_type_of_user',store=True,)
    prestamos_id = fields.One2many('fondoda.prestamo','partner_id',string='Prestamos',readonly=True)
    doc = fields.Binary('Solicitud de alta')
    fecha_alta = fields.Date('Fecha de alta del IMSS',default=fields.Date.today())

    @api.onchange('benef_birth')
    def calculate_age(self):
        if self.benef_birth:
            today = date.today()
            born = self.benef_birth
            age = today.year - born.year-((today.month,today.day) < (born.month,born.day))
            if age < 18:
                self.benef_birth = False
                return {'warning': {
                    'title': "Error",
                    'message': "La fecha de nacimiento no es válida",
                    }
                }

    @api.onchange('phone')
    def verify_phone_number(self):
        if self.phone:
            telefono = str(self.phone)
            telefono.replace(" ","")
            _logger.info(telefono)
            temp = list(filter(lambda numero: numero in '0123456789',telefono))
            len_phone = len(temp)
            caracteres = [numero for numero in str(telefono) if not numero in '+-(0123456789)']
            _logger.info(str(caracteres))
            if caracteres:
                self.phone = False
                return {'warning': {
                    'title': "Error Teléfono",
                    'message': "No se permite el uso de letras",
                    }
                }
            if len_phone >= 10 and len_phone <= 13:
                pass
            else:
                return {'warning': {
                    'title': "Error Teléfono",
                    'message': "Favor de introducir un numero con al menos 10 caracteres",
                    }
                }


    @api.onchange('benef_phone')
    def onchange_phone_verification(self):
        if self.benef_phone:
            telefono = str(self.benef_phone)
            telefono.replace(" ","")
            temp=list(filter(lambda numero: numero in '0123456789',telefono) )
            tam_telefono = len(temp)
            caracteres = [numero for numero in str(telefono) if not numero in '+-(0123456789)']
            if caracteres:
                self.phone=False
                return {'warning': {
                    'title': "Error Teléfono",
                    'message': "No se permite el uso de letras",
                    }
                }
            if tam_telefono >= 10 and tam_telefono <= 15:
                pass
            else:
                return {'warning': {
                    'title': "Error Teléfono",
                    'message': "Favor de introducir un numero con al menos 10 caracteres",
                    }
                }

    

    @api.onchange('email')
    def method_validete_mail(self):
        if self.email:
            mail = self.email
            match = re.match('^[_A-Za-z0-9-]+(\.[_A-Za-z0-9-]+)*@estrasol.com.mx$', mail)
            if match == None:
                self.email = False
                return {'warning': {
                    'title': "Error Correo Electrónico",
                    'message': "El correo electrónico no pertenece a estrasol",
                    }
                }

    @api.onchange('num_colab')
    def onchange_colab_verification(self):
        if self.num_colab:
            colab = self.convert_int(self.num_colab)
            if colab == True:
                pass
            else:
                self.num_colab = False
                return {'warning': {
                    'title': "Error Colaborador",
                    'message': "El número colaborador contiene caracteres",
                    }
                }
    def convert_int(self,texto):
        try:
            int(texto)
            return True
        except ValueError:
            return False
    
    @api.depends('user_ids','active')
    def define_type_of_user(self):
        for res in self:
            if res.active == True and res.user_ids:
                res.is_colaborator = True
            else:
                res.is_colaborator = False


    @api.model
    def create(self, vals):
        res = super(FondoContact, self).create(vals)
        colab = self.env['res.partner'].search([('num_colab','=',vals['num_colab']),('is_company','=',False)])
        if len(colab) > 1:
            raise ValidationError(('El número de colaborador que intenta agregar ya existe'))
        else:
            return res
    

    def write(self, vals):
        res = super(FondoContact, self).write(vals)
        colab = self.env['res.partner'].search([('num_colab','=',self.num_colab)])
        if len(colab) > 1:
            raise ValidationError(('El número de colaborador que intenta utilizar ya existe'))
        else:
            return res
    

    def name_get(self):
        result = []
        for record in self:
            if record.father_name and record.mother_name:
                name = '%s %s %s' % (record.name, record.father_name, record.mother_name)
                result.append((record.id, name))
            elif not record.father_name and not record.mother_name:
                result.append((record.id, record.name))
            elif not record.mother_name:
                name = '%s %s' % (record.name, record.father_name)
                result.append((record.id, name))
            else:
                result.append((record.id, record.name))
        return result
    
    
    def send_solicitud_alta(self):
        if self.email:
            mail_search = self.env.ref('fondoda.mail_solicitud_colab').id
            template = self.env['mail.template'].browse(mail_search)
            template.send_mail(self.id,force_send=True)
        else:
            raise ValidationError(('Error!! El usuario no cuenta con correo electronico, favor de agregar uno'))
   