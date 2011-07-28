# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from melange.tests.functional import get_api_port, FunctionalTest


class TestServiceConf(FunctionalTest):

    def test_root_url_returns_versions(self):
        response = self.client.get("/")

        self.assertEqual(response.status, 200)
        self.assertTrue("versions" in response.read())

    def test_extensions_are_loaded(self):
        response = self.client.get("/v0.1/extensions")
        self.assertEqual(response.status, 200)
        self.assertTrue("extensions" in response.read())

    def test_ipam_service_can_be_accessed(self):
        response = self.client.get("/v0.1/ipam/ip_blocks",
                                   headers={'X_ROLE': 'Admin'})

        self.assertEqual(response.status, 200)
        self.assertTrue("ip_blocks" in response.read())


class TestMimeTypeVersioning(FunctionalTest):

    def test_ipam_service_can_be_accessed_with_mime_type_versioning(self):
        headers = {'X_ROLE': 'Admin',
                   'Accept': "application/vnd.openstack.melange+xml;"
                   "version=0.1"}

        response = self.client.get("/ipam/ip_blocks", headers=headers)

        self.assertEqual(response.status, 200)
        self.assertTrue("ip_blocks" in response.read())

    def test_requesting_nonexistent_version_via_mime_type_versioning(self):
        headers = {'X_ROLE': 'Admin',
                   'Accept': "application/vnd.openstack.melange+xml;"
                   "version=99.1"}

        response = self.client.get("/ipam/ip_blocks", headers=headers)

        self.assertEqual(response.status, 406)
        self.assertTrue("version not supported" in response.read())


class TestAuthMiddleware(FunctionalTest):

    def test_forbids_tenants_accesing_other_tenants_resource(self):
        response = self.client.get("/v0.1/ipam/tenants/123/ip_blocks",
                                   headers={'X_TENANT': "111"})
        self.assertEqual(response.status, 403)

    def test_authorizes_tenants_accesing_their_resource(self):
        response = self.client.get("/v0.1/ipam/tenants/123/ip_blocks",
                                   headers={'X_TENANT': "123"})

        self.assertEqual(response.status, 200)

    def test_forbids_tenants_accesing_admin_resources(self):
        response = self.client.get("/v0.1/ipam/ip_blocks",
                                   headers={'X_TENANT': "123",
                                            'X_ROLE': "Tenant"})

        self.assertEqual(response.status, 403)
