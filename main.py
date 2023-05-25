import requests
import json
import sys
import os

def to_error_message(errs):
  """
  Formats an array of error dicts into an error message string. Returns an error message.
  """

  return ', '.join(map(lambda e: f"{e['title']}: {e['detail']}", errs))

def create_release(**kwargs):
  """
  Creates a new release for the configured product. Returns a release object.
  """

  res = requests.put(
    f"https://api.keygen.sh/v1/accounts/{os.environ['KEYGEN_ACCOUNT_ID']}/releases",
    headers={
      'Authorization': f"Bearer {os.environ['KEYGEN_PRODUCT_TOKEN']}",
      'Content-Type': 'application/vnd.api+json',
      'Accept': 'application/vnd.api+json',
      'Keygen-Version': '1.0'
    },
    data=json.dumps({
      'data': {
        'type': 'releases',
        'attributes': {
          **kwargs
        },
        'relationships': {
          'product': {
            'data': { 'type': 'product', 'id': os.environ['KEYGEN_PRODUCT_ID'] }
          }
        }
      }
    })
  )

  release = res.json()

  if 'errors' in release:
    errs = release['errors']

    print(f'[error] Release failed: errors={to_error_message(errs)}',
          file=sys.stderr)

    sys.exit(1)
  else:
    print(f"[info] Created: release={release['data']['id']} link={release['data']['links']['self']}",
          file=sys.stdout)

  return release['data']

def upload_artifact_for_release(**kwargs):
  """
  Uploads an artifact for the given release. Returns an artifact object.
  """

  res = requests.put(
    f"https://api.keygen.sh/v1/accounts/{os.environ['KEYGEN_ACCOUNT_ID']}/releases/{kwargs['release_id']}/artifact",
    allow_redirects=False,
    headers={
      'Authorization': f"Bearer {os.environ['KEYGEN_PRODUCT_TOKEN']}",
      'Accept': 'application/vnd.api+json',
      'Keygen-Version': '1.0'
    }
  )

  upload_url = res.headers['location']
  artifact   = res.json()

  if 'errors' in artifact:
    errs = artifact['errors']

    print(f'[error] Upload failed: errors={to_error_message(errs)}',
          file=sys.stderr)

    sys.exit(1)
  else:
    print(f"[info] Uploaded: artifact={artifact['data']['id']} link={artifact['data']['links']['self']}",
          file=sys.stdout)

  # Follow redirect and upload file to S3
  requests.put(upload_url,
    headers={ 'Content-Type': 'text/plain' },
    data=kwargs['file']
  )

  return artifact['data']

with open('examples/hello-world.txt', mode='r') as f:
  stat    = os.stat(f.name)
  release = create_release(
    filename=f.name,
    filesize=stat.st_size,
    version='1.0.0',
    filetype='txt',
    platform=sys.platform,
    channel='stable'
  )

  artifact = upload_artifact_for_release(
    release_id=release['id'],
    file=f
  )
