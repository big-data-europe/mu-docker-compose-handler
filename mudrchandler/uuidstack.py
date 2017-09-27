import logging
from mudrchandler.stack import Stack
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
    async def uri(self):
        """
        Fetches the URI of the stack using the UUID.
        """
        if not hasattr(self, "_uri"):
            logger.info("Fetching URI for Stack UUID: {}".format(self.uuid))
            result = await self.app.sparql.query(
                """
                SELECT DISTINCT ?uri
                FROM {{graph}}
                WHERE {
                ?uri a <http://usefulinc.com/ns/doap#Stack> .
                ?uri <http://mu.semte.ch/vocabularies/core/uuid> {{uuid}} .
                }
                """,
                uuid=escape_string(self.uuid)
            )
            self._uri = result['results']['bindings'][0]['uri']['value']
        return self._uri