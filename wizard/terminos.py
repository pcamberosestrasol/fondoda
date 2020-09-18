# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class fondodaTerms(models.TransientModel):
    _name = 'fondoda.terms.conditions'

    prestamo_id = fields.Many2one('fondoda.prestamo')
    description = fields.Html('Description')



    def aceptar_terminos_condicones(self):
        self.prestamo_id.aceptar = True

    def cancelar(self):
        return {'type': 'ir.actions.act_window_close'}