# Copyright 2014 - Rackspace Hosting
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

import mock
import os.path
import uuid

from solum.openstack.common.gettextutils import _
from solum.tests import base
from solum.tests import fakes
from solum.tests import utils
from solum.worker.handlers import shell as shell_handler


class HandlerTest(base.BaseTestCase):
    def setUp(self):
        super(HandlerTest, self).setUp()
        self.ctx = utils.dummy_context()

    @mock.patch('solum.worker.handlers.shell.LOG')
    def test_echo(self, fake_LOG):
        shell_handler.Handler().echo({}, 'foo')
        fake_LOG.debug.assert_called_once_with(_('%s') % 'foo')

    @mock.patch('solum.worker.handlers.shell.Handler._get_environment')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.conductor.api.API.build_job_update')
    @mock.patch('subprocess.Popen')
    def test_build(self, mock_popen, mock_updater, mock_registry,
                   mock_get_env):
        handler = shell_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        fake_glance_id = str(uuid.uuid4())
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        handler._update_assembly_status = mock.MagicMock()
        mock_popen.return_value.communicate.return_value = [
            'foo\ncreated_image_id=%s' % fake_glance_id, None]
        test_env = {'PATH': '/bin'}
        mock_get_env.return_value = test_env
        handler.build(self.ctx, 5, 'git://example.com/foo', 'new_app',
                      '1-2-3-4', 'heroku',
                      'docker', 44)

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        script = os.path.join(proj_dir, 'contrib/lp-cedarish/docker/build-app')
        mock_popen.assert_called_once_with([script, 'git://example.com/foo',
                                            'new_app', self.ctx.tenant,
                                           '1-2-3-4'], env=test_env, stdout=-1)
        expected = [mock.call(5, 'BUILDING', 'Starting the image build',
                              None, 44),
                    mock.call(5, 'COMPLETE', 'built successfully',
                              fake_glance_id, 44)]

        self.assertEqual(expected, mock_updater.call_args_list)

    @mock.patch('solum.worker.handlers.shell.Handler._get_environment')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.conductor.api.API.build_job_update')
    @mock.patch('subprocess.Popen')
    def test_build_fail(self, mock_popen, mock_updater, mock_registry,
                        mock_get_env):
        handler = shell_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        handler._update_assembly_status = mock.MagicMock()
        mock_popen.return_value.communicate.return_value = [
            'foo\ncreated_image_id= \n', None]
        test_env = {'PATH': '/bin'}
        mock_get_env.return_value = test_env
        handler.build(self.ctx, 5, 'git://example.com/foo', 'new_app',
                      '1-2-3-4', 'heroku',
                      'docker', 44)

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        script = os.path.join(proj_dir, 'contrib/lp-cedarish/docker/build-app')
        mock_popen.assert_called_once_with([script, 'git://example.com/foo',
                                            'new_app', self.ctx.tenant,
                                           '1-2-3-4'], env=test_env, stdout=-1)
        expected = [mock.call(5, 'BUILDING', 'Starting the image build',
                              None, 44),
                    mock.call(5, 'ERROR', 'image not created', None, 44)]

        self.assertEqual(expected, mock_updater.call_args_list)


class TestBuildCommand(base.BaseTestCase):
    scenarios = [
        ('docker',
         dict(source_format='heroku', image_format='docker',
              base_image_id='auto',
              expect='lp-cedarish/docker/build-app')),
        ('vmslug',
         dict(source_format='heroku', image_format='qcow2',
              base_image_id='auto',
              expect='lp-cedarish/vm-slug/build-app')),
        ('dib',
         dict(source_format='dib', image_format='qcow2',
              base_image_id='xyz',
              expect='diskimage-builder/vm-slug/build-app'))]

    def test_build_cmd(self):
        ctx = utils.dummy_context()
        handler = shell_handler.Handler()
        cmd = handler._get_build_command(ctx,
                                         'http://example.com/a.git',
                                         'testa',
                                         self.base_image_id,
                                         self.source_format,
                                         self.image_format)
        self.assertIn(self.expect, cmd[0])
        self.assertEqual('http://example.com/a.git', cmd[1])
        self.assertEqual('testa', cmd[2])
        self.assertEqual(ctx.tenant, cmd[3])
        if self.base_image_id == 'auto' and self.image_format == 'qcow2':
            self.assertEqual('cedarish', cmd[4])
        else:
            self.assertEqual(self.base_image_id, cmd[4])
