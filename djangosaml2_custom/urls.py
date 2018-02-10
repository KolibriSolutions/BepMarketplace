# Copyright (C) 2010-2012 Yaco Sistemas (http://www.yaco.es)
# Copyright (C) 2009 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls import url
from djangosaml2 import views

from djangosaml2_custom import views as custom_views

app_name = 'djangosaml2_custom'
urlpatterns = [
    url(r'^login/$', views.login, name='saml2_login'),
    url(r'^acs/$', custom_views.assertion_consumer_service, name='saml2_acs'),  # ACS is changed to a custom view function
    # url(r'^logout/$', views.logout, name='saml2_logout'), # SAML logout doesn't work, regular Django logout is used.
    url(r'^ls/$', views.logout_service, name='saml2_ls'),
    url(r'^ls/post/$', views.logout_service_post, name='saml2_ls_post'),
    url(r'^metadata/$', views.metadata, name='saml2_metadata'),
]
