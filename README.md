# Papilotte

Papilotte is a flexible and extensible server which implements the [IPIF API](https://github.com/GVogeler/prosopogrAPhI).

The server is currently being developed as a tool for testing the API. Once the IPIF API is stable, 
Papilotte can be used as a stand-alone server with integrated database or as a frontend or proxy to 
existing prosopographic resources to provide them via the IPIF interface.

## Installation

**Attention**: Papilotte is in alpha state and will undergo frequent changes. 

### Supported Python versions
Papilotte needs Python Version 3.5 or above.

### Use a virtual environment
As usually it is recommended to keep Papilotte in it's own virtual environment. To create the environment run

~~~
python3 -m venv <venv_dir>
~~~

Where ``<venv_dir>`` can be any path on your computer. The virtual environment will be created under this path.

### Activate the virtual environment

On Linux or OSX run

~~~
source <venv_path>/bin/activate
~~~

On Windows run

~~~
<venv_path>\Scripts\activate.bat
~~~

### Install Papilotte

Papilotte is not installable via pip yet. 
At the moment the only way to install it is do clone the repository and then run

~~~
python setup.py install  (or python setup.py develop)
~~~


## Configuring Papilotte

The recommended way to configure Papilotte is to create a new configuration file, eg. ``papilotte.yml``.

To serve server factoids from your own json file, add these lines to your configuration:

~~~
connector: papilotte.connectors.json
json_file: <path_to_your_json_file>
~~~

## Running Papilotte

Make sure your virtual environment is active before running Papilotte.

### Run Papilotte in development/tryout mode

~~~
python -m papilotte run --config-file <path to configuration file>
~~~

this will start the built in web server. Default port is 5000, but this can 
be changed via '--port' or a ``port:`` entry in the configuration file. 

After the server has startet, you should be able to access the factoids at http://localhost:5000/api/factoids

**Attention:** The built in http server is not meant to be used in production! To put your Papilotte Server on the web,
use a WSGI Server like gunicorn, waitress, uWSGI, or Apache mod_wsgi

### Running papilotte with gunicorn

Gunicorn can be heavily configured. Please read the documentation at https://gunicorn.org/#docs. Here a minimalistic example:

~~~
gunicorn "papilotte:create_app(config_file='<path_to_your_config_file>')"
~~~

