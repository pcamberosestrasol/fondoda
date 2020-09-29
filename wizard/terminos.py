# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class fondodaTerms(models.TransientModel):
    _name = 'fondoda.terms.conditions'

    reglamento = fields.Many2one('ir.attachment')
    document = fields.Binary('Reglamento')

    @api.depends('reglamento')
    def show_binary_filed(self):
        for val in self:
            self.document = self.reglamento.datas


    def aceptar_terminos_condicones(self):
        self.prestamo_id.aceptar = True

    def cancelar(self):
        return {'type': 'ir.actions.act_window_close'}