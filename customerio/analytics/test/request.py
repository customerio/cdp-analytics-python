from datetime import datetime, date
import unittest
import unittest.mock as mock
import json
import os
import tempfile
import requests

from customerio.analytics.request import post, DatetimeSerializer, _BearerAuth


class TestRequests(unittest.TestCase):

    def test_valid_request(self):
        res = post('testsecret', batch=[{
            'userId': 'userId',
            'event': 'python event',
            'type': 'track'
        }])
        self.assertEqual(res.status_code, 200)

    def test_invalid_request_error(self):
        self.assertRaises(Exception, post, 'testsecret',
                          'https://cdp.customer.io', False, '[{]')

    def test_invalid_host(self):
        self.assertRaises(Exception, post, 'testsecret',
                          'cdp.customer.io/', batch=[])

    def test_datetime_serialization(self):
        data = {'created': datetime(2012, 3, 4, 5, 6, 7, 891011)}
        result = json.dumps(data, cls=DatetimeSerializer)
        self.assertEqual(result, '{"created": "2012-03-04T05:06:07.891011"}')

    def test_date_serialization(self):
        today = date.today()
        data = {'created': today}
        result = json.dumps(data, cls=DatetimeSerializer)
        expected = '{"created": "%s"}' % today.isoformat()
        self.assertEqual(result, expected)

    def test_should_not_timeout(self):
        res = post('testsecret', batch=[{
            'userId': 'userId',
            'event': 'python event',
            'type': 'track'
        }], timeout=15)
        self.assertEqual(res.status_code, 200)

    def test_should_timeout(self):
        with self.assertRaises(requests.ReadTimeout):
            post('testsecret', batch=[{
                'userId': 'userId',
                'event': 'python event',
                'type': 'track'
            }], timeout=0.0001)

    def test_proxies_passed_to_session(self):
        proxies = {
            'https': 'http://proxy.example.com:8080',
            'http': 'http://proxy.example.com:8080',
        }
        mock_response = mock.Mock()
        mock_response.status_code = 200
        with mock.patch('customerio.analytics.request._session.post',
                        return_value=mock_response) as mock_post:
            post('testsecret', proxies=proxies, batch=[{
                'userId': 'userId',
                'event': 'python event',
                'type': 'track',
            }])
            mock_post.assert_called_once()
            _, call_kwargs = mock_post.call_args
            self.assertEqual(call_kwargs['proxies'], proxies)

    def test_no_proxies_by_default(self):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        with mock.patch('customerio.analytics.request._session.post',
                        return_value=mock_response) as mock_post:
            post('testsecret', batch=[{
                'userId': 'userId',
                'event': 'python event',
                'type': 'track',
            }])
            mock_post.assert_called_once()
            _, call_kwargs = mock_post.call_args
            self.assertNotIn('proxies', call_kwargs)

    def _post_and_get_call(self, write_key, **kwargs):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        with mock.patch('customerio.analytics.request._session.post',
                        return_value=mock_response) as mock_post:
            post(write_key, batch=[{
                'userId': 'userId',
                'event': 'python event',
                'type': 'track',
            }], **kwargs)
            mock_post.assert_called_once()
            return mock_post.call_args

    def test_secret_api_key_uses_bearer(self):
        key = 'sk_us_' + 'a' * 32 + '_abcdef'
        _, call_kwargs = self._post_and_get_call(key)
        self.assertIsInstance(call_kwargs['auth'], _BearerAuth)
        self.assertEqual(call_kwargs['auth'].key, key)

    def test_public_api_key_uses_bearer(self):
        key = 'pk_us_' + 'a' * 32 + '_abcdef'
        _, call_kwargs = self._post_and_get_call(key)
        self.assertIsInstance(call_kwargs['auth'], _BearerAuth)
        self.assertEqual(call_kwargs['auth'].key, key)

    def test_netrc_entry_does_not_override_bearer(self):
        key = 'sk_us_' + 'a' * 32 + '_abcdef'
        with tempfile.TemporaryDirectory() as tmp:
            netrc = os.path.join(tmp, 'netrc')
            with open(netrc, 'w') as f:
                f.write('machine cdp.customer.io login user password pass\n')
            mock_response = mock.Mock()
            mock_response.status_code = 200
            with mock.patch.dict(os.environ, {'NETRC': netrc}), \
                    mock.patch('requests.sessions.Session.send',
                               return_value=mock_response) as mock_send:
                post(key, batch=[{'userId': 'userId', 'type': 'track'}])
            prepared = mock_send.call_args[0][0]
        self.assertEqual(prepared.headers['Authorization'], 'Bearer ' + key)

    def test_legacy_write_key_uses_basic(self):
        call_args, call_kwargs = self._post_and_get_call('testsecret')
        self.assertEqual(call_args[0], 'https://cdp.customer.io/v1/batch')
        self.assertNotIn('Authorization', call_kwargs['headers'])
        self.assertEqual(call_kwargs['auth'].username, 'testsecret')
        self.assertEqual(call_kwargs['auth'].password, '')

    def test_eu_api_key_uses_eu_host(self):
        key = 'sk_eu_' + 'a' * 32 + '_abcdef'
        call_args, _ = self._post_and_get_call(key)
        self.assertEqual(call_args[0], 'https://cdp-eu.customer.io/v1/batch')

    def test_us_api_key_uses_us_host(self):
        key = 'sk_us_' + 'a' * 32 + '_abcdef'
        call_args, _ = self._post_and_get_call(key)
        self.assertEqual(call_args[0], 'https://cdp.customer.io/v1/batch')

    def test_explicit_host_wins_over_api_key(self):
        key = 'sk_eu_' + 'a' * 32 + '_abcdef'
        call_args, _ = self._post_and_get_call(
            key, host='https://example.com')
        self.assertEqual(call_args[0], 'https://example.com/v1/batch')

    def test_api_key_with_trailing_newline_is_stripped(self):
        key = 'sk_eu_' + 'a' * 32 + '_abcdef'
        mock_response = mock.Mock()
        mock_response.status_code = 200
        with mock.patch('requests.sessions.Session.send',
                        return_value=mock_response) as mock_send:
            post(key + '\n', batch=[{'userId': 'userId', 'type': 'track'}])
        prepared = mock_send.call_args[0][0]
        self.assertEqual(prepared.url, 'https://cdp-eu.customer.io/v1/batch')
        self.assertEqual(prepared.headers['Authorization'], 'Bearer ' + key)

    def test_unknown_prefix_uses_basic_and_us_host(self):
        key = 'xx_us_' + 'a' * 32 + '_abcdef'
        call_args, call_kwargs = self._post_and_get_call(key)
        self.assertEqual(call_args[0], 'https://cdp.customer.io/v1/batch')
        self.assertNotIsInstance(call_kwargs['auth'], _BearerAuth)
        self.assertEqual(call_kwargs['auth'].username, key)
        self.assertEqual(call_kwargs['auth'].password, '')
