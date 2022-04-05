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
import requests
import cherrypy

sys.path.append("../../")
from mp1.models import *


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
        if cherrypy.request.method == "GET":
            # TODO CREATE REALLY CONNECTION
            data = {
                "_links": {
                    "self": {"href": "http://google.com"},
                    "subscriptions": [
                        {"href": "http://google.com", "subscriptionType": "data"}
                    ],
                }
            }
            service = MecServiceMgmtApiSubscriptionLinkList.from_json(data)
            return service
        else:
            # TODO PROPERLY FIX INVALID REQUESTS
            cherrypy.response.status = 400
            problem_detail = ProblemDetails(
                type="",
                title="Invalid HTTP Request Method",
                status=400,
                detail="Endpoint only accepts GET requests",
                instance="",
            )

            return vars(problem_detail)

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

        data = cherrypy.request.json
        # The process of generating the class allows for "automatic" validation of the json and for filtering after saving to the database
        availability_notification = SerAvailabilityNotificationSubscription.from_json(data)
        cherrypy.thread_data.db.create("subscriptions", object_to_mongodb_dict(availability_notification, extra=dict(appInstanceId=appInstanceId)))

        # After generating the subscription we need to, according to the users filtering criteria, get the services that match
        # and process to execute a callback in order for him to know which services are up and running so that he can subscribe to them

        # Obtain the notification filtering criteria
        query = availability_notification.filteringCriteria.to_json(query=True)
        # Query the database for services that are already registered and that match the filtering criteria
        data = cherrypy.thread_data.db.query_col("services", query)
        # Data is a pymongo cursor we first need to convert it into a json serializable object
        # Since this query is supposed to return various valid Services we can simply convert into a list prior to encoding

        # Send the callback to the specified url (i.e callbackreference)
        # TODO Transform this into CELERY otherwise when a lot of services exist it will be a bottleneck
        # TODO remove try except block - only used during development since we may not have the other webserver up
        try:
            requests.post(f"{availability_notification.callbackReference}/callbackReference",
                          data=json.dumps(list(data), cls=NestedEncoder), headers={'Content-Type': 'application/json'})
        except:
            pass
        # Return the data that was sent via the post message
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
        data = json.loads(
            '{"subscriptionType":"string","callbackReference":"http://www.google1.com","_links":{"self":{"href":"http://www.google.com"},"subscriptions":[{"href":"http://www.google.com","subscriptionType":"Normal"}]},"filteringCriteria":{"serInstanceIds":["string"],"serNames":["string"],"serCategories":[{"href":"http://www.google.com","id":"string","name":"string","version":"string"}],"states":["ACTIVE"],"isLocal":true}}'
        )
        availability_notification = SerAvailabilityNotificationSubscription.from_json(
            data
        )
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
