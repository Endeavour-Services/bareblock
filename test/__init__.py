import hashlib
import json
import os
import pathlib
import tempfile
import unittest
from unittest import TestCase

import gnupg
import requests


def get_hash(data):
    if type(data) != bytes:
        # wierd hack
        # be warned
        data = data.encode('utf-8')
    gfg = hashlib.sha3_256()
    gfg.update(data)
    return gfg.hexdigest()


class IntgTestCase(TestCase):
    passphrase = 'test'
    server_url = "http://node:5000/"
    node_id = "node@dothttp.dev"
    gpg = None
    session = requests.session()

    @classmethod
    def setUpClass(cls):
        tempdir = tempfile.mkdtemp()
        client_name = os.path.basename(tempdir)
        path = pathlib.Path(tempdir)
        gpg = gnupg.GPG(gnupghome=path)
        IntgTestCase.gpg = gpg
        if not path.exists():
            path.mkdir()
        input_data = gpg.gen_key_input(
            name_email=f'{client_name}@dothttp.dev',
            passphrase='test')
        gpg.gen_key(input_data)
        fingerprint = gpg.list_keys()[0]['fingerprint']
        ascii_armored_public_keys = gpg.export_keys(fingerprint)
        regi_resp = IntgTestCase.session.post(f"{IntgTestCase.server_url}/register", json={
            "pgp": ascii_armored_public_keys
        })
        public_key = regi_resp.json()['public_key']
        server = gpg.import_keys(public_key)
        IntgTestCase.server_fingerprint = server.fingerprints[0]
        super(IntgTestCase, cls).setUpClass()

    @staticmethod
    def get_encrypted_message(message):
        signed_message = IntgTestCase.gpg.encrypt(
            message, passphrase=IntgTestCase.passphrase, always_trust=True, recipients=[IntgTestCase.node_id])
        return signed_message.data.decode('utf-8')

    @staticmethod
    def get_message(message):
        input_message = {
            "message": {
                "message": message
            }
        }
        message = json.dumps(input_message)
        return message

    def test_invalid_schema_message(self):

        resp = IntgTestCase.session.post(
            f"{IntgTestCase.server_url}/message", json={})
        self.assertEqual(500, resp.status_code)

    def test_message(self):
        message = IntgTestCase.get_encrypted_message(
            IntgTestCase.get_message('hi'))
        resp = IntgTestCase.session.post(
            f"{IntgTestCase.server_url}/message", json=dict(message=message))
        self.assertEqual(200, resp.status_code)

    def test_invalid_schema(self):
        message = IntgTestCase.get_encrypted_message(json.dumps({}))
        resp = IntgTestCase.session.post(
            f"{IntgTestCase.server_url}/message", json=dict(message=message))
        self.assertEqual(400, resp.status_code)

    def test_wrong_message(self):
        resp = IntgTestCase.session.post(
            f"{IntgTestCase.server_url}/message", json={})
        self.assertEqual(500, resp.status_code)


class Intgtest(IntgTestCase):
    def test(self):
        for i in range(12):
            self.test_message()
        # verify list
        list_resp = IntgTestCase.session.get(
            f"{IntgTestCase.server_url}/block/list")
        self.assertEqual(2, len(list_resp.json()))

        # verify count
        count_resp = IntgTestCase.session.get(
            f"{IntgTestCase.server_url}/block/count")
        self.assertEqual('2', count_resp.text)

        # verify latest
        resp = IntgTestCase.session.get(
            f"{IntgTestCase.server_url}/block/latest")
        self.assertEqual(list_resp.json()[-1], resp.text)

        # verify previous
        prev_resp = IntgTestCase.session.get(
            f"{IntgTestCase.server_url}/block/previous/{list_resp.json()[-1]}")
        self.assertEqual(200, prev_resp.status_code)

        # verify block
        resp = IntgTestCase.session.get(
            f"{IntgTestCase.server_url}/block/index/1")
        self.assertEqual(200, resp.status_code)

        body = resp.json()
        hash = body['hash']
        sign = body['sign']
        value = body['value']
        self.assertEqual(hash, get_hash(value))
        self.assertTrue(IntgTestCase.gpg.verify(sign))
