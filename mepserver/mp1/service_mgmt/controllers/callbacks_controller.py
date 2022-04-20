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
import cherrypy
import requests
from mp1.models import *
import time
from typing import Union
from cherrypy.process.plugins import BackgroundTask

class CallbackController:
    @staticmethod
    def execute_callback(availability_notifications: Union[List[SerAvailabilityNotificationSubscription],SerAvailabilityNotificationSubscription],
                         data: dict, sleep_time: int = 10):
        """
        Send the callback to the specified url (i.e callbackreference)
        Start a cherrypy BackgroundTask https://docs.cherrypy.dev/en/latest/pkg/cherrypy.process.plugins.html
        Pass the callbackreference (i.e url to call) and the data

        :param availability_notifications: The python object containing the callbackreference
        :type availability_notifications: AvailabilityNotification
        :param data: Data containing the services that match the filtering criteria of the subscriber
        :type data: Json/Dict
        """
        if availability_notifications:
            callback_task = BackgroundTask(
                interval=0, function=CallbackController._callback_function, args=[availability_notifications,data,sleep_time],
                bus=cherrypy.engine)
            # Add the callback_task to itself to allow to cancel itself
            # (needed since BackgroundTask is usually repeatable)
            callback_task.args.insert(0,callback_task)
            callback_task.start()

    @staticmethod
    def _callback_function(task, availability_notifications: Union[List[SerAvailabilityNotificationSubscription], SerAvailabilityNotificationSubscription],
                           data: dict, sleep_time: int):
        """
        :param task: Reference to the background task itself
        :type task: BackgroundTask
        :param availability_notifications:  Used to obtain the callback references
        :type availability_notifications: SerAvailabilityNotificationSubscription or List of SerAvailabilityNotificationSubscription (each one contains a callbackreference)
        :param data: Data containing the information to be sent in a callback
        :type data: Json/Dict
        """
        cherrypy.log("Starting callback function")
        # Wait for a bit since client might still be receiving the answer from the subscriptions and thus might
        # not be ready to receive the callback
        time.sleep(sleep_time)
        # Check if the type is a list or not due to the two instances where callback can be used
        # Instance 1: A new services is created and thus we need to check all subscriptions and
        # send the new service to each
        # Instance 2: Service creates a subscription with filtering criteria x and we send the
        # list of existing services that match

        # Instance 1 - A list of SerAvailabilityNotifications and the data of the newly added service
        # Add the _links.subscription
        if isinstance(availability_notifications, list):
            for callbackUrl in availability_notifications:
                # When using this method (i.e when a service registers and there are various subscribers)
                # we need to append the subscription (_links) parameter to the ServiceAvailabilityNotification
                # this data is storage in the SerAvailabilityNotificationSubscription object
                appInstanceId = callbackUrl.appInstanceId
                subscriptionId = callbackUrl.subscriptionId
                data._links = Subscription(href=f"/applications/{appInstanceId}/subscriptions/{subscriptionId}")
                requests.post(callbackUrl.callbackReference,
                              data=json.dumps(data,cls=NestedEncoder), headers={'Content-Type': 'application/json'})
        # Instance 2
        else:
            requests.post(availability_notifications.callbackReference,
                          data=json.dumps(data,cls=NestedEncoder), headers={'Content-Type': 'application/json'})
        task.cancel()