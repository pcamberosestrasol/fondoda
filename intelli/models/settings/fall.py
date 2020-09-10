from odoo import models, fields, api
class Fall(models.Model):
    _name= 'intelli.fall'
    _inherit =  ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    active = fields.Boolean('Active', default=True, track_visibility=True)
    name = fields.Char(string ="Nombre", track_visibility=True)
   