from mp1.service_mgmt.controllers.app_subscriptions_controller import SubscriptionsController
import cherrypy

if __name__ == "__main__":
    dispatcher = cherrypy.dispatch.RoutesDispatcher()
    dispatcher.connect(name='Get an applicationInstanceId Subscriptions',
                       action='applications_subscriptions_get',
                       controller=SubscriptionsController,
                       route='/applications/:appInstanceId/subscriptions',
                       conditions=dict(method=["GET"]))

    dispatcher.connect(name='Create applicationInstanceId Subscriptions',
                       action='applications_subscriptions_post',
                       controller=SubscriptionsController,
                       route='/applications/:appInstanceId/subscriptions',
                       conditions=dict(method=["POST"]))

    conf = {'/':{'request.dispatch':dispatcher}}
    cherrypy.tree.mount(None,'/mec_service_mgmt/v1',config=conf)
    cherrypy.engine.start()