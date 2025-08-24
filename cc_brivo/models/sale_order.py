import logging
from odoo import models, fields
from ..utils.brivo import brivo_add_to_group, brivo_remove_from_group

_logger = logging.getLogger(__name__)
class SaleOrder(models.Model):
  _inherit = 'sale.order'
  
  brivo_group_id = fields.Many2one('brivo.groups', related='sale_order_template_id.brivo_group_id')
  
  def action_confirm(self, *args, **kwargs):
    '''
      Override action_confirm so that the partner's
      Brivo user is added to the Brivo group corresponding
      to this membership.
    '''
    res = super().action_confirm(*args, **kwargs)
    if self.brivo_group_id and self.partner_id.brivo_id:
      try:
        brivo_add_to_group(self.env, self.brivo_group_id.brivo_group_id, self.partner_id.brivo_id)
      except Exception as err:
        _logger.error(err)
        
    return res
  
  def set_close(self, *args, **kwargs):
    '''
      Override set_close so that the partner's
      Brivo user is removed from the Brivo group corresponding
      with this membership.
    '''
    res = super().set_close(*args, **kwargs)
    if self.brivo_group_id and self.partner_id.brivo_id:
      try:
        brivo_remove_from_group(self.env, self.brivo_group_id.brivo_group_id, self.partner_id.brivo_id)
      except Exception as err:
        _logger.error(err)
        
    return res