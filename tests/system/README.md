# System tests

Test the http interface of papilotte against mock data.

These tests need the server started with the mock connector on port 16165.
This is handled automaticall, but for debugging it might be helpfull, to 
start the server by hand in debug mode:

~~~
python -m papilotte run --p 16165 -n papilotte.connectors.mock
~~~

Make sure to set ``AUTOSTART_SERVER`` to ``False`` in contest.py if you plan
to use to start the server by hand.
