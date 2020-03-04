import logging
from papilotte import server


def test_configure_logging_with_file():
    cfg = {
        'logLevel': 'info',
        'logTo': 'file',
        'logFile': '/tmp/foo.log',
        'maxLogFileSize': '20000',
        'keepLogFiles': 5
    }
    server.configure_logging(False, **cfg)
    logger = logging.getLogger('papilotte')
    assert logger.level == logging.INFO
    handler = logger.handlers[0]
    assert isinstance(handler, logging.handlers.RotatingFileHandler)
    assert handler.baseFilename == cfg['logFile']
    assert handler.maxBytes == int(cfg['maxLogFileSize'])
    assert handler.backupCount == cfg['keepLogFiles']

def test_configure_with_syslog():
    cfg =  {
        'logLevel': 'info',
        'logTo': 'syslog',
        # This must be accessible!
        'logHost': 'localhost',
        'logPort': 514
        }   
    server.configure_logging(False, **cfg) 
    logger = logging.getLogger('papilotte')
    assert logger.level == logging.INFO
    handler = logger.handlers[1]
    assert isinstance(handler, logging.handlers.SysLogHandler)
    log_host, log_port = handler.address
    assert log_host == 'localhost'
    assert log_port == 514

def test_create_app():
    app = server.create_app()
    cfg = app.app.config
    assert cfg['PAPI_CONNECTOR_MODULE']
    assert cfg['PAPI_CONNECTOR_CONFIGURATION']
    assert cfg['PAPI_MAX_SIZE'] == 200
    assert cfg['PAPI_COMPLIANCE_LEVEL'] == 1
    assert cfg['PAPI_METADATA']['contact'] == "No contact information available"
     