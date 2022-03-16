from mp1.service_mgmt.controllers.app_subscriptions_controller import SubscriptionsController
from mp1.service_mgmt.controllers.app_services_controller import ServicesController
import cherrypy

if __name__ == "__main__":
    dispatcher = cherrypy.dispatch.RoutesDispatcher()
    # Todo load from config file
    ###########################
    # Subscription Controller #
    ###########################

    dispatcher.connect(name='Get an applicationInstanceId Subscriptions',
                       action='applications_subscriptions_get',
                       controller=SubscriptionsController,
                       route='/applications/:appInstanceId/subscriptions',
                       conditions=dict(method=["GET"]))

    dispatcher.connect(name='Get an applicationInstanceId Subscriptions',
                       action='applications_subscriptions_get_with_subscription_id',
                       controller=SubscriptionsController,
                       route='/applications/:appInstanceId/subscriptions/:subscriptionId',
                       conditions=dict(method=["GET"]))

    dispatcher.connect(name='Create applicationInstanceId Subscriptions',
                       action='applications_subscriptions_post',
                       controller=SubscriptionsController,
                       route='/applications/:appInstanceId/subscriptions',
                       conditions=dict(method=["POST"]))

    dispatcher.connect(name='Delete applicationInstanceID Subscriptions with subscriptionId',
                       action='applications_subscriptions_delete',
                       controller=SubscriptionsController,
                       route='/applications/:appInstanceId/subscriptions/:subscriptionId',
                       conditions=dict(method=["DELETE"]))

    #######################
    # Services Controller #
    #######################
    dispatcher.connect(name='Get service from InstanceId',
                      action='applications_services_get',
                      controller=ServicesController,
                      route='/applications/:appInstanceId/services',
                      conditions=dict(method=["GET"]))

    conf = {'/':{'request.dispatch':dispatcher}}
    cherrypy.tree.mount(None,'/mec_service_mgmt/v1',config=conf)
    cherrypy.engine.start()