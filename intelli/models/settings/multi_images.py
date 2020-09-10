from odoo import models, fields, api,_
from odoo.exceptions import UserError
import sys
class Images(models.Model):
    _name= 'intelli.images'
    _order = 'sequence, id'
    name = fields.Char("Nombre", required=True)
    sequence = fields.Integer(default=10, index=True)
    image = fields.Image("Imagen")
    parent_blind = fields.Many2one("intelli.blind")
    @api.onchange('image')
    def on_blind(self):
        if sys.getsizeof(self.image)  > 1*1000*1000:      
            raise UserError(_("Exediste el tamaño permitido (1mb/10000) para la imagen ."))