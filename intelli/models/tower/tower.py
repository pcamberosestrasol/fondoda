from odoo import models, fields, api ,_
import logging
_logger = logging.getLogger(__name__)
from odoo.tools.misc import clean_context
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import sys
class Tower(models.Model):
    _name= 'intelli.tower'
    _inherit =  ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
   
    def _get_default_country(self):
        country = self.env['res.country'].search([('code', '=', 'MX')], limit=1)
        return country


    active = fields.Boolean('Active', default=True, track_visibility=True)
    name = fields.Char("Nombre", track_visibility=True,  required=True)
    street = fields.Char("Calle 1",track_visibility=True, size=50, required=True)
    street2 = fields.Char("Calle 2",track_visibility=True, size=50)
    location  = fields.Char("Locación",track_visibility=True, size=30)
    zip = fields.Char("Codigo postal",change_default=True,track_visibility=True, size=10, required=True)
    city = fields.Char("Ciudad",track_visibility=True, size=20, required=True)
    #email = fields.Char("Email")
    state_id = fields.Many2one("res.country.state", string='Estado', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Pais', ondelete='restrict', default=_get_default_country)
    tower_latitude = fields.Float(string='Geo Latitude', digits=(16, 5))
    tower_longitude = fields.Float(string='Geo Longitude', digits=(16, 5))
    #
    instalation_price = fields.Float("Instalación por pieza",digits=(16, 3),track_visibility=True)
    delivery_price = fields.Float("Envio por pieza",digits=(16, 3),track_visibility=True)
    password = fields.Char("Contrato",track_visibility=True, size=20, required=True)
    tower_picture = fields.Image("Producto autorizado",required=True,track_visibility=True)
    background_picture = fields.Image("Imagen fondo",required=True,track_visibility=True)
    logo = fields.Image("Logo",track_visibility=True)
    agent = fields.Many2one('res.partner', string='Agente', index=True,required=True)
    email_agent = fields.Char(related='agent.email', readonly=True, string='Email',track_visibility=True)
    currency_id = fields.Many2one("res.currency", string="Tipo cambio",required=True,track_visibility=True)
    blinds = fields.One2many (comodel_name='intelli.blind',inverse_name='parent_tower',string="Productos")
    departments = fields.One2many (comodel_name='intelli.department',inverse_name='tower',string="Departamentos")
    styles_available =  fields.Many2many(comodel_name='intelli.style', relation='table_search_styles', column1='style_id', column2='tower_id')
    _sql_constraints = [
        ('unique_name', 'unique (name)', 'EL nombre no debe repetirse!')
       
    ]
    @api.constrains('password')
    def _check_passwrod(self):
        if len(self.env['intelli.tower'].search([('password','=',self.password)])) > 1:
            raise ValidationError(_('Ya existe el contrato en otra torre.'))
    #Boton
    def button_blinds(self):
       view_id = self.env.ref('intelli.tower_view_form_associate').id
       view = {
           'name': ('Productos'),
           'view_type': 'form',
           'view_mode': 'form',
           'res_model': 'intelli.tower',
           'views':  [(view_id,'form')],
          'type': 'ir.actions.act_window',
           'target': 'new',
           'context':dict(create = False ),
           'res_id': self.id,
           
       }
       return view 

    def copy(self, default=None):
        self.ensure_one()
        
        news_blind = []
        for blind in self.blinds:
            blind_images = []
            for image in blind.images:
                new_image = image.copy({'parent_blind':False})
                blind_images.append( (4, new_image.id) )
            new_blind = blind.copy({'parent_tower':False})
            if blind.images:
                new_blind.write({'images':blind_images}  )
            news_blind.append( (4, new_blind.id) )
        #new_deps = []
        #for depa in self.departments:
        #    new_depa = depa.copy()
        #    new_deps.append((4,new_depa.id))
        res = super(Tower, self).copy({'name':self.name + "(copia)",'password':self.name + "(copia"})    
        if self.blinds:
            res.write({'blinds':news_blind}  )
        #if self.departments:
        #    res.write({'departments':new_deps}  )
        return res
    def button_duplicate(self):
       self.copy()


    @api.onchange('logo')
    def on_image(self):
        if sys.getsizeof(self.logo)  > 1*1000*1000:      
            raise UserError(_("Exediste el tamaño permitido (1mb/10000) para la imagen ."))
    @api.onchange('tower_picture')
    def on_tower_picture(self):
        if sys.getsizeof(self.tower_picture)  > 1*1000*1000:          
            raise UserError(_("Exediste el tamaño permitido (1mb/10000) para la imagen ."))
    @api.onchange('background_picture')
    def on_background_picture(self):
        if sys.getsizeof(self.background_picture)  > 1*1000*1000:         
            raise UserError(_("Exediste el tamaño permitido (1mb/10000) para la imagen ."))
    @api.onchange('blinds')
    def on_styles_change(self):
        self.styles_available = False
        self.styles_available = [(6, None, [blind.style.id for blind in self.blinds ] )]
        
    """
    def open_one2many_line(self):
        context = self.env.context
        return {
            'type': 'ir.actions.act_window',
            'name': 'Open Line',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': context.get('default_active_id'),
            'target': 'new',
        }}
    """

    def tower_departments(self,password):    
        search = self.env['intelli.tower'].search([('password','=',password)])
        if search :
            search= search[0]
            data = {
                    'id': search['id'], 
                    'name': search['name'],
                    'street' : search['street'], 
                    'street2' : search['street2'],
                    'location'  : search['location'],  
                    'state_id' : search['state_id'].name, 
                    'country_id' : search['country_id'].name, 
                    'instalation_price' : search['instalation_price'], 
                    'delivery_price' : search['delivery_price'], 
                    'password' : search['password'], 
                    'tower_picture' : search['tower_picture'], 
                    'background_picture' : search['background_picture'], 
                    'logo' : search['logo'], 
                    'agent' : search['agent'].name,
                    'email_agent' : search['email_agent'], 
                    'currency_id' : search['currency_id'].name
                
                    }
            ids =  [id.id for id in search['departments'] ]       
            depas = self.env['intelli.department'].search([('id','in',ids)], order="name asc")
            data['departments'] = [
                        {
                            'id':department['id'],           
                            'name':department['name'],
                            'instalation':department['instalation'].name,
                            'map':department['map'],
                            'department_areas':len( department['department_areas']) if department['department_areas'] else "0",
                            

                        } for department in  depas

                        ]
     
        
        return [  
                    {
                        
                            'success': 200 if search else 204,
                            'data':data  if search else "null"
                    }
        ]