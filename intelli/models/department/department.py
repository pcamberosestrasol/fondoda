from odoo import models, fields, api ,_
import logging
_logger = logging.getLogger(__name__)
from odoo.tools.misc import clean_context
from odoo.exceptions import UserError
import sys
class Department(models.Model):
    _name= 'intelli.department'
    _inherit =  ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
   
    def _get_instalation(self):
        instalation = self.env['intelli.instalation'].search([('name', '=', 'No aplica')], limit=1)
        if not instalation:
             instalation = self.env['intelli.instalation'].create({'name':"No aplica"})
        return instalation.id

    active = fields.Boolean('Active', default=True, track_visibility=True)
    name = fields.Char("Departamento", track_visibility=True, required=True)
    map = fields.Image("Plano",track_visibility=True)
    instalation = fields.Many2one('intelli.instalation', string='Instalación', required=True, default=_get_instalation)
    tower = fields.Many2one('intelli.tower', string='Torre', required=True,ondelete='cascade')
    count_areas = fields.Integer("Areas",compute='_compute_areas')
    department_areas = fields.One2many (comodel_name='intelli.department.area',inverse_name='parent_department',string="Areas")
    #_sql_constraints = [
    #    ('unique_name_', 'unique (name)', 'EL nombre no debe repetirse!')
    #   
    #]
    _sql_constraints = [
        ('name_tower', 'unique ( name, tower)', 'No se puede tener torre y departamento con el mismo nombre'),
    ]

    #Boton
    def button_areas(self):
       view_id = self.env.ref('intelli.department_view_form_associate').id
       view = {
           'name': ('Areas'),
           'view_type': 'form',
           'view_mode': 'form',
           'res_model': 'intelli.department',
           'views':  [(view_id,'form')],
          'type': 'ir.actions.act_window',
           'target': 'new',
           'context':dict(create = False ),
           'res_id': self.id,
           
       }
       return view 

    def copy(self, default=None):
        self.ensure_one()
        res = super(Department, self).copy({'name':self.name + "(copia)"})
        
        news_area = []
        for area in self.department_areas:    
            new_area = area.copy({'parent_department':res.id})
            

            news_area.append( (4, new_area.id) )
        if self.department_areas:
            res.write({'department_areas':news_area}  )
        return res
    
    def button_duplicate(self):
       self.copy()
    def button_open(self):
        view_id = self.env.ref('intelli.department_area_view_tree').id
        view_form = self.env.ref('intelli.department_area_view_form').id
        view = {
            'name': ('Areas'),
            'view_type': 'form',
             'view_mode': 'tree,form',
            'res_model': 'intelli.department.area',
            'views':  [(view_id,'tree'),(view_form,'form')],
            'target': 'current',
            'type': 'ir.actions.act_window',
            'context':dict(create = True, default_parent_department = self.id ),
            'domain': [('parent_department','=',self.id)]
            
            
        }
        return view 

    """   
     def write(self,vals):
        if 'name' in vals:
            duplicate = self.env['intelli.department'].search(['&',('tower','=',self.tower.id),('name','=',vals['name'])] )
            if duplicate:
                 raise UserError(_("Existe departamento con el mismo nombre."))   
        return super(Department, self).write(vals)
    def create(self,vals):
        if 'name' in vals:
            duplicate = self.env['intelli.department'].search(['&',('tower','=',vals['tower']),('name','=',vals['name'])] )
            if duplicate:
                 raise UserError(_("Existe departamento con el mismo nombre.")) 
        return super(Department, self).create(vals)
    """
    @api.onchange('map')
    def on_image(self):
        if sys.getsizeof(self.map)  > 1*1000*1000:      
            raise UserError(_("Exediste el tamaño permitido (1mb/10000) para la imagen ."))
   
    @api.onchange('tower')
    def on_tower(self):
       self.department_areas = False 

    
    @api.depends( 'department_areas')
    def _compute_areas(self):
        for item in self:
            item.count_areas = len(item.department_areas)

