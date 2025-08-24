from odoo import models, fields

'''
  Overrides the sale order template model to support Brivo-related features.
'''
class SaleOrderTemplate(models.Model):
  _inherit = 'sale.order.template'
  
  '''
    Brivo Fields
  '''
  brivo_group_id = fields.Many2one('brivo.groups')
  
  def action_open_assign_brivo_group_wizard(self):
    self.ensure_one()
    
    return {
      'name': 'Assign Brivo Group',
      'type': 'ir.actions.act_window',
      'view_id': self.env.ref('cc_brivo.assign_brivo_group_wizard').id,
      'view_mode': 'form',
      'res_model': 'assign.brivo.group.wizard',
      'target': 'new',
      'context': {
        'default_sale_order_template_id': self.id
      }
    }