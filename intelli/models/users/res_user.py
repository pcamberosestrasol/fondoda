from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
from odoo.tools.misc import clean_context
class ResPartner(models.Model):
    _inherit = "res.partner"
    vat = fields.Char(string='RFC', help="RFC")
  
  