"""Callback functions for /describe endpoint.
"""
from flask import current_app as app

def get_description():
    "Generate the describe info."
    data = {
        'complianceLevel': app.config['PAPI_COMPLIANCE_LEVEL'],
        'contact': app.config['PAPI_METADATA']['contact'],
        'description': app.config['PAPI_METADATA']['description'],
        'provider': app.config['PAPI_METADATA']['provider'],
        'formats': app.config['PAPI_FORMATS']
    }
    return data
        
