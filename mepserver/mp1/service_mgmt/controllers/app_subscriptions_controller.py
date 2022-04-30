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
import json
import sys
import time

import requests
import cherrypy
import uuid
sys.path.append("../../")
from mp1.models import *
from .callbacks_controller import CallbackController


class ApplicationSubscriptionsController:
    @json_out(cls=NestedEncoder)
    def applications_subscriptions_get(self, appInstanceId: str):
        """
        The GET method may be used to request information about all subscriptions for this requestor. Upon success, the response contains entity body with all the subscriptions for the requestor.

        :param appInstanceId: Represents a MEC application instance. Note that the appInstanceId is allocated by the MEC platform manager.
        :type appInstanceId: str

        :return: MecServiceMgmtApiSubscriptionLinkList or ProblemDetails
        HTTP STATUS CODE: 200, 400, 403, 404
        """
        # Obtain the subscriptionIds that match the appInstanceId
        # TODO validate the authorization to get the subscriptions of the appinstanceid (i.e if this person can query for this appinstanceid)
        subscriptionIds = cherrypy.thread_data.db.query_col("subscriptions",
                                                          query=dict(appInstanceId=appInstanceId),
                                                          fields=dict(subscriptionId=1))

        # Generate dict and then validate via the already existing models
        # Takes all subscriptions created by appInstanceId and generates a list of subscriptions
        subscriptionlinklist = {"_links":
                                    {"self":
                                         {"href":cherrypy.url(qs = cherrypy.request.query_string, relative = "server")},
                                     "subscriptions": []
                                    }
                                }

        # Iterate the cursor and add to the linklist
        for subId in subscriptionIds:
            serverSelfReferencingUri = cherrypy.url(qs=cherrypy.request.query_string, relative='server')
            href = {"href": f"{serverSelfReferencingUri}/{subId['subscriptionId']}"}
            subscriptionlinklist["_links"]["subscriptions"].append(href)

        return MecServiceMgmtApiSubscriptionLinkList.from_json(subscriptionlinklist)

    @cherrypy.tools.json_in()
    @json_out(cls=NestedEncoder)
    def applications_subscriptions_post(self, appInstanceId: str):
        """
        The GET method may be used to request information about all subscriptions for this requestor. Upon success, the response contains entity body with all the subscriptions for the requestor.

        :param appInstanceId: Represents a MEC application instance. Note that the appInstanceId is allocated by the MEC platform manager.
        :type appInstanceId: str

        :request body: Entity body in the request contains a subscription to the MEC application termination notifications that is to be created.

        :return: SerAvailabilityNotificationSubscription or ProblemDetails
        HTTP STATUS CODE: 201, 400, 403, 404
        """
        #TODO validate that appinstanceid exists
        data = cherrypy.request.json
        # The process of generating the class allows for "automatic" validation of the json and
        # for filtering after saving to the database
        availability_notification = SerAvailabilityNotificationSubscription.from_json(data)
        # Add subscriptionId required for the Subscriptions Method specified in Section 8.2.9.2
        # TODO subscriptionID generation should be inside the class
        subscriptionId = str(uuid.uuid4())
        # Add appInstanceId for internal usage
        cherrypy.thread_data.db.create("subscriptions", object_to_mongodb_dict(availability_notification,
                                        extra=dict(appInstanceId=appInstanceId,subscriptionId=subscriptionId)))

        # After generating the subscription we need to, according to the users filtering criteria,
        # get the services that match the filtering criteria.
        # Afterwards, execute a callback in order for the client to know which services are up and running

        # Obtain the notification filtering criteria
        query = availability_notification.filteringCriteria.to_query()
        # Query the database for services that are already registered and that match the filtering criteria
        data = cherrypy.thread_data.db.query_col("services", query)
        # Transform cursor into a list
        data = list(data)
        # From the existing services that match the subscription criteria generate the notifications
        # According to Section 8.1.4.2-1 of MEC 011 _links contains hyperlinks to the related subscription
        subscription = f"/applications/{appInstanceId}/subscriptions/{subscriptionId}"
        if len(data)>0:
            serviceNotification = ServiceAvailabilityNotification.from_json_service_list(data=data,subscription=subscription,changeType="ADDED")
            # Execute the callback with the data to be sent
            # default sleep_time is 10 due to the fact that the subscriber hasn't receive his request response
            # stating that he will receive subscription notifications
            CallbackController.execute_callback(availability_notifications=availability_notification,
                                                data=serviceNotification)

        # Return the data that was sent via the post message with added _links that references to current subscriptionId
        server_self_referencing_uri = cherrypy.url(qs=cherrypy.request.query_string, relative='server')
        _links = Links(_self=LinkType(f"{server_self_referencing_uri}/{subscriptionId}"))
        availability_notification._links = _links
        # According to Table 8.2.8.3.4-2 we need to add the location to header
        # TODO ASK ETSI WHATS THE DIFFERENCE BETWEEN _LINK AND THIS LOCATION HEADER BECAUSE BOTH SEEM TO POINT TO SAME THING
        cherrypy.response.headers["Location"] = subscription

        ## KAFKA
        import socket
        from kafka import KafkaProducer
        kafka_ip = socket.gethostbyname("kafka")
        kafka_port = 9092
        producer = KafkaProducer(bootstrap_servers=f"{kafka_ip}:{kafka_port}")
        producer.send('mep', f'MEC APP with appInstanceId {appInstanceId} has created a subscriptionnotification for services'.encode())
        producer.flush()

        return availability_notification

    @json_out(cls=NestedEncoder)
    def applications_subscriptions_get_with_subscription_id(
        self, appInstanceId: str, subscriptionId: str
    ):
        """
        The GET method requests information about a subscription for this requestor. Upon success, the response contains entity body with the subscription for the requestor.

        :param appInstanceId:  Represents a MEC application instance. Note that the appInstanceId is allocated by the MEC platform manager.
        :type appInstanceId: str
        :param subscriptionId: Represents a subscription to the notifications from the MEC platform.
        :type subscriptionId: str

        :return: SerAvailabilityNotificationSubscription or ProblemDetails
        HTTP STATUS CODE: 200, 400, 403, 404
        """
        # Obtain the subscriptionIds that match the appInstanceId and subscriptionId
        # TODO validate the authorization to get the subscriptions of the appinstanceid (i.e if this person can query for this appinstanceid)
        # Only one result is expected so use find_one to limit the database search and decrease response time
        subscription = cherrypy.thread_data.db.query_col("subscriptions",
                                                            query=dict(appInstanceId=appInstanceId,
                                                                       subscriptionId=subscriptionId),
                                                            fields=dict(subscriptionId=0),
                                                            find_one=True)


        # In the database we also save the appInstanceId but it isn't supposed to be returned or used to create the object
        subscription.pop("appInstanceId",None)
        availability_notification = SerAvailabilityNotificationSubscription.from_json(subscription)
        # Add _links to class before sending
        server_self_referencing_uri = cherrypy.url(qs=cherrypy.request.query_string, relative='server')
        _links = Links(_self=LinkType(f"{server_self_referencing_uri}/{subscriptionId}"))
        availability_notification._links = _links

        return availability_notification


    @json_out(cls=NestedEncoder)
    def applications_subscriptions_delete(
        self, appInstanceId: str, subscriptionId: str
    ):
        """
        This method deletes a mecSrvMgmtSubscription. This method is typically used in "Unsubscribing from service availability event notifications" procedure.

        :param appInstanceId: Represents a MEC application instance. Note that the appInstanceId is allocated by the MEC platform manager.
        :type appInstanceId: str
        :param subscriptionId: Represents a subscription to the notifications from the MEC platform.
        :type subscriptionId: str

        :return: No Content or ProblemDetails
        HTTP STATUS CODE: 204, 403, 404
        """
        # TODO LOGIC
        cherrypy.response.status = 204
        return
