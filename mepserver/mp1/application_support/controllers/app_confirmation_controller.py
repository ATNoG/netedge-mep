import sys

import cherrypy

sys.path.append('../../')
from mp1.models import *

class ApplicationConfirmationController:

    @cherrypy.tools.json_in()
    @json_out(cls=NestedEncoder)
    def application_confirm_ready(self, appInstanceId: str):
        return None

    @cherrypy.tools.json_in()
    @json_out(cls=NestedEncoder)
    def application_confirm_termination(self, appInstanceId: str):
        return None
