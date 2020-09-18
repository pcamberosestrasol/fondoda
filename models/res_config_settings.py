# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.addons.website.tools import get_video_embed_code
import logging
_logger = logging.getLogger(__name__)
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    
    description = fields.Html('Description')
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            description = (self.env['ir.config_parameter'].sudo().get_param('fondoda.description'))
        )
        return res

    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        description = self.description or False
        param.set_param('intelli.description', description)
   