# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.addons.website.tools import get_video_embed_code
import logging
_logger = logging.getLogger(__name__)
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    url_video = fields.Char("Url youtube")
    embed_code = fields.Char(compute="_compute_embed_code")
    pdf_manual = fields.Char("Url youtube")
    pdf_m = fields.Many2one("intelli.pdf","Pdf")
    description = fields.Html('Description')
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        _logger.info("-----------------------------------"+str(self.env['ir.config_parameter'].sudo().get_param('intelli.pdf_m')))
        res.update(
            url_video = self.env['ir.config_parameter'].sudo().get_param('intelli.url_video'),
            pdf_m = int(self.env['ir.config_parameter'].sudo().get_param('intelli.pdf_m')),
             description = (self.env['ir.config_parameter'].sudo().get_param('intelli.description'))
          
        )
        return res

    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        url_video = self.url_video or False
        description = self.description or False
        pdf_m = self.pdf_m and self.pdf_m.id or False
        param.set_param('intelli.url_video', url_video)
        param.set_param('intelli.pdf_m', pdf_m)
        param.set_param('intelli.description', description)
    
    @api.depends('url_video')
    def _compute_embed_code(self):
        for image in self:
            image.embed_code = get_video_embed_code(image.url_video)
            #help help dsd