from datetime import date, datetime
from io import BytesIO
from gzip import GzipFile
import logging
import json
import re
from dateutil.tz import tzutc
from requests.auth import AuthBase, HTTPBasicAuth
from requests import sessions

from customerio.analytics.version import VERSION
from customerio.analytics.utils import remove_trailing_slash

_session = sessions.Session()

_API_KEY_PREFIX = re.compile(r'^(pk|sk)_(us|eu)_')
_REGION_HOSTS = {
    'us': 'https://cdp.customer.io',
    'eu': 'https://cdp-eu.customer.io',
}


class _BearerAuth(AuthBase):
    """Sends the key as a Bearer token. Passed as `auth` so Requests never
    swaps in Basic auth from a matching .netrc entry."""

    def __init__(self, key):
        self.key = key

    def __call__(self, request):
        request.headers['Authorization'] = 'Bearer ' + self.key
        return request


def _base_url(api_key, host):
    region = api_key.group(2) if api_key else 'us'
    return remove_trailing_slash(host or _REGION_HOSTS[region])


def warn_if_other_region_host(write_key, host):
    """Logs a warning when a region API key is set to go to the other
    region's default host. Called once per client, not per request."""
    api_key = _API_KEY_PREFIX.match(write_key.strip())
    if not api_key:
        return
    region = api_key.group(2)
    base_url = _base_url(api_key, host)
    for other_region, other_host in _REGION_HOSTS.items():
        if other_region != region and base_url == other_host:
            logging.getLogger('customerio').warning(
                '%s API key is being sent to the %s host %s',
                region.upper(), other_region.upper(), base_url)


def post(write_key, host=None, gzip=False, timeout=15, proxies=None, **kwargs):
    """Post the `kwargs` to the API"""
    log = logging.getLogger('customerio')
    body = kwargs
    body["sentAt"] = datetime.utcnow().replace(tzinfo=tzutc()).isoformat()
    # Keys read from mounted secret files often end in a newline, which
    # http.client rejects with an error that includes the whole key.
    write_key = write_key.strip()
    api_key = _API_KEY_PREFIX.match(write_key)
    url = _base_url(api_key, host) + '/v1/batch'
    auth = _BearerAuth(write_key) if api_key else HTTPBasicAuth(write_key, '')
    data = json.dumps(body, cls=DatetimeSerializer)
    log.debug('making request: %s', data)
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'analytics-python/' + VERSION
    }
    if gzip:
        headers['Content-Encoding'] = 'gzip'
        buf = BytesIO()
        with GzipFile(fileobj=buf, mode='w') as gz:
            # 'data' was produced by json.dumps(),
            # whose default encoding is utf-8.
            gz.write(data.encode('utf-8'))
        data = buf.getvalue()

    kwargs = {
        "data": data,
        "auth": auth,
        "headers": headers,
        "timeout": timeout,
    }

    if proxies is not None:
        kwargs['proxies'] = proxies

    res = _session.post(url, **kwargs)

    if res.status_code == 200:
        log.debug('data uploaded successfully')
        return res

    try:
        payload = res.json()
        log.debug('received response: %s', payload)
        raise APIError(res.status_code, payload['code'], payload['message'])
    except ValueError as exc:
        raise APIError(res.status_code, 'unknown', res.text) from exc


class APIError(Exception):

    def __init__(self, status, code, message):
        self.message = message
        self.status = status
        self.code = code

    def __str__(self):
        msg = "[customer.io] {0}: {1} ({2})"
        return msg.format(self.code, self.message, self.status)


class DatetimeSerializer(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)
