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
from cherrypy.process.plugins import BackgroundTask

class CallbackController:

    def execute_callback(self,availability_notification, data):
        """
        Send the callback to the specified url (i.e callbackreference)
        Start a cherrypy BackgroundTask https://docs.cherrypy.dev/en/latest/pkg/cherrypy.process.plugins.html
        Pass the callbackreference (i.e url to call) and the data

        :param availability_notification: The python object containing the callbackreference
        :type availability_notification: AvailabilityNotification
        :param data: Data containing the services that match the filtering criteria of the subscriber
        :type data: Json/Dict
        """

        # Only send callback if there is a service that matches the filtering criteria
        if len(list(data))>0:
            callback_task = BackgroundTask(
                interval=0, function=self._callback_function, args=[availability_notification.callbackReference,data],
                bus=cherrypy.engine)
            # Add the callback_task to itself to allow to cancel itself (needed since BackgroundTask is usually repeatable)
            callback_task.args.insert(0,callback_task)
            callback_task.start()

    def _callback_function(self, task, callbackreference, data):
        """

        :param task: Reference to the background task itself
        :type task: BackgroundTask
        :param callbackreference: URL containing the reference where the client will receive the callbackdata
        :type callbackreference: String
        :param data: Data containing the information to be sent in a callback
        :type data: Json/Dict
        """
        cherrypy.log("Starting callback function")
        # Wait for a bit since client might still be receiving the answer from the subscriptions and thus might
        # not be ready to receive the callback
        time.sleep(10)
        requests.post(callbackreference,
                      data=json.dumps(list(data), cls=NestedEncoder), headers={'Content-Type': 'application/json'})
        task.cancel()