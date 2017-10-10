import logging
import json
from mudrchandler.stack import Stack

logger = logging.getLogger(__name__)

class URIStack(Stack):
    """
    Stack created when deltas are received in /update
    entrypoint and a stack creation is detected
    """
    def __init__(self, data):
        super(URIStack, self).__init__(data)
        assert isinstance(data, dict)
        assert "uri" in data
        self._uri = data["uri"]


    @property
    def uri(self) -> str:
        """
        Returns the URI of the stack.
        """
        return self._uri


    @property
    async def uuid(self) -> str:
        """
        Returns the uuid of the Stack
        """
        if not hasattr(self, "_uuid"):
            result = await self.app.sparql.query("""
                SELECT DISTINCT ?o
                WHERE {
                    <{{uri}}> <http://mu.semte.ch/vocabularies/core/uuid> ?o .
                }
                """, uri=self.uri)
            self._uuid = result['results']['bindings'][0]['o']['value']
        return self._uuid


    @property
    async def location(self):
        """
        Returns the location of the Stack
        """
        if not hasattr(self, "_location"):
            self._location = await Stack.fetch_stack_value(self, "http://usefulinc.com/ns/doap#location", await self.uuid)
        return self._location


    @property
    async def title(self):
        """
        Returns the title of the Stack
        """
        if not hasattr(self, "_title"):
            self._title = await Stack.fetch_stack_value(self, "http://purl.org/dc/terms/title", await self.uuid)
        return self._title


    @property
    async def icon(self):
        """
        Returns the icon of the Stack
        """
        if not hasattr(self, "_icon"):
            self._icon = await Stack.fetch_stack_value(self, "https://www.w3.org/1999/xhtml/vocab#icon", await self.uuid)
        return self._icon

    
