from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
from odoo.tools.misc import clean_context
import re
from odoo.exceptions import UserError,ValidationError



class ResPartner(models.Model):
    _inherit = "res.users"

    @api.onchange('login')
    def method_validete_mail(self):
        if self.login:
            mail = self.login
            match = re.match('^[_A-Za-z0-9-]+(\.[_A-Za-z0-9-]+)*@estrasol.com.mx$', mail)
            if match == None:
                self.login = False
                return {'warning': {
                    'title': "Error Correo Electrónico",
                    'message': "El correo electrónico no pertenece a estrasol",
                    }
                }