from odoo import models, fields
from ...ksc_club_cloud.utils.notifications import NotificationFeedback
from ..utils.brivo import brivo_query_suspended_status, brivo_toggle_suspended_status

class ManageSuspendedStatusWizard(models.TransientModel):
  _name = 'manage.suspended.status.wizard'
  _description = 'Wizard for managing the suspended status of Brivo users'
  
  partner_id = fields.Many2one('res.partner', string='Member')
  is_brivo_suspended = fields.Boolean()
  
  def default_get(self, default_vals):
    '''
      Query the suspended status of the customer on Brivo and populate
      `is_brivo_suspended`.
    '''
    res = super().default_get(default_vals)
    
    partner = self.env['res.partner'].browse(self.env.context.get('default_partner_id'))
    susp_query = brivo_query_suspended_status(self.env, partner.brivo_id)
    
    res['is_brivo_suspended'] = susp_query['suspended']
    
    return res

  def action_toggle_suspension(self):
    '''
      Make a call to toggle the suspended status of the Brivo user, and
      then return a success notification.
    '''
    brivo_toggle_suspended_status(self.env, self.partner_id.brivo_id, not self.is_brivo_suspended)
    
    return NotificationFeedback.notification_feedback(self.env,
                                                      'Suspension Toggle Successful!',
                                                      'The user\'s suspension status was successfully changed.',
                                                      'success')