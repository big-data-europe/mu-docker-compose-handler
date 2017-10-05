import logging
import asyncio
import subprocess
import json
import jsonapi_requests
from uuid import uuid1
from aiofiles import open
from os import path, environ as ENV
from aiohttp import web
from aiohttp.client_exceptions import ClientConnectionError
from aiosparql.client import SPARQLClient
from mudrchandler.uuidstack import UUIDStack
from mudrchandler.stack import Stack
from aiosparql.syntax import escape_any, escape_string, IRI, Node, RDF, RDFTerm, Triples

logger = logging.getLogger(__name__)


if ENV.get("ENV", "prod").startswith("dev"):
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


class Application(web.Application):
    sparql_timeout = 60
    run_command_timeout = 60

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


    async def run_command(self, *args, timeout=None) -> int:
        """
        Run command in subprocess and wait until completion.
        """
        if timeout is None:
            timeout = self.run_command_timeout
            
        # Create subprocess
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE, # accessible as process.stdout
            loop=self.loop)

        # Wait for the subprocess to finish
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout)
        except asyncio.TimeoutError:
            logger.warn(
                "Child process %d awaited for too long, terminating...",
                process.pid)
            try:
                process.terminate()
            except Exception:
                pass
        return process.returncode


    async def handle_fetch_drc(self, request):
        """
        Handle the request to fetch a docker-compose 
        file & save it into the database.

        Arguments:
            request: the request object coming from the 
                     /createdrc POST entrypoint
        
        Notes: 
            The structure of the data available in this
            entrypoint is:
            {
                uuid: uuid of the stack.
                location: git url of the stack
                app: instance of the application
            }

            The stacks' URI is not available in this entrypoint,
            logic to retrieve it has to be implemented.
        """
        try:
            data = await request.json()
        except:
            raise web.HTTPBadRequest(body="invalid json")

        data.update({ 'app': self })
        stack = UUIDStack(data)
        docker_compose = await self.docker_compose(stack)
        post_response = await self.create_drc_db(docker_compose, stack)
        patch_response = await self.update_stack_drc(post_response.data.id, stack)
        return web.Response(body=json.dumps({
            "data": {
                "attributes": {
                    "status": 200,
                    "message": "DockerCompose created and Stack updated"
                },
                "type": "mu-docker-compose-handler"
            }}))


    async def ensure_stack_has_drc(self, uuid: str) -> bool:
        """
        Return True if the Stack has already a docker-compose.yml
        file associated and False otherwise.

        Arguments:
            uri: the URI of the given Stack
        
        Returns: boolean 
        """
        result = await self.sparql.query("""
            ASK FROM {{graph}} WHERE { 
                ?s <http://mu.semte.ch/vocabularies/core/uuid> {{}} .
                ?s <http://swarmui.semte.ch/vocabularies/core/dockerComposeFile> ?x .
            }
            """, escape_string(uuid))
        return result['boolean']


    async def create_drc_db(self, drc: str, stack: Stack) -> str:
        """
        Create the DockerCompose model in the db using a POST request,
        and update the Stack to point to it.

        Arguments:
            drc: string with the docker-compose file contents
            stack: Stack to link the DockerCompose to
        """
        api = jsonapi_requests.Api.config({
            'API_ROOT': ENV['MU_RESOURCE_ENDPOINT'],
            'VALIDATE_SSL': False,
            'TIMEOUT': 10,
        })
        post_endpoint = api.endpoint('docker-composes')
        
        # Create the DockerCompose model
        ret = post_endpoint.post(object=jsonapi_requests.JsonApiObject(
            attributes={
                'title': "stack_{}_drc_{}".format(stack.uuid, uuid1().hex), 
                'text': drc 
            },
            type='docker-composes'))

        return ret

    async def update_stack_drc(self, drc_uuid: str, stack: Stack) -> str:
        
        # Update the link of the Stack with the new DockerCompose
        # docker_compose_uuid = ret.data.id
        api = jsonapi_requests.Api.config({
            'API_ROOT': ENV['MU_RESOURCE_ENDPOINT'],
            'VALIDATE_SSL': False,
            'TIMEOUT': 10,
        })

        icon = await stack.icon
        title = await stack.title
        location = await stack.location
        patch_endpoint = api.endpoint("stacks/{}".format(stack.uuid))
        ret = patch_endpoint.patch(object=jsonapi_requests.JsonApiObject(
            attributes={
                "icon": icon,
                "title": title,
                "location": location
            },
            id=stack.uuid,
            type="stacks",
            relationships={
                "docker-file": {
                    "data": {
                        "id": drc_uuid,
                        "type": "docker-composes"
                    }
                }
            }))
        return ret



    async def docker_compose(self, stack: Stack):
        """
        Fetches the docker-compose.yml file from the git url.
        
        Steps:
            - If the stack doesn't already have a drc
            - Clone repo & get drc.yml from file
            - Create drc model in DB with the drc.yml file
            - Create link URI -> drc model  
        """
        # TODO: Add "smart" prediction. If it is a github URL no need
        # to clone the repo, we can just download it raw (faster). The 
        # same for gitlab, aws codecommit, if we manage to somehow know
        # the urls to query from the git url, we can leap over cloning 
        # the repo
        uuid = stack.uuid
        if not await self.ensure_stack_has_drc(uuid):
            project_path = "/data/{}".format(uuid)   
            cmd = await self.run_command(
                "git", 
                "clone", 
                await stack.location, 
                "-b", 
                stack.branch, 
                project_path)
            if cmd == 0: # command finished properly
                async with open(path.join(project_path, 
                                          'docker-compose.yml'), 
                                          mode='r') as f:
                    return await f.read()

    async def cleanup(self):
        """
        Properly close SPARQL client
        """
        await self.sparql.close()


# Create a new application and set the routes to handle requests
app = Application()
app.router.add_post('/createdrc', app.handle_fetch_drc)
app.on_cleanup.append(app.cleanup)