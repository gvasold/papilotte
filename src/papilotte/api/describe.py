"""Callback functions for /describe endpoint.
"""
from papilotte import options

def get_description():
    "Generate the describe info."
    data = {
        'complianceLevel': options['compliance_level'],
        'contact': options['contact'],
        'description': options['description'],
        'provider': options['provider'],
        'formats': options['formats']
    }
    return data
