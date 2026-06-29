from datetime import datetime, date
import unittest
import unittest.mock as mock
import json
import requests

from customerio.analytics.request import post, DatetimeSerializer


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
