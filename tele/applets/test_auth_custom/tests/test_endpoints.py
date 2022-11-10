from http import HTTPStatus

import tele.tools
from tele.tests import HttpCase, HOST


class TestCustomAuth(HttpCase):
    # suppress "WARNING: Access Error" when auth fails on json endpoints
    @tele.tools.mute_logger('tele.http')
    def test_json(self):
        # straight request should fail
        r = self.url_open('/test_auth_custom/json', headers={'Content-Type': 'application/json'}, data="{}")
        e = r.json()['error']
        self.assertEqual(e['data']['name'], 'tele.exceptions.AccessDenied')

        # but preflight should work
        self.env['base'].flush()
        url = "http://%s:%s/test_auth_custom/json" % (HOST, tele.tools.config['http_port'])
        r = self.opener.options(url, headers={
            'Origin': 'localhost',
            'Access-Control-Request-Method': 'QUX',
            'Access-Control-Request-Headers': 'XYZ',
        })
        self.assertTrue(r.ok)
        self.assertEqual(r.headers['Access-Control-Allow-Origin'], '*')
        self.assertEqual(r.headers['Access-Control-Allow-Methods'], 'POST', "json is always POST")
        self.assertNotIn('XYZ', r.headers['Access-Control-Allow-Headers'], "headers are ignored")

    def test_http(self):
        # straight request should fail
        r = self.url_open('/test_auth_custom/http')
        self.assertEqual(r.status_code, HTTPStatus.FORBIDDEN)

        # but preflight should work
        self.env['base'].flush()
        url = "http://%s:%s/test_auth_custom/http" % (HOST, tele.tools.config['http_port'])
        r = self.opener.options(url, headers={
            'Origin': 'localhost',
            'Access-Control-Request-Method': 'QUX',
            'Access-Control-Request-Headers': 'XYZ',
        })
        self.assertTrue(r.ok, r.text)
        self.assertEqual(r.headers['Access-Control-Allow-Origin'], '*')
        self.assertEqual(r.headers['Access-Control-Allow-Methods'], 'GET, OPTIONS',
                         "http is whatever's on the endpoint")
        self.assertNotIn('XYZ', r.headers['Access-Control-Allow-Headers'], "headers are ignored")
