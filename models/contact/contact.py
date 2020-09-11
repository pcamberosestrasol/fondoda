    # -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
from datetime import datetime,date,time
_logger = logging.getLogger(__name__)




class FondoContact(models.Model):
    
    _inherit = 'res.partner'

    num_colab = fields.Integer('Número de colaborador',tracking=True,default=0 )
    father_name = fields.Char('Apellido paterno',tracking=True)
    mother_name = fields.Char('Apellido materno',tracking=True)
    payroll = fields.Selection([
        ('semanal', 'Semanal'),
        ('quincena', 'Quincenal'),
        ('mensual','Mensual')],
        'Tipo de nómina',tracking=True)

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
            born = self.benef_birtdate
            age = today.year - born.year-((today.month,today.day) < (born.month,born.day))
            if age < 18:
                self.benef_birth = False
            else:
                return {'warning': {
                    'title': "Error Edad",
                    'message': "La fecha de nacimiento no es valida",
                    }
                }
