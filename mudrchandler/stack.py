import logging
import json
from aiohttp import web
from aiosparql.escape import escape_string

logger = logging.getLogger(__name__)

class Stack():
    """
    Base class including the location and app, 
    since both types of Stacks (created with uuid or uri)
    have them
    """
    def __init__(self, data):
        assert "app" in data
        self._app = data["app"]


    @property
    def app(self):
        """
        Returns the instance of the application, needed to
        execute commands inside the run loop.
        """
        return self._app


    @property
    def branch(self):
        """
        Returns the stack branch or master by default
        """
        if not hasattr(self, '_branch'):
            self._branch = "master"
        return self._branch
    

    async def fetch_stack_value(self, predicate: str, stack_uuid) -> str:
        """
        Fetches the value of a predicate for the Stack for a
        given UUID
        """
        logger.info("Fetching information for {} in Stack UUID: {}".format(predicate, stack_uuid))
        result = await self.app.sparql.query(
            """
            SELECT DISTINCT ?o 
            FROM {{graph}}
            WHERE {
            ?s a <http://usefulinc.com/ns/doap#Stack> .
            ?s <http://mu.semte.ch/vocabularies/core/uuid> {{uuid}} .
            ?s <%s> ?o . 
            }
            """ % predicate,
            uuid=escape_string(stack_uuid)
        )
        try:
            ret_value = result['results']['bindings'][0]['o']['value']
        except IndexError:
            raise web.HTTPInternalServerError(body=json.dumps({
                "status": 500,
                "title": "Invalid UUID",
                "detail": "A Stack with an unexistent UUID: {} and predicate: {} was tried to be accessed".format(stack_uuid, predicate)
            }))
        return ret_value