import logging
from os import environ as ENV
from aiohttp import web
from aiohttp.client_exceptions import ClientConnectionError
from aiosparql.client import SPARQLClient
from mudrchandler.repository import Repository
from aiosparql.syntax import escape_string, IRI, Node, RDF, RDFTerm, Triples

logger = logging.getLogger(__name__)


if ENV.get("ENV", "prod").startswith("dev"):
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


class Application(web.Application):
    # NOTE: override default timeout for SPARQL queries
    sparql_timeout = 60

    @property
    def sparql(self):
        """
        The SPARQL client
        """
        if not hasattr(self, '_sparql'):
            self._sparql = SPARQLClient(ENV['MU_SPARQL_ENDPOINT'],
                                        graph=IRI(ENV['MU_APPLICATION_GRAPH']),
                                        loop=self.loop,
                                        read_timeout=self.sparql_timeout)
        return self._sparql


async def handle_fetch_drc(request):
    """
    Handle the request to fetch a docker-compose 
    file & save it into the database.
    """
    try:
        data = await request.json()
    except:
        raise web.HTTPBadRequest(body="invalid json")
    repository = Repository(data)
    print (await repository.docker_compose)
    return web.Response(text="all good")

async def cleanup(app):
    """
    Properly close SPARQL client
    """
    await app.sparql.close()

# Create a new application and set the routes to handle requests
app = Application()
app.router.add_post('/', handle_fetch_drc)
# app.router.add_route('*', '/path', all_handler)
app.on_cleanup.append(cleanup)