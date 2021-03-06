# Copyright 2014 - Rackspace
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
import mock

import wsme

from solum.api.controllers.v1.datamodel import language_pack as lp_model
from solum.api.controllers.v1 import language_pack
from solum.common import exception
from solum import objects
from solum.tests import base
from solum.tests import fakes


image_sample = {"status": "active",
                "name": "nodeus",
                "tags": [
                    "solum::lp::type::fake_type",
                    "solum::lp::description::a fake description",
                    "solum::lp::compiler_version::1.3",
                    "solum::lp::compiler_version::1.4",
                    "solum::lp::compiler_version::1.5",
                    "solum::lp::runtime_version::1.4",
                    "solum::lp::runtime_version::1.5",
                    "solum::lp::runtime_version::1.6",
                    "solum::lp::implementation::Sun",
                    "solum::lp::build_tool::maven::3.0",
                    "solum::lp::build_tool::ant::2.1",
                    "solum::lp::os_platform::Ubuntu::12.04",
                    "solum::lp::attribute::attr1key::attr1value",
                    "solum::lp::attribute::attr2key::attr2value"
                ],
                "self": "/v2/images/bc68cd73",
                "id": "bc68cd73"}

lp_sample = {
    "name": "fake_name",
    "description": "A test to create language_pack",
    "project_id": "project_id",
    "user_id": "user_id",
    "language_implementation": "Sun",
    "language_pack_type": "Java",
    "compiler_versions": ["1.3", "1.4", "1.5"],
    "runtime_versions": ["1.5", "1.6", "1.7"],
    "os_platform": {
        "OS": "Ubuntu",
        "version": "12.04"
    },
    "build_tool_chain": [lp_model.BuildTool(type="maven", version="3.0"),
    lp_model.BuildTool(type="ant", version="2.1")],
    "attributes": {
        "attr1key": "attr1value",
        "attr2key": "attr2value"
    }
}


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.language_pack_handler.LanguagePackHandler')
class TestLanguagePackController(base.BaseTestCase):
    def test_language_pack_get(self, handler_mock, resp_mock, request_mock):
        handler_get = handler_mock.return_value.get
        handler_get.return_value = image_sample
        language_pack_obj = language_pack.LanguagePackController(
            'test_id')
        result = language_pack_obj.get()
        self.assertEqual(200, resp_mock.status)
        self.assertIsNotNone(result)
        handler_get.assert_called_once_with('test_id')

    def test_lp_get_not_found(self, handler_mock, resp_mock, request_mock):
        handler_get = handler_mock.return_value.get
        handler_get.side_effect = exception.ResourceNotFound(
            name='language_pack', id='test_id')
        language_pack_obj = language_pack.LanguagePackController(
            'test_id')
        language_pack_obj.get()
        self.assertEqual(404, resp_mock.status)
        handler_get.assert_called_once_with('test_id')

    def test_language_pack_put_none(self, LanguagePackHandler, resp_mock,
                                    request_mock):
        request_mock.body = None
        request_mock.content_type = 'application/json'
        hand_put = LanguagePackHandler.return_value.put
        hand_put.return_value = image_sample
        ret_val = language_pack.LanguagePackController('test_id').put()
        faultstring = str(ret_val['faultstring'])
        self.assertEqual("Missing argument: \"data\"", faultstring)
        self.assertEqual(400, resp_mock.status)

    def test_language_pack_put_not_found(self, LanguagePackHandler,
                                         resp_mock, request_mock):
        json_update = {'name': 'foo'}
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        hand_update = LanguagePackHandler.return_value.update
        hand_update.side_effect = exception.ResourceNotFound(
            name='language_pack', id='test_id')
        language_pack.LanguagePackController('test_id').put()
        json_update.update(dict(tags=['solum::lp']))
        hand_update.assert_called_with('test_id', json_update)
        self.assertEqual(404, resp_mock.status)

    def test_language_pack_put_ok(self, LanguagePackHandler, resp_mock,
                                  request_mock):
        json_update = {'name': 'foo'}
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        hand_update = LanguagePackHandler.return_value.update
        hand_update.return_value = image_sample
        language_pack.LanguagePackController('test_id').put()
        json_update.update(dict(tags=['solum::lp']))
        hand_update.assert_called_with('test_id', json_update)
        self.assertEqual(200, resp_mock.status)

    def test_language_pack_delete_not_found(self, LanguagePackHandler,
                                            resp_mock, request_mock):
        hand_delete = LanguagePackHandler.return_value.delete
        hand_delete.side_effect = exception.ResourceNotFound(
            name='language_pack', language_pack_id='test_id')
        obj = language_pack.LanguagePackController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)

    def test_language_pack_delete_ok(self, LanguagePackHandler,
                                     resp_mock, request_mock):
        hand_delete = LanguagePackHandler.return_value.delete
        hand_delete.return_value = None
        obj = language_pack.LanguagePackController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(204, resp_mock.status)


class TestLanguagePackImage(base.BaseTestCase):

    def test_from_image(self):
        lp = lp_model.LanguagePack.from_image(image_sample, 'fake_host_url')
        self.assertEqual(lp.name, 'nodeus')
        self.assertEqual(lp.description, 'a fake description')
        self.assertEqual(lp.language_pack_type, 'fake_type')
        self.assertEqual(lp.uuid, 'bc68cd73')
        self.assertEqual(lp.compiler_versions, ['1.3', '1.4', '1.5'])
        self.assertEqual(lp.runtime_versions, ['1.4', '1.5', '1.6'])
        self.assertEqual(lp.language_implementation, 'Sun')
        self.assertEqual(len(lp.build_tool_chain), 2)
        self.assertEqual(lp.build_tool_chain[0].type, 'maven')
        self.assertEqual(lp.build_tool_chain[0].version, '3.0')
        self.assertEqual(lp.os_platform, {'OS': 'Ubuntu', 'version': '12.04'})
        self.assertIn('attr1key', lp.attributes)
        self.assertIn('attr2key', lp.attributes)
        self.assertEqual(lp.attributes['attr1key'], 'attr1value')
        self.assertEqual(lp.attributes['attr2key'], 'attr2value')

    def test_as_image_dict(self):
        lp = lp_model.LanguagePack(**lp_sample)
        image_dict = lp.as_image_dict()
        self.assertEqual(image_dict['name'], lp.name)
        self.assertIn('solum::lp', image_dict['tags'])
        self.assertIn(lp_model.TYPE + lp.language_pack_type,
                      image_dict['tags'])
        self.assertIn(lp_model.DESCRIPTION + lp.description,
                      image_dict['tags'])
        self.assertIn(lp_model.COMPILER_VERSION + lp.compiler_versions[0],
                      image_dict['tags'])
        self.assertIn(lp_model.COMPILER_VERSION + lp.compiler_versions[1],
                      image_dict['tags'])
        self.assertIn(lp_model.COMPILER_VERSION + lp.compiler_versions[2],
                      image_dict['tags'])
        self.assertIn(lp_model.RUNTIME_VERSION + lp.runtime_versions[0],
                      image_dict['tags'])
        self.assertIn(lp_model.RUNTIME_VERSION + lp.runtime_versions[0],
                      image_dict['tags'])
        self.assertIn(lp_model.RUNTIME_VERSION + lp.runtime_versions[0],
                      image_dict['tags'])
        self.assertIn(lp_model.RUNTIME_VERSION + lp.runtime_versions[0],
                      image_dict['tags'])
        self.assertIn(lp_model.BUILD_TOOL + lp.build_tool_chain[0].type +
                      '::' + lp.build_tool_chain[0].version,
                      image_dict['tags'])
        self.assertIn(lp_model.BUILD_TOOL + lp.build_tool_chain[1].type +
                      '::' + lp.build_tool_chain[1].version,
                      image_dict['tags'])
        self.assertIn(lp_model.OS_PLATFORM + lp.os_platform['OS'] +
                      '::' + lp.os_platform['version'], image_dict['tags'])
        self.assertIn(lp_model.ATTRIBUTE + lp.attributes.items()[0][0] +
                      '::' + lp.attributes.items()[0][1], image_dict['tags'])
        self.assertIn(lp_model.ATTRIBUTE + lp.attributes.items()[1][0] +
                      '::' + lp.attributes.items()[1][1], image_dict['tags'])

    def test_as_image_dict_unset(self):
        lp = lp_model.LanguagePack()
        image_dict = lp.as_image_dict()
        self.assertEqual(image_dict, {'name': wsme.Unset,
                                      'tags': ['solum::lp']})


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.language_pack_handler.LanguagePackHandler')
class TestLanguagePacksController(base.BaseTestCase):
    def setUp(self):
        super(TestLanguagePacksController, self).setUp()
        objects.load()

    def test_language_packs_get_all(self, LanguagePackHandler,
                                    resp_mock, request_mock):
        hand_get = LanguagePackHandler.return_value.get_all
        hand_get.return_value = []
        resp = language_pack.LanguagePacksController().get_all()
        hand_get.assert_called_with()
        self.assertEqual(200, resp_mock.status)
        self.assertIsNotNone(resp)

    def test_language_packs_post(self, LanguagePackHandler, resp_mock,
                                 request_mock):
        json_create = {'name': 'foo'}
        request_mock.body = json.dumps(json_create)
        request_mock.content_type = 'application/json'
        hand_create = LanguagePackHandler.return_value.create
        hand_create.return_value = image_sample
        language_pack.LanguagePacksController().post()
        json_create.update(dict(tags=['solum::lp']))
        hand_create.assert_called_with(json_create)
        self.assertEqual(201, resp_mock.status)

    def test_language_packs_post_nodata(self, LanguagePackHandler, resp_mock,
                                        request_mock):
        request_mock.body = ''
        request_mock.content_type = 'application/json'
        hand_create = LanguagePackHandler.return_value.create
        hand_create.return_value = image_sample
        ret_val = language_pack.LanguagePacksController().post()
        faultstring = str(ret_val['faultstring'])
        self.assertEqual("Missing argument: \"data\"", faultstring)
        self.assertEqual(400, resp_mock.status)
