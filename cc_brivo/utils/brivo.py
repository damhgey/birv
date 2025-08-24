# All Rights Reserved
# You may not use, distribute and modify this code without the express written consent of clubcloud, LLC. 
import requests
import logging
import base64

_logger = logging.getLogger(__name__)

AUTH_STUB = 'https://auth.brivo.com'
API_STUB = 'https://api.brivo.com'

def brivo_auth(env):
  '''
    Authenticates with Brivo to obtain an authentication token.
    Input:
      env. An object environment.
    Output:
      A response from Brivo.
  '''
  SYSTEM_SETTINGS = env['club.system.settings'].search([], limit=1)
  
  s = f'{SYSTEM_SETTINGS.brivo_app_client_id}:{SYSTEM_SETTINGS.brivo_app_client_secret}'
  client_creds = base64.b64encode(bytes(s, encoding='utf-8')).decode('utf-8')
  
  headers = {
    'Authorization': f'Basic {client_creds}',
    'api-key': SYSTEM_SETTINGS.brivo_api_key,
    'Content-Type': 'application/x-www-form-urlencoded'
  }
  
  data = {
    'grant_type': 'password',
    'username': SYSTEM_SETTINGS.brivo_access_username,
    'password': SYSTEM_SETTINGS.brivo_access_password
  }
  
  return handle_response(requests.post(f'{AUTH_STUB}/oauth/token', data=data, headers=headers))

def _set_api_headers(env):
  '''
    Helper function for setting API headers to make requests to Brivo.
    Input:
      env: An object environment, used to access Odoo models.
    Output:
      An object containing necessary headers for calling to Brivo, including an access token and
      the API key.
  '''
  SYSTEM_SETTINGS = env['club.system.settings'].search([], limit=1)
  auth_res = brivo_auth(env)
  
  if auth_res.get('status', None) == 'FAILURE':
    return auth_res
  
  access_token = auth_res['access_token']
  
  return {
    'Authorization': f'bearer {access_token}',
    'api-key': SYSTEM_SETTINGS.brivo_api_key,
    'Content-Type': 'application/json'
  }

def brivo_create_user(env, partner_rec):
  '''
    Create a Brivo user.
    Input:
      - env. An object environment, passed into `_set_api_headers` to generate the API call headers.
      - partner_rec. A res.partner record.
      
    Output:
      A response from Brivo's API.
  '''
  first_name = partner_rec.name.split(' ')[0]
  last_name = partner_rec.name.split(' ')[1]
  external_id = str(partner_rec.id)
  emails = [{ 'address': partner_rec.email, 'type': 'personal' }] if partner_rec.email else []
  
  body = {
    'firstName': first_name,
    'lastName': last_name,
    'externalId': external_id,
    'emails': emails
  }
  
  headers = _set_api_headers(env)
  
  if headers.get('status', None) == 'FAILURE':
    return headers

  return handle_response(requests.post(f'{API_STUB}/v1/api/users', json=body, headers=headers))

def brivo_delete_user(env, brivo_user_id):
  '''
    Deletes a user from Brivo
  '''
  headers = _set_api_headers(env)
  
  if headers.get('status', None) == 'FAILURE':
    return headers
  
  return handle_response(requests.delete(f'{API_STUB}/v1/api/users/{brivo_user_id}', headers=headers), no_content=True)

def brivo_update_user(env, partner_rec):
  '''
    Update a brivo user
    Input:
      - env. An object environment, passed into `_set_api_headers` to generate the API call headers.
      - partner_rec. A res.partner record.
      
    Output:
      A response from Brivo's API.
  '''
  first_name = partner_rec.name.split(' ')[0]
  last_name = partner_rec.name.split(' ')[1]
  emails = [{ 'address': partner_rec.email, 'type': 'personal' }] if partner_rec.email else []
  
  body = {
    'firstName': first_name,
    'lastName': last_name,
    'emails': emails
  }
  
  headers = _set_api_headers(env)
  
  if headers.get('status', None) == 'FAILURE':
    return headers

  return handle_response(requests.put(f'{API_STUB}/v1/api/users/{partner_rec.brivo_id}', json=body, headers=headers))

def brivo_create_barcode_credential(env, barcode):
  '''
    Creates a barcode credential in Brivo.
    Input:
      - env. An object environment, passed into `_set_api_headers` to generate the API call headers.
      - barcode. A barcode number.
    Output:
      - A response from Brivo.
  '''
  # According to a call to https://apidocs.brivo.com/#api-Credential-ListCredentialFormats,
  # the unknown format is 110. We will use the unknown format for barcode credentials.
  unknown_format_id = 110
  body = {
    'credentialFormat' : { 'id': unknown_format_id },
    'referenceId': barcode,
    'encodedCredential': barcode
  }
  
  headers = _set_api_headers(env)
  
  if headers.get('status', None) == 'FAILURE':
    return headers
  
  return handle_response(requests.post(f'{API_STUB}/v1/api/credentials', json=body, headers=headers))

def brivo_delete_barcode_credential(env, brivo_cred_id):
  '''
    Deletes a credential in Brivo.
  '''
  headers = _set_api_headers(env)
  
  if headers.get('status', None) == 'FAILURE':
    return headers
  
  return handle_response(requests.delete(f'{API_STUB}/v1/api/credentials/{brivo_cred_id}', headers=headers), no_content=True)

def brivo_assign_credential(env, brivo_user_id, brivo_credential_id):
  '''
    Assigns a credential in Brivo to a user.
  '''
  headers = _set_api_headers(env)
  
  if headers.get('status', None) == 'FAILURE':
    return headers
  
  return handle_response(requests.put(f'{API_STUB}/v1/api/users/{brivo_user_id}/credentials/{brivo_credential_id}', headers=headers), no_content=True)

def brivo_create_group(env, group_name):
  '''
    Creates a group in Brivo
    Input:
      - env. An Odoo environment, used to create headers.
      - group_name. The name for the group.
      
    Return:
      A response from Brivo of the form:
      
      {
        "id"                   : 8219006,
        "name"                 : "staff",
        "keypadUnlock"         : false,
        "immuneToAntipassback" : false,
        "excludedFromLockdown" : false
      }
  '''
  headers = _set_api_headers(env)
  
  if headers.get('status', None) == 'FAILURE':
    return headers
  
  payload = {
    'name' : group_name
  }
  
  return handle_response(requests.post(f'{API_STUB}/v1/api/groups', headers=headers, json=payload))

def brivo_list_groups(env):
  '''
    List groups in Brivo
  '''
  headers = _set_api_headers(env)
  
  if headers.get('status', None) == 'FAILURE':
    return headers
  
  return handle_response(requests.get(f'{API_STUB}/v1/api/groups', headers=headers))

def brivo_remove_from_group(env, brivo_group_id, brivo_user_id):
  '''
    Remove a partner from a group in Brivo.
  '''
  headers = _set_api_headers(env)
  
  if headers.get('status', None) == 'FAILURE':
    return headers
  
  return handle_response(requests.delete(f'{API_STUB}/v1/api/groups/{brivo_group_id}/users/{brivo_user_id}', headers=headers), no_content=True)

def brivo_add_to_group(env, brivo_group_id, brivo_user_id):
  '''
    Remove a partner from a group in Brivo.
  '''
  headers = _set_api_headers(env)
  
  if headers.get('status', None) == 'FAILURE':
    return headers
  
  return handle_response(requests.put(f'{API_STUB}/v1/api/groups/{brivo_group_id}/users/{brivo_user_id}', headers=headers), no_content=True)

def brivo_query_suspended_status(env, brivo_user_id):
  '''
    Retrieves the suspended status of a Brivo user.
  '''
  headers = _set_api_headers(env)
  
  if headers.get('status', None) == 'FAILURE':
    return headers
  
  return handle_response(requests.get(f'{API_STUB}/v1/api/users/{brivo_user_id}/suspended', headers=headers))

def brivo_toggle_suspended_status(env, brivo_user_id, suspend):
  '''
    Toggles the suspended status of a Brivo user.
  '''
  headers = _set_api_headers(env)
  
  if headers.get('status', None) == 'FAILURE':
    return headers
  
  payload = {
    "suspended": suspend
  }
  
  return handle_response(requests.put(f'{API_STUB}/v1/api/users/{brivo_user_id}/suspended', headers=headers, json=payload))

def handle_response(res : requests.Response, no_content=False):
  '''
    Helper function for handling responses from Brivo.
    If a call fails, returns an object containing the error for the call.
    
    Input:
      res: The raw response object for an API call.
      no_content: If true, the function will not attempt to parse the response body.
  '''
  _logger.info(f'Brivo API Call to {res.request.method} {res.url} with data {res.request.body}')
  
  try:
    if not res.ok:
      res.raise_for_status()
  except Exception as err:
    _logger.error(str(err))
    _logger.error(res.json())
    return { 'status': 'FAILURE', 'error': str(err) }

  try:
    if not no_content:
      res_data = res.json()
      _logger.info('Response from Brivo: %s', res_data)
      return res_data
    else:
      return { 'status': 'SUCCESS' }
  except Exception as err:
    _logger.error(str(err))
    return { 'status': 'FAILURE', 'error': str(err) }