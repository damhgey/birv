import logging
from odoo import models, fields
from ...ksc_club_cloud.utils.notifications import NotificationFeedback
from ..utils.brivo import brivo_remove_from_group, brivo_add_to_group

_logger = logging.getLogger(__name__)

class AssignBrivoGroupWizard(models.TransientModel):
  _name = 'assign.brivo.group.wizard'
  _description = 'Wizard for selecting a Brivo group to link to a membership.'
  
  sale_order_template_id = fields.Many2one('sale.order.template', string='Membership')
  brivo_group_id = fields.Many2one('brivo.groups')
  
  def action_confirm(self):
    '''
      Transfer members with this membership from an old brivo group 
      to the one selected. Then, link the brivo group to the membership.
    '''
    
    old_brivo_group = self.sale_order_template_id.brivo_group_id.brivo_group_id
    members = self.env['sale.order'].search([
      ('subscription_state', '=', '3_progress'),
      ('sale_order_template_id', '=', self.sale_order_template_id.id),
      ('partner_id.brivo_id', '!=', False)
      ]).mapped('partner_id')
    
    # Remove members from the old brivo group, then add them
    # to the new brivo group.
    _logger.info(f'Assign Brivo Group Wizard: Assigning {members.mapped('name')} to the new group')
    for m in members:
      if old_brivo_group:
        brivo_remove_from_group(self.env, old_brivo_group, m.brivo_id)
        
      brivo_add_to_group(self.env, self.brivo_group_id.brivo_group_id, m.brivo_id)
    
    # Set the brivo group on the membership
    self.sale_order_template_id.brivo_group_id = self.brivo_group_id
    
    return NotificationFeedback.notification_feedback(self.env,
                                                      'Brivo Group Reassignment Successful',
                                                      'Successfully reassigned Brivo group.',
                                                      'success')