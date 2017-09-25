# mu-docker-compose-handler

Microservice to download the docker-compose.yml from a given repository's URL and store it in a graph database.
The service will receive the repository's id & the location string, fetch the docker-compose.yml file
from that location, save it on the database, and then create a link in the database from the repository to the 
compose file.

# Workflow Diagram


# Quick start

```python
docker run -it --rm \
    --link database:some_container \
    -v /var/run/docker.sock:/var/run/docker.sock \
    mu-docker-compose-handler
Overrides
```

The default graph can be overridden by passing the environment variable MU_APPLICATION_GRAPH to the container.
The default SPARQL endpoint can be overridden by passing the environment variable MU_SPARQL_ENDPOINT to the container.

# Usage




