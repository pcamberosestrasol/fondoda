from odoo import models, fields, api,_
from odoo.exceptions import UserError
import sys
class Manual(models.Model):
    _name= 'intelli.pdf'
    name = fields.Char("Nombre", required=True)
    pdf = fields.Binary("Pdf", required=True)