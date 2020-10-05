# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class fondodaTerms(models.TransientModel):
    _name = 'fondoda.terms.conditions'

    reglamento = fields.Many2one('fondoda.document')
    document = fields.Binary('Reglamento',compute="show_binary_filed")

    @api.depends('reglamento')
    def show_binary_filed(self):
        for val in self:
            val.document = val.reglamento.archivo



    def cancelar(self):
        return {'type': 'ir.actions.act_window_close'}