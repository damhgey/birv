import logging
from ..utils.brivo import brivo_auth, brivo_create_group
from ..utils import const
from ...ksc_club_cloud.utils.notifications import NotificationFeedback
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class ClubSystemSettings(models.Model):
  _inherit = 'club.system.settings'
  
  '''
    Brivo API Fields
  '''
  brivo_app_client_id = fields.Char(string='Brivo App Client ID')
  brivo_app_client_secret = fields.Char(string='Brivo App Client Secret')
  brivo_access_username = fields.Char(string='Brivo Admin ID')
  brivo_access_password = fields.Char(string='Brivo Access Pasword')
  brivo_api_key = fields.Char(string='Brivo API Key')
    
  def action_test_brivo_connection(self):
    self.ensure_one()
    
    res = brivo_auth(self.env)
    
    if res.get('status', None) == 'FAILURE':
      return NotificationFeedback.notification_feedback(self.env,
                                                        'Brivo Test Connection',
                                                        'The Brivo test connection failed.',
                                                        'danger')
    else:
      return NotificationFeedback.notification_feedback(self.env,
                                                        'Brivo Test Connection',
                                                        'The Brivo test connection was successful.',
                                                        'success')