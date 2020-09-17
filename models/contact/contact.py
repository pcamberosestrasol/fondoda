    # -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
from datetime import datetime,date,time
_logger = logging.getLogger(__name__)
import re
from odoo.exceptions import UserError,ValidationError

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

    @api.onchange('phone')
    def onchange_phone_verification(self):
        if self.phone:
            telefono = str(self.phone)
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
            if tam_telefono >= 10 and tam_telefono <= 13:
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
            colab = self.num_colab
            colab.replace(" ","")
            temp=list(filter(lambda numero: numero in '0123456789',colab) )
            colab = len(temp)
            caracteres = [numero for numero in str(colab) if not numero in '(0123456789)']
            if caracteres:
                self.num_colab = False
                return {'warning': {
                    'title': "Error Colaborador",
                    'message': "El número colaborador contiene caracteres",
                    }
                }
            #colab = str(self.num_colab)
            #colab.replace(" ","")
            #temp=list(filter(lambda numero: numero in '0123456789',colab) )
            #caracteres = [numero for numero in str(colab) if not numero in '0123456789']
            #colaboradores = self.env['res.partner'].search([('num_colab','=',self.num_colab)])
            #if caracteres or len(colaboradores) > 1:
            #    self.colab=''
            #    return {'warning': {
            #        'title': "Error Colaborador",
            #        'message': "Puede que contenga letras, o el colaborador ya existe",
            #        }
            #    }
    
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
        colab = self.env['res.partner'].search([('num_colab','=',vals['num_colab'])])
        if len(colab) > 1:
            raise ValidationError(('El número de colaborador que intenta agregar ya existe'))
        else:
            return res
    

    def write(self, vals):
        res = super(FondoContact, self).write(vals)
        colab = self.env['res.partner'].search([('num_colab','=',self.num_colab)])
        if len(colab) > 1:
            raise ValidationError(('El número de colaborador que intenta agregar ya existe'))
        else:
            return res