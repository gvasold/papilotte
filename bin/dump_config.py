import toml

from papilotte import configuration

COMMENTS = {
    'server': {
        "strictValidation": "Set this to false to allow parameters not defined in the papi openapi spec",
        "responseValidation": "Validates responses against openapi schematas.\n" +
                              "For production use you might want set this to false",
        "debug": "Run Server in debug mode. Do not use this for production!",
        "host": "Host name the server is running on",
        "connector": "Fully qualified name of the connector package to use",
        "port": "Port number Papilotte should listen to",
    },
    'logging': {
        "logLevel": "Set the log level. Must be one of these values:\n" +
                    "'debug', 'info', 'warn', 'error'",
        "logTo": "Set the target for logging. Must be one of these values:\n" + 
                "'console', 'file', 'syslog'",
        "logFile": "The name of the log file. Only used when 'logTo' is set to 'file'",
        "maxLogFileSize": "Maximum number of bytes for the log file.\n" + 
                          "The log file will be rotated automatically if it becomes larger than this value\n" +
                          "Value can be set in Bytes, Kilobytes (k), Megabytes (m) or Gigabytes (g)\n" +
                          "Only used if 'logTo' is set to 'file",
        "keepLogFiles": "Number of old log files to keep after rotation. Only used when 'logTo' is set to 'file'",
        "logHost": "Hostname of the syslog host. Only used if 'logTo' is set to 'syslog'",
        "logPort": "Port of the syslog server. Only used if 'logTo' is set to 'syslog'"
    },
    'api': {
        "complianceLevel": "Set IPIF compliance level. Must be a value between 0 and 2",
        "specFile": "Name of the IPIF spec file to use. Change this to use a custom spec file (not recommended)",
        "basePath": "Base path for accessing the api",
        "maxSize": "Mamimum number of objects returned with one request",
        "formats": "Response formats supported by this server. At the moment only 'application/json' is implemented"
    },
    'metadata': {
        "description": "Verbal description of the data provided by this server",
        "provider": "Information about the data provider. This can be a person or institution",
        "contact": "How to contact the data provider. Eg. an email address."
    }
}

def add_comments(section, data):
    rv = []
    comments = COMMENTS.get(section, {})
    rv.append('[{}]'.format(section))
    for line in toml.dumps(data).split('\n'):
        if line.strip():
            setting = line.split('=', 1)[0].strip()
            if setting in comments:
                for comment_line in comments[setting].split('\n'):
                    rv.append('  ### ' + comment_line)
            rv.append('  # ' + line)
            rv.append('')
    return rv

def add_connector_comments():
    lines = []
    lines.append("### This sections depends on the connector to use")
    lines.append('### Here an example for the default pony connector')
    lines.append('[connector]')
    lines.append('### provider sets the database to use. Allowed values are:')
    lines.append('### sqlite, postgresql, mysql, oracle')
    lines.append('provider = "sqlite"')
    lines.append('')
    lines.append("### Sets the file name for the database. Only used if 'provider' is 'sqlite'")
    lines.append("### The default value ':memory: creates a non persistent in-memory-database")
    lines.append('filename = ":memory:"')
    lines.append("### Set the host name of the database. Not used if 'provider' is 'sqlite'")
    lines.append('# host = ""')
    lines.append("### Set the port number. Can be ommitted if database server is running on default port.")
    lines.append("### Not used if 'provider' is 'sqlite'")
    lines.append('# port = ""')
    lines.append("### Set the user for connecting to the database. Not used if 'provider' is 'sqlite'")
    lines.append('# user = ""')
    lines.append("### Set the password for the database. Not used if 'provider' is 'sqlite'")
    lines.append('# password = ""')
    lines.append("### Set the database name to use. Not used if 'provider' is 'sqlite'")
    lines.append('# database = ""')
    return lines

if __name__ == '__main__':
    lines = []
    cfg = configuration.get_default_configuration()
    lines += add_comments('server', cfg['server'])
    lines += add_comments('logging', cfg['logging'])
    lines += add_comments('api', cfg['api'])
    lines += add_comments('metadata', cfg['metadata'])
    lines += add_connector_comments()
    print("\n".join(lines))
#print(toml.dumps(cfg))