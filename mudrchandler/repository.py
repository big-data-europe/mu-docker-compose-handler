import aiosparql
from aiohttp import ClientSession
from urllib.parse import urlparse

class Repository():
    def __init__(self, data):
        assert isinstance(data, dict)
        assert "location" in data
        assert "uuid" in data
        self._location = data["location"]
        self._uuid = data["uuid"]

    @property
    def location(self):
        """
        Returns the repository's location in the form of a
        http(s) or git URL)
        """
        return self._location

    @property
    def uuid(self):
        """
        Returns the uuid corresponding to a repository in the DB
        """
        return self._uuid

    @property
    def branch(self):
        """
        Returns the repository branch or master by default
        """
        if not hasattr(self, '_branch'):
            self._branch = "master"
        return self._branch

    @property
    async def docker_compose(self):
        """
        Fetches the docker_
        """
        if not hasattr(self, '_dockercompose'):
            repository_path = urlparse(self.location)
            drc_url = "https://raw.githubusercontent.com{}/master/docker-compose.yml".format(repository_path.path)
            print(drc_url)
            # async with ClientSession() as session:
            #     async with session.get('{}/blob/master/docker-compose.yml'.format(self.location)) as resp:
            #         self._dockercompose = await resp.content.read()
        return self._dockercompose