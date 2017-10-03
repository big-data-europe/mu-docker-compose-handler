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
    def location(self):
        """
        Returns the stack's location in the form of a
        http(s) or git URL)
        """
        return self._location

    @property
    def branch(self):
        """
        Returns the stack branch or master by default
        """
        if not hasattr(self, '_branch'):
            self._branch = "master"
        return self._branch