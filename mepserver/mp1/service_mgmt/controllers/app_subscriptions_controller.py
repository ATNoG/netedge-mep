import cherrypy
import json
import sys
sys.path.append('../../')
from mp1.models import *
from mp1.model_expections import *

class SubscriptionsController:

    @cherrypy.tools.json_out()
    def applications_subscriptions_get(self,appInstanceId: int):
        """
        The GET method may be used to request information about all subscriptions for this requestor. Upon success, the response contains entity body with all the subscriptions for the requestor.

        :param appInstanceId: Represents a MEC application instance. Note that the appInstanceId is allocated by the MEC platform manager.
        :type appInstanceId: str

        :return: MecServiceMgmtApiSubscriptionLinkList or ProblemDetails
        HTTP STATUS CODE: 200, 400, 403, 404
        """
        if cherrypy.request.method == "GET":
            #TODO CREATE REALLY CONNECTION
            data = {"_links":{"self":{"href":"data"},"subscriptions":{"href":"data","subscription":"data"}}}
            service = MecServiceMgmtApiSubscriptionLinkList(**data)
            return vars(service)
        else:
            # TODO PROPERLY FIX INVALID REQUESTS
            cherrypy.response.status = 400
            problem_detail = ProblemDetails(type="",
                                            title="Invalid HTTP Request Method",
                                            status=400,
                                            detail="Endpoint only accepts GET requests",
                                            instance="")

            return vars(problem_detail)

    @cherrypy.tools.json_in()
    def applications_subscriptions_post(self,appInstanceId: int):
        """
        The GET method may be used to request information about all subscriptions for this requestor. Upon success, the response contains entity body with all the subscriptions for the requestor.

        :param appInstanceId: Represents a MEC application instance. Note that the appInstanceId is allocated by the MEC platform manager.
        :type appInstanceId: str

        :request body: Entity body in the request contains a subscription to the MEC application termination notifications that is to be created.

        :return: SerAvailabilityNotificationSubscription or ProblemDetails
        HTTP STATUS CODE: 201, 400, 403, 404
        """
        if cherrypy.request.method == "POST":
            # TODO VALIDATE THE JSON and use Instance ID
            input_json = cherrypy.request.json
            try:
                availability_notification = SerAvailabilityNotificationSubscription.from_json(input_json)

                return json.dumps(availability_notification,cls=NestedEncoder)
            except TypeError as e:
                cherrypy.log(traceback=True)
                problem_detail = ProblemDetails(type="",
                                                title="Invalid href",
                                                status=400,
                                                detail="Resource URI didn't meet specifications",
                                                instance="")
                return vars(problem_detail)
            except InvalidIdentifier as e:
                problem_detail = ProblemDetails(type="",
                                                title="No identifier was sent",
                                                status=400,
                                                detail="Application Subscription POST Method requires at least one filteringCriteria Identifier (serNames,serCategories,serInstanceIds)",
                                                instance="")
                return vars(problem_detail)
        else:
            # TODO PROPERLY FIX INVALID REQUESTS
            cherrypy.response.status = 400
            problem_detail = ProblemDetails(type="",
                                            title="Invalid HTTP Request Method",
                                            status=400,
                                            detail="Endpoint only accepts GET requests",
                                            instance="")
            return vars(problem_detail)

    def applications_subscriptions_get_with_subscription_id(self,appInstanceId: int, subscriptionId: int):
        """
        The GET method requests information about a subscription for this requestor. Upon success, the response contains entity body with the subscription for the requestor.

        :param appInstanceId:  Represents a MEC application instance. Note that the appInstanceId is allocated by the MEC platform manager.
        :type appInstanceId: str
        :param subscriptionId: Represents a subscription to the notifications from the MEC platform.
        :type subscriptionId: str

        :return: SerAvailabilityNotificationSubscription or ProblemDetails
        HTTP STATUS CODE: 200, 400, 403, 404
        """

        return None

    def applications_subscriptions_delete(self,appInstanceId: int, subscriptionId: int):
        """
        This method deletes a mecSrvMgmtSubscription. This method is typically used in "Unsubscribing from service availability event notifications" procedure.

        :param appInstanceId: Represents a MEC application instance. Note that the appInstanceId is allocated by the MEC platform manager.
        :type appInstanceId: str
        :param subscriptionId: Represents a subscription to the notifications from the MEC platform.
        :type subscriptionId: str

        :return: No Content or ProblemDetails
        HTTP STATUS CODE: 204, 403, 404
        """
        return None
