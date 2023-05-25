import requests
import platform
import json
import sys
import os

def to_error_message(errs):
  """
  Formats an array of error dicts into an error message string. Returns an error message.
  """

  return ', '.join(map(lambda e: f"{e['title']}: {e['detail']}", errs))

def create_release(version, channel, name=None, tag=None):
  """
  Creates a new release for the configured product. Returns a release object.
  """

  res = requests.post(
    f"https://api.keygen.sh/v1/accounts/{os.environ['KEYGEN_ACCOUNT_ID']}/releases",
    headers={
      'Authorization': f"Bearer {os.environ['KEYGEN_PRODUCT_TOKEN']}",
      'Content-Type': 'application/vnd.api+json',
      'Accept': 'application/vnd.api+json',
      'Keygen-Version': '1.3'
    },
    data=json.dumps({
      'data': {
        'type': 'releases',
        'attributes': {
          'version': version,
          'channel': channel,
          'name': name,
          'tag': tag
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

def publish_release(release):
  """
  Publishes a release. Returns a release object.
  """

  res = requests.post(
    f"https://api.keygen.sh/v1/accounts/{os.environ['KEYGEN_ACCOUNT_ID']}/releases/{release['id']}/actions/publish",
    headers={
      'Authorization': f"Bearer {os.environ['KEYGEN_PRODUCT_TOKEN']}",
      'Accept': 'application/vnd.api+json',
      'Keygen-Version': '1.3'
    }
  )

  release = res.json()

  if 'errors' in release:
    errs = release['errors']

    print(f'[error] Publish failed: errors={to_error_message(errs)}',
          file=sys.stderr)

    sys.exit(1)
  else:
    print(f"[info] Published: release={release['data']['id']} link={release['data']['links']['self']}",
          file=sys.stdout)

  return release['data']

def upload_artifact_for_release(release, filename, filetype, filesize, platform, arch, data=None):
  """
  Uploads an artifact for the given release. Returns an artifact object.
  """

  res = requests.post(
    f"https://api.keygen.sh/v1/accounts/{os.environ['KEYGEN_ACCOUNT_ID']}/artifacts",
    allow_redirects=False,
    headers={
      'Authorization': f"Bearer {os.environ['KEYGEN_PRODUCT_TOKEN']}",
      'Content-Type': 'application/vnd.api+json',
      'Accept': 'application/vnd.api+json',
      'Keygen-Version': '1.3'
    },
    data=json.dumps({
      'data': {
        'type': 'artifacts',
        'attributes': {
          'filename': filename,
          'filesize': filesize,
          'filetype': filetype,
          'platform': platform,
          'arch': arch
        },
        'relationships': {
          'release': {
            'data': { 'type': 'release', 'id': release['id'] }
          }
        }
      }
    })
  )

  artifact = res.json()

  if 'errors' in artifact:
    errs = artifact['errors']

    print(f'[error] Upload failed: errors={to_error_message(errs)}',
          file=sys.stderr)

    sys.exit(1)
  else:
    print(f"[info] Uploaded: artifact={artifact['data']['id']} link={artifact['data']['links']['self']}",
          file=sys.stdout)

  # Follow redirect and upload file to storage provider
  upload_url = res.headers['location']

  if data:
    requests.put(upload_url,
      headers={ 'Content-Type': 'text/plain' },
      data=data
    )

  return artifact['data']

release = create_release(
  name='Python Release v1',
  version='1.0.0',
  channel='stable'
)

with open('examples/hello-world.txt', mode='r') as f:
  stat = os.stat(f.name)

  artifact = upload_artifact_for_release(
    filename=f.name,
    filesize=stat.st_size,
    filetype='txt',
    platform=f"{platform.system()} {platform.release()}",
    arch=platform.processor(),
    release=release,
    data=f
  )

with open('examples/hello-mars.txt', mode='r') as f:
  stat = os.stat(f.name)

  artifact = upload_artifact_for_release(
    filename=f.name,
    filesize=stat.st_size,
    filetype='txt',
    platform=f"{platform.system()} {platform.release()}",
    arch=platform.processor(),
    release=release,
    data=f
  )

publish_release(release)