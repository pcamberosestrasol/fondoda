# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.addons.website.tools import get_video_embed_code
import logging
_logger = logging.getLogger(__name__)
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    
    reglamento = fields.Many2one('fondoda.document')
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            reglamento = (self.env['ir.config_parameter'].sudo().get_param('fondoda.reglamento'))
        )
        return res

    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        reglamento = self.reglamento or False
        param.set_param('fondoda.reglamento', reglamento)
   