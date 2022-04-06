# Copyright 2022 Instituto de Telecomunicações - Aveiro
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

import sys
sys.path.append("../../")
from mp1.models import *


class ServicesController:
    @url_query_validator(cls=ServicesQueryValidator)
    @json_out(cls=NestedEncoder)
    def services_get(self,ser_instance_id: List[str] = None,
                                  ser_name: List[str] = None, ser_category_id: List[str] = None,
                                  consumed_local_only: bool = False, is_local: bool = False,
                                  scope_of_locality: str = None):
        """
        This method retrieves information about a list of mecService resources. This method is typically used in "service availability query" procedure

        Query Params
        :param ser_instance_id: A MEC application instance may use multiple ser_instance_ids as an input parameter to query the availability of a list of MEC service instances. Either "ser_instance_id" or "ser_name" or "ser_category_id" or none of them shall be present.
        :type ser_instance_id: List[String]
        :param ser_name: A MEC application instance may use multiple ser_names as an input parameter to query the availability of a list of MEC service instances. Either "ser_instance_id" or "ser_name" or "ser_category_id" or none of them shall be present.
        :type ser_name: List[String]
        :param ser_category_id: A MEC application instance may use ser_category_id as an input parameter to query the availability of a list of MEC service instances in a serCategory. Either "ser_instance_id" or "ser_name" or "ser_category_id" or none of them shall be present.
        :type ser_category_id: String
        :param consumed_local_only: Indicate whether the service can only be consumed by the MEC applications located in the same locality (as defined by scopeOfLocality) as this service instance.
        :type consumed_local_only: boolean
        :param is_local: Indicate whether the service is located in the same locality (as defined by scopeOfLocality) as the consuming MEC application.
        :type is_local: boolean
        :param scope_of_locality: A MEC application instance may use scope_of_locality as an input parameter to query the availability of a list of MEC service instances with a certain scope of locality.
        :type scope_of_locality: String

        :note: ser_name, ser_category_id, ser_instance_id are mutually-exclusive only one should be used

        :return: ServiceInfo or ProblemDetails
        HTTP STATUS CODE: 200, 400, 403, 404, 414
        """
        cherrypy.log("ola")
        query = dict(serInstanceId=ser_instance_id,
                     serName=ser_name,
                     serCategory=dict(id=ser_category_id),
                     consumedLocalOnly=consumed_local_only,
                     isLocal=is_local,
                     scopeOfLocality=scope_of_locality,
                     )
        data = cherrypy.thread_data.db.query_col("services",query)
        # Data is a pymongo cursor we first need to convert it into a json serializable object
        # Since this query is supposed to return various valid Services we can simply convert into a list
        return list(data)

    @json_out(cls=NestedEncoder)
    def services_get_with_serviceId(self, serviceId: str):
        """
        This method retrieves information about a mecService resource. This method is typically used in "service availability query" procedure

        :param serviceId: Represents a MEC service instance.
        :type serviceId: String

        :return: ServiceInfo or ProblemDetails
        """
        # TODO VALIDATE PARAMETERS (i.e mutually exclusive) AND CREATE QUERY
        data = json.loads(
            '{"serName":"working","livenessInterval":5,"_links":{"self":{"href":"http://www.google.com"},"liveness":{"href":"http://www.google.com"}},"version":"string","state":"ACTIVE","transportInfo":{"id":"string","endpoint":{"uris":["http://www.google.com"]},"name":"string","description":"string","type":"REST_HTTP","protocol":"string","version":"string","security":{"oAuth2Info":{"grantTypes":["OAUTH2_AUTHORIZATION_CODE"],"tokenEndpoint":"string"}},"implSpecificInfo":{}},"serializer":"JSON","scopeOfLocality":"MEC_SYSTEM","consumedLocalOnly":true,"isLocal":true}'
        )
        serviceInfo = ServiceInfo.from_json(data)
        return serviceInfo
