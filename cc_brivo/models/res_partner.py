from odoo import models, fields
from odoo.exceptions import ValidationError

from ..utils.brivo import brivo_create_user, brivo_toggle_suspended_status, brivo_update_user, brivo_create_barcode_credential, brivo_delete_barcode_credential, brivo_assign_credential

class ResPartner(models.Model):
  _inherit = 'res.partner'
  
  '''
    Brivo fields
  '''
  brivo_id = fields.Integer()
  brivo_barcode_credential_id = fields.Integer()
  
  def create(self, vals):
    '''
      Override account creation so that a brivo user is 
      created along with this user.
    '''
    res = super().create(vals)
    
    res._create_brivo_user()
    
    return res
  
  def write(self, vals):
    '''
      Override account editing so that the brivo user
      is edited along with this user.
    '''
    res = super().write(vals)
    
    if not self.env.context.get('skip_brivo_call_on_write', False) and self.active:  
      if self.brivo_id:
        brivo_update_user(self.env, self)
      else:
        self._create_brivo_user()
        
    # If the user's barcode was updated, 
    # update the Brivo user's credential
    if vals.get('barcode') and self:
      self._update_user_barcode_credential()
    
    return res
  
  def action_archive(self, *args, **kwargs):
    res = super().action_archive(*args, **kwargs)
    if self.brivo_id:
      brivo_toggle_suspended_status(self.env, self.brivo_id, True)
    return res
  
  def action_manage_suspended_status(self):
    self.ensure_one()
    
    return {
      'name': 'Manage Suspended Status',
      'type': 'ir.actions.act_window',
      'view_id': self.env.ref('cc_brivo.manage_suspended_status_wizard').id,
      'view_mode': 'form',
      'res_model': 'manage.suspended.status.wizard',
      'target': 'new',
      'context': {
        'default_partner_id': self.id
      }
    }
  
  def _create_brivo_user(self):
    # create a user counterpart
    brivo_res = brivo_create_user(self.env, self)  
    
    if brivo_res.get('status', None) == 'FAILURE':
      raise ValidationError('Cannot create user on Brivo!')
    
    self.with_context(skip_brivo_call_on_write=True).brivo_id = brivo_res['id']
    # create a barcode credential
    self._create_user_credential()
    
  def _create_user_credential(self):
    '''
      Create and assign a user credential
    '''
    # create a barcode credential
    barcode_res = brivo_create_barcode_credential(self.env, self.barcode)
    
    if barcode_res.get('status', None) == 'FAILURE':
      raise ValidationError('Cannot create user credential on Brivo!')
    
    self.with_context(skip_brivo_call_on_write=True).brivo_barcode_credential_id = barcode_res
    # assign credential to user
    assign_res = brivo_assign_credential(self.env, self.brivo_id, barcode_res['id'])
    
    if assign_res.get('status', None) == 'FAILURE':
      raise ValidationError('Cannot assign credential to user on Brivo!')
    
  def _update_user_barcode_credential(self):
    # Delete the user's current credential
    brivo_delete_barcode_credential(self.env, self.brivo_barcode_credential_id)
    # Assign the user a new credential based on their barcode
    self._create_user_credential()