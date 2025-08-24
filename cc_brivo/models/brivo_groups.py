import logging
from odoo import models, fields, api
from ..utils.brivo import brivo_list_groups

_logger = logging.getLogger(__name__)

class BrivoGroups(models.Model):
  _name = 'brivo.groups'
  _description = 'Model that syncs with Brivo for listing groups in the system.'
  
  name = fields.Char(readonly=True)
  brivo_group_id = fields.Integer(readonly=True)
  
  @api.model
  def cron_sync_brivo_groups(self):
    '''
       Synchronize groups in Brivo with our system.
    '''
    groups : dict = brivo_list_groups(self.env)
    
    group_id_to_group : dict = { g['id'] : g for g in groups['data'] }
    group_ids : list = [ g['id'] for g in groups['data'] ]
    
    # Erase records that are not found in the Brivo groups
    erase_records = self.search([('brivo_group_id', 'not in', group_ids)])
    erase_records.unlink()
    
    # Create records for Brivo records that do not have a corresponding record
    rec_ids : set = set(self.search([]).mapped('brivo_group_id'))
    
    diff : set = set(group_ids).difference(rec_ids)
    
    _logger.info(f'Brivo Group Sync: Creating records for Brivo Groups: {[ group_id_to_group[gid]['name'] for gid in diff ]}')
    for gid in diff:
      group = group_id_to_group[gid]
      self.create({
        'name': group['name'],
        'brivo_group_id': group['id']
      })