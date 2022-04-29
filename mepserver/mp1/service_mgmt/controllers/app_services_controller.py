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

import cherrypy

sys.path.append("../../")
from mp1.models import *
import uuid
from .callbacks_controller import CallbackController

class ApplicationServicesController:

    @url_query_validator(cls=ServicesQueryValidator)
    @json_out(cls=NestedEncoder)
    def applications_services_get(self, appInstanceId: str, ser_instance_id: List[str] = None,
                                  ser_name: List[str] = None, ser_category_id: List[str] = None,
                                  consumed_local_only: bool = False, is_local: bool = False,
                                  scope_of_locality: str = None):
        """
        This method retrieves information about a list of mecService resources. This method is typically used in "service availability query" procedure

        Required params
        :param appInstanceId: Represents a MEC application instance. Note that the appInstanceId is allocated by the MEC platform manager.
        :type appInstanceId: String

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

        :return: ProblemDetails or ServiceInfo
        HTTP STATUS CODE: 200, 400, 403, 404, 414
        """
        # TODO VALIDATE PARAMETERS (i.e mutually exclusive) AND CREATE QUERY
        data = json.loads(
            '{"livenessInterval":5,"serName":"ola","serCategory":{"href":"http://www.google.com","id":"string","name":"string","version":"string"},"version":"string","state":"ACTIVE","transportInfo":{"id":"string","endpoint":{"uris":["http://www.google.com"]},"name":"string","description":"string","type":"REST_HTTP","protocol":"string","version":"string","security":{"oAuth2Info":{"grantTypes":["OAUTH2_AUTHORIZATION_CODE","OAUTH2_RESOURCE_OWNER"],"tokenEndpoint":"string"}},"implSpecificInfo":{}},"serializer":"JSON","scopeOfLocality":"MEC_SYSTEM","consumedLocalOnly":true,"isLocal":true}'
        )
        serviceInfo = ServiceInfo.from_json(data)
        return serviceInfo

    @cherrypy.tools.json_in()
    @json_out(cls=NestedEncoder)
    def applications_services_post(self, appInstanceId: str):
        """
        This method is used to create a mecService resource. This method is typically used in "service availability update and new service registration" procedure

        :param appInstanceId: Represents a MEC application instance. Note that the appInstanceId is allocated by the MEC platform manager.
        :type appInstanceId: String

        :return: ServiceInfo or ProblemDetails
        HTTP STATUS CODE: 201, 400, 403, 404
        """
        # TODO ADD RATE LIMITING OTHERWISE APP CAN CONTINOUSLY GENERATE NEW SERVICES
        # TODO NEEDS TO BE RATE LIMIT SINCE AN APP CAN HAVE N SERVICES
        data = cherrypy.request.json
        # The process of generating the class allows for "automatic" validation of the json
        serviceInfo = ServiceInfo.from_json(data)
        # Add serInstanceId (uuid) to serviceInfo according to Section 8.1.2.2
        # serInstaceId is used as serviceId appServices
        serviceInfo.serInstanceId = str(uuid.uuid4())
        # Add _links data to serviceInfo
        server_self_referencing_uri = cherrypy.url(qs=cherrypy.request.query_string, relative='server')
        _links = Links(liveness=LinkType(f"{server_self_referencing_uri}/{serviceInfo.serInstanceId}/liveness"))
        serviceInfo._links = _links
        # TODO serCategory IF NOT PRESENT NEEDS TO BE SET BY MEP (SOMEHOW TELL ME ETSI)
        # Check if the appInstanceId has already confirmed ready status
        if cherrypy.thread_data.db.count_documents("appStatus", dict(appInstanceId=appInstanceId)) > 0:
            # Store new service into the database
            cherrypy.thread_data.db.create("services",object_to_mongodb_dict(serviceInfo))
            # Obtain all the Subscriptions that match the newly added service
            # Generate query that allows for all possible criteria using the $and and $or mongo operators
            query = serviceInfo.to_filtering_criteria_json()
            cherrypy.log(json.dumps(query,cls=NestedEncoder))
            subscriptions = cherrypy.thread_data.db.query_col("subscriptions",query)
            subscriptions = list(subscriptions)
            # Before creating the object transform the serviceInfo into a json list since it is
            # expecting a list of services in json
            # We don't use the original data because it is missing parameters that are introduced internally
            serviceInfoData = [json.loads(json.dumps(serviceInfo,cls=NestedEncoder))]
            serviceNotification = ServiceAvailabilityNotification.from_json_service_list(data=serviceInfoData,
                                                                                    changeType="ADDED")
            # If some subscriptions matches with the newly added service we need to notify them of this change
            if len(subscriptions)>0:
                availability_notifications = []
                # Transform each subscription into a ServiceNotificationSubscription class for easier usage
                for subscription in list(subscriptions):
                    appInstanceId = subscription.pop("appInstanceId")
                    subscriptionId = subscription.pop("subscriptionId")
                    availability_notification = SerAvailabilityNotificationSubscription.from_json(subscription)
                    availability_notification.appInstanceId = appInstanceId
                    availability_notification.subscriptionId = subscriptionId
                    availability_notifications.append(availability_notification)
                # Call the callback with the list of SerAvailabilityNotificationSubscriptions
                # Use a sleep_time of 0 (the subscriber is already up and waiting for subscriptions)
                CallbackController.execute_callback(availability_notifications=availability_notifications,
                                                    data=serviceNotification,sleep_time=0)

            # According to Table 8.2.6.3.4-2
            # TODO ASK ETSI WHATS THE DIFFERENCE BETWEEN _LINK AND THIS LOCATION HEADER BECAUSE BOTH SEEM TO POINT TO SAME THING
            cherrypy.response.headers["Location"] = _links.liveness.href

            ## KAFKA
            import socket
            from kafka import KafkaProducer
            kafka_ip = socket.gethostbyname("kafka")
            kafka_port = 9092
            producer = KafkaProducer(bootstrap_servers=f"{kafka_ip}:{kafka_port}")
            producer.send('mep', f'MEC APP with appInstanceID {appInstanceId} has created a service'.encode())
            producer.flush()


            return serviceInfo
        else:
            # TODO PROBLEM DETAILS OUTPUT
            pass

    @json_out(cls=NestedEncoder)
    def applicaton_services_get_with_service_id(
        self, appInstanceId: str, serviceId: str
    ):
        """
        This method retrieves information about a mecService resource. This method is typically used in "service availability query" procedure

        :param appInstanceId: Represents a MEC application instance. Note that the appInstanceId is allocated by the MEC platform manager.
        :type appInstanceId: String
        :param serviceId: Represents a MEC service instance.
        :type serviceId: String

        :return: ServiceInfo or ProblemDetails
        HTTP STATUS CODE: 200, 400, 403, 404
        """
        # TODO VALIDATE PARAMETERS (i.e mutually exclusive) AND CREATE QUERY
        data = json.loads(
            '{"serInstanceId":"string","livenessInterval":5,"_links":{"self":{"href":"http://www.google.com"},"liveness":{"href":"http://www.google.com"}},"version":"string","state":"ACTIVE","transportInfo":{"id":"string","endpoint":{"uris":["http://www.google.com"]},"name":"string","description":"string","type":"REST_HTTP","protocol":"string","version":"string","security":{"oAuth2Info":{"grantTypes":["OAUTH2_AUTHORIZATION_CODE","OAUTH2_RESOURCE_OWNER"],"tokenEndpoint":"string"}},"implSpecificInfo":{}},"serializer":"JSON","scopeOfLocality":"MEC_SYSTEM","consumedLocalOnly":true,"isLocal":true}'
        )
        serviceInfo = ServiceInfo.from_json(data)
        return serviceInfo

    @cherrypy.tools.json_in()
    @json_out(cls=NestedEncoder)
    def application_services_put(self, appInstanceId: str, serviceId: str):
        """
                This method updates the information about a mecService resource

                :param appInstanceId: Represents a MEC application instance. Note that the appInstanceId is allocated by the MEC platform manager.
                :type appInstanceId: String
                :param serviceId: Represents a MEC service instance.
                :type serviceId: String
        2
                :request body: New ServiceInfo with updated "state" is included as entity body of the request


                :return: ServiceInfo or ProblemDetails
                HTTP STATUS CODE: 200, 400, 403, 404, 412
        """
        # TODO PUT ONLY NEEDS TO RECEIVE ONE UPDATABLE CRITERIA
        data = cherrypy.request.json
        serviceInfo = ServiceInfo.from_json(data)
        return serviceInfo

    @json_out(cls=NestedEncoder)
    def application_services_delete(self, appInstanceId: str, serviceId: str):
        """
        This method deletes a mecService resource. This method is typically used in the service deregistration procedure.

        :param appInstanceId: Represents a MEC application instance. Note that the appInstanceId is allocated by the MEC platform manager.
        :type appInstanceId: String
        :param serviceId: Represents a MEC service instance.
        :type serviceId: String


        :return: No Content or ProblemDetails
        HTTP STATUS CODE: 204, 403, 404,
        """
        cherrypy.response.status = 204
        return
