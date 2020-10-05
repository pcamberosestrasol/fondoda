# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.addons.website.tools import get_video_embed_code
import logging
_logger = logging.getLogger(__name__)
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fda_reglamento = fields.Many2one('fondoda.document','Reglamento')


    def get_values(self): 
        res = super(ResConfigSettings, self).get_values()
        res.update(
            fda_reglamento =  int(self.env['ir.config_parameter'].sudo().get_param('fondoda.fda_reglamento'))
        )
        return res
    
    def set_values(self):
        super (ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo() 
        rule = self.fda_reglamento and self.fda_reglamento.id or False
        param.set_param('fondoda.fda_reglamento',rule)
