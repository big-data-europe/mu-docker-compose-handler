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
        super(UUIDStack, self).__init__(data)
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
            self._location = await Stack.fetch_stack_value(self, "http://usefulinc.com/ns/doap#location", self.uuid)
        return self._location


    @property
    async def title(self):
        """
        Returns the title of the Stack
        """
        if not hasattr(self, "_title"):
            self._title = await Stack.fetch_stack_value(self, "http://purl.org/dc/terms/title", self.uuid)
        return self._title


    @property
    async def icon(self):
        """
        Returns the icon of the Stack
        """
        if not hasattr(self, "_icon"):
            self._icon = await Stack.fetch_stack_value(self, "https://www.w3.org/1999/xhtml/vocab#icon", self.uuid)
        return self._icon