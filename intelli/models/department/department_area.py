from odoo import models, fields, api ,_
import logging
_logger = logging.getLogger(__name__)
from odoo.tools.misc import clean_context
from odoo.exceptions import UserError, ValidationError
import sys
import itertools
from operator import itemgetter
import functools 

class Departent_Area(models.Model):
    _name= 'intelli.department.area'
    _inherit =  ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
   
    def _get_fall(self):
        fall = self.env['intelli.fall'].search([('name', '=', 'No aplica')], limit=1)
        if not fall:
             fall = self.env['intelli.fall'].create({'name':"No aplica"})
        return fall.id 
    def _get_control(self):
        control = self.env['intelli.control'].search([('name', '=', 'No aplica')], limit=1)
        if not control:
             control = self.env['intelli.control'].create({'name':"No aplica"})
        return control.id
    active = fields.Boolean('Active', default=True, track_visibility=True)
    name = fields.Char("Ventana",track_visibility=True, required=True)
    with_w = fields.Float("Ancho",digits=(16, 3),track_visibility=True)
    heigth_h = fields.Float("Alto",digits=(16, 3),track_visibility=True) 
    area = fields.Many2one('intelli.area', string='Area',required=True)
    fall = fields.Many2one('intelli.fall', string='Caída',required=True,default=_get_fall)
    control = fields.Many2one('intelli.control', string='Control',required=True,default=_get_control)
    parent_department = fields.Many2one('intelli.department', string='Departamento',readonly=True,ondelete='cascade' )
    parent_tower =  fields.Many2one(related="parent_department.tower")
    
    

    parent_available = fields.Many2many(related="parent_department.tower.styles_available")
    #blind = fields.Many2one('intelli.blind', string='Cortina',required=True )
    style = fields.Many2one('intelli.style', string='Estilo')
    products_ids = fields.Many2many(comodel_name='intelli.blind', required=True,relation='table_many_products', column1='blind_id', column2='', domain="['&',('parent_tower', '=', parent_tower),('style', '=', style)]")
    flag = fields.Char("Productos", required=True)
    
    @api.constrains('name')
    def _check_name(self):
        if len( self.env['intelli.department.area'].search(['&',('name','=',self.name),'&',('parent_department','=',self.parent_department.id),('area','=',self.area.id)]) ) > 1 :
            raise ValidationError(_('Ya existe el registo con  ventana , no se pueden repetir para este departamento.'))
    def button_duplicate(self):
        self.copy({'name':self.name+"(copia)",'flag':"1" if self.products_ids else False })
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
            'res_id': self.parent_department.id,
            
        }
        return view 
    def button_duplicate_no_open(self):
        self.copy({'name':self.name+"(copia)",'flag':"1" if self.products_ids else False })
        
   
    @api.onchange('style')
    def on_image(self):
       #self.blind = False
       #self.with_w = 0
       #self.heigth_h = 0
       #self.products_ids = False
       if self.products_ids:    
            for product in self.products_ids:
                m2_max = self.with_w * self.heigth_h
                if m2_max > product.m2_max or product.style != self.style :
                    self.products_ids = [(3,product.id)]    
                  
                elif self.with_w > product.with_w or product.style != self.style:
                    self.products_ids = [(3,product.id)]    
                   
                elif self.heigth_h > product.heigth_h or product.style != self.style:      
                    self.products_ids = [(3,product.id)]
            self.flag = "1" if  self.products_ids else False 
       else:
            self.flag = "1" if  self.products_ids else False 
    @api.onchange('with_w','heigth_h')
    def on_size(self):
        if self.products_ids:
           
            for product in self.products_ids:
                m2_max = self.with_w * self.heigth_h
                if m2_max > product.m2_max:
                    self.products_ids = [(3,product.id)]    
                  
                elif self.with_w > product.with_w:
                    self.products_ids = [(3,product.id)]    
                   
                elif self.heigth_h > product.heigth_h:      
                    self.products_ids = [(3,product.id)]    
            self.flag = 1 if  self.products_ids else False
        else:
            self.flag = 1 if  self.products_ids else False


                       

                    
   
   
    @api.onchange('products_ids')
    def on_products_ids(self):
        products_not_a =""
        product_exced_w =""
        product_exced_h =""
        for product in self.products_ids:
           
            m2_max = self.with_w * self.heigth_h
            if m2_max > product.m2_max:
                res = {}
                self.products_ids = [(3,product.id)]    
                products_not_a += product.name+","
            elif self.with_w > product.with_w:
                res = {}
                self.products_ids = [(3,product.id)]    
                product_exced_w += product.name+","
            elif self.heigth_h > product.heigth_h:
                res = {}
                self.products_ids = [(3,product.id)]    
                product_exced_h += product.name+","

        if  products_not_a != "":
            self.flag = "1" if  self.products_ids else False 
            res['warning'] = {
            'title': _('Error'),
            'message': _(' Producto(s) '+products_not_a+' exceden  M2  permitido.'
                                        )   }
            return res
        if  product_exced_w != "":
            self.flag = "1" if  self.products_ids else False 
            res['warning'] = {
            'title': _('Error'),
            'message': _(' Producto(s) '+product_exced_w+' exceden  ancho(W)  permitido. '
                                        )   }
            return res
        if  product_exced_h != "":
            self.flag = "1" if  self.products_ids else False 
            res['warning'] = {
            'title': _('Error'),
            'message': _(' Producto(s) '+product_exced_h+' exceden  alto(H) permitido. '
                                        )   }
            return res  
        self.flag = "1" if  self.products_ids else False                           
           
           
           

    #WS
    def product_areas(self,id):  
       
        search = self.env['intelli.department.area'].search([('parent_department.id','=',id)], order='area asc, style asc ,name asc')
                
        data = []
        for key, group in itertools.groupby(search, key=lambda x:( x['area'], x['style'] ) ):
            new_area = {
                            'area':key[0].name,
                        
                            'style':key[1].name,                    
                       }
            new_area['zones']= [    {
                                        'zone':key_z,
                                        'products': self._get_products(group_z )

                                    }        
                                    for key_z, group_z in itertools.groupby(group, key=lambda x: x['name']  )  ]           
                        
            data.append(new_area)
        
        
        if search :
            data = sorted(data, key = lambda x: (x['area'], x['style']))
            for dat in data:
                dat['zones'] = sorted(dat['zones'], key = lambda x: (x['zone']))
            data_end = {
                    'areas': data, 
                }
            data_end['map'] = search[0].parent_department.map   
            data_end['extra_products'] = []
            ctr_1 = self.env['intelli.blind'].search(['&',('parent_tower.id','=',search[0].parent_tower.id),'&',('electronic.name','like','Control 1 Canal'),('style.name','like','Electrónica')])
            if ctr_1:
               for product in ctr_1: 
                    data_end['extra_products'].append( {
                                                        'parent_department_area': -1  , 
                                                        'product_id': product.id,
                                                        'product':product.name,
                                                        'price': '{0:.2f}'.format(product.price),
                                                        'style':product.style.name,
                                                        'style_id': product.style.id,
                                                        'electronic':product.electronic.name,
                                                        'electronic_id': product.electronic.id,
                                                        'image':product.blind,
                                                        'images':[ image.image for image in product.images ]                   
                                                    }  )
            ctr_2 = self.env['intelli.blind'].search(['&',('parent_tower.id','=',search[0].parent_tower.id),'&',('electronic.name','like','Control 5 Canales'),('style.name','like','Electrónica')])
            if ctr_2:
               for product in ctr_2: 
                    data_end['extra_products'].append( {
                                                        'parent_department_area': -1  , 
                                                        'product_id': product.id,
                                                        'product':product.name,
                                                        'price':'{0:.2f}'.format(product.price),
                                                        'style':product.style.name,
                                                        'style_id': product.style.id,
                                                        'electronic':product.electronic.name,
                                                        'electronic_id': product.electronic.id,
                                                        'image':product.blind,
                                                        'images':[ image.image for image in product.images ]                   
                                                    }  )
            cargador = self.env['intelli.blind'].search(['&',('parent_tower.id','=',search[0].parent_tower.id),'&',('electronic.name','like','Cargador'),('style.name','like','Electrónica')])
            if cargador:
               for product in cargador: 
                    data_end['extra_products'].append( {
                                                        'parent_department_area': -1  , 
                                                        'product_id': product.id,
                                                        'product':product.name,
                                                        'price':'{0:.2f}'.format(product.price),
                                                        'style':product.style.name,
                                                        'style_id': product.style.id,
                                                        'electronic':product.electronic.name,
                                                        'electronic_id': product.electronic.id,
                                                        'actuation':product.actuation.name,
                                                        'actuation_id':product.actuation.id,
                                                        'image':product.blind,
                                                        'images':[ image.image for image in product.images ]                   
                                                    }  )
            inteo = self.env['intelli.blind'].search(['&',('parent_tower.id','=',search[0].parent_tower.id),'&',('electronic.name','like','Interfase'),('style.name','like','Electrónica')])
            if inteo:
               for product in inteo: 
                    data_end['extra_products'].append( {
                                                        'parent_department_area': -1  , 
                                                        'product_id': product.id,
                                                        'product':product.name,
                                                        'price':'{0:,.2f}'.format(product.price),
                                                        'style':product.style.name,
                                                        'style_id': product.style.id,
                                                        'electronic':product.electronic.name,
                                                        'electronic_id': product.electronic.id,
                                                        'actuation':product.actuation.name,
                                                        'actuation_id':product.actuation.id,
                                                        'image':product.blind,
                                                        'images':[ image.image for image in product.images ]                   
                                                    }  )
        
        else: 
           data_end =  "null"     
        
     
        
        return [  
                    {
                        
                            'success': 200 if search else 204,
                            'data': data_end  if search else "null"
                    }
                    ]
    def _get_products(self,group):
         
        all_products = []
        for producs in group:
            parent_department = producs.id
            for product  in producs.products_ids:  
                    total_product =  (producs.with_w*producs.heigth_h*product.price_size) + product.price         
                    all_products.append(
                    {  
                         'parent_department_area':  parent_department  ,  
                         'product_id': product.id,
                         'product':product.name,
                         'price':'{0:,.2f}'.format(total_product),
                         'style':product.style.name,
                         'style_id': product.style.id,
                         'electronic':product.electronic.name,
                         'electronic_id': product.electronic.id,
                         'actuation':product.actuation.name,
                         'actuation_id':product.actuation.id,
                         'image':product.blind,
                         'images':[ image.image for image in product.images ]                   
                    }
                    )
                    
        all_products = sorted(all_products, key = lambda x: (x['product']))
        return all_products
          
