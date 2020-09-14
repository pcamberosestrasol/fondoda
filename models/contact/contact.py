    # -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
from datetime import datetime,date,time
_logger = logging.getLogger(__name__)




class FondoContact(models.Model):
    
    _inherit = 'res.partner'

    num_colab = fields.Char('Número de colaborador',tracking=True,default=0 )
    father_name = fields.Char('Apellido paterno',tracking=True)
    mother_name = fields.Char('Apellido materno',tracking=True)
    payroll = fields.Selection([
        ('semanal', 'Semanal'),
        ('quincena', 'Quincenal'),
        ('mensual','Mensual')],
        'Tipo de nómina',tracking=True)

    colab_status = fields.Selection([('activo', 'Activo'),('inactivo', 'Inactivo')], 'Estatus',tracking=True)

    benef_firstname = fields.Char('Nombre del beneficiario',tracking=True)
    benef_fathername = fields.Char('Apellido paterno del beneficiario',tracking=True)
    benef_mothername = fields.Char('Apellido materno del beneficiario',tracking=True)
    benef_relation = fields.Char('Parentesco del beneficiario',tracking=True)
    benef_birth = fields.Date('Fecha de nacimiento del beneficiario',tracking=True)
    benef_phone = fields.Char('Número telefónico del beneficiario',tracking=True)

    

    @api.onchange('benef_birth')
    def calculate_age(self):
        if self.benef_birth:
            today = date.today()
            born = self.benef_birth
            age = today.year - born.year-((today.month,today.day) < (born.month,born.day))
            if age < 18:
                self.benef_birth = False
                return {'warning': {
                    'title': "Error Edad",
                    'message': "La fecha de nacimiento no es valida",
                    }
                }

    @api.onchange('num_colab')
    def search_colab(self):
        if self.num_colab:
            colab = self.env['res.partner'].search([('num_colab','=',self.num_colab)])
            if colab.id:
                return {'warning': {
                   'title': "Número de colaborador existente.",
                   'message': "El número de colaborador colocado, ya existe en el sistema.",
                   }
                }
            #else:
                #self.phone = "No existe el número de colab"



            

            

            
        
