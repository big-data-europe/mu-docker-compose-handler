import logging
import json
from mudrchandler.stack import Stack
from aiohttp import web
from aiosparql.escape import escape_string

logger = logging.getLogger(__name__)


class UUIDStack(Stack):
    """
    Stack created when the entrypoint is /createdrc,
    meaning the call came from the frontend, and therefore
    only the UUID of the stack was provided.
    """
    def __init__(self, data):
        super().__init__(data)
        assert isinstance(data, dict)
        assert "uuid" in data
        self._uuid = data["uuid"]

    @property
    def uuid(self):
        """
        Returns the uuid corresponding to a stack in the DB
        """
        return self._uuid

    @property
    async def location(self):
        """
        Returns the location of the Stack
        """
        if not hasattr(self, "_location"):
            self._location = await self.fetch_stack_value("http://usefulinc.com/ns/doap#location")
        return self._location


    @property
    async def title(self):
        """
        Returns the title of the Stack
        """
        if not hasattr(self, "_title"):
            self._title = await self.fetch_stack_value("http://purl.org/dc/terms/title")
        return self._title

    @property
    async def icon(self):
        """
        Returns the icon of the Stack
        """
        if not hasattr(self, "_icon"):
            self._icon = await self.fetch_stack_value("https://www.w3.org/1999/xhtml/vocab#icon")
        return self._icon


    async def fetch_stack_value(self, predicate: str) -> str:
        """
        Fetches the value of a predicate for the Stack for a
        given UUID
        """
        logger.info("Fetching information for Stack UUID: {}".format(self.uuid))
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
            uuid=escape_string(self.uuid)
        )
        try:
            ret_value = result['results']['bindings'][0]['o']['value']
        except IndexError:
            raise web.HTTPInternalServerError(body=json.dumps({
                "status": 500,
                "title": "Invalid UUID",
                "detail": "A Stack with an unexistent UUID was tried to be accessed"
            }))
        return ret_value