import sys

import cherrypy

sys.path.append('../../')
from mp1.models import *

class TransportsController:

    @json_out(cls=NestedEncoder)
    def transports_get(self):
        """
        This method retrieves information about a list of available transports. This method is typically used by a service-producing application to discover transports provided by the MEC platform in the "transport information query" procedure

        :return: TransportInfo or ProblemDetails
        HTTP STATUS CODE: 200, 400, 403, 404
        """
        data = json.loads("{\"id\":\"string\",\"name\":\"string\",\"endpoint\":{\"uris\":[\"http://www.google.com\",\"http://www.google.com\"]},\"description\":\"string\",\"type\":\"REST_HTTP\",\"protocol\":\"string\",\"version\":\"string\",\"security\":{\"oAuth2Info\":{\"grantTypes\":[\"OAUTH2_AUTHORIZATION_CODE\"],\"tokenEndpoint\":\"string\"}},\"implSpecificInfo\":{}}")
        transportInfo = TransportInfo.from_json(data)
        return transportInfo