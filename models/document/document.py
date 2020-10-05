# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
from datetime import datetime,date,time
_logger = logging.getLogger(__name__)
import re
from odoo.exceptions import UserError,ValidationError

class FondoDocument(models.Model):
    _name = 'fondoda.document'
    _rec_name = 'nombre'

    nombre = fields.Char('Nombre')
    archivo = fields.Binary('Documento')


    def cancelar(self):
        return {'type': 'ir.actions.act_window_close'}