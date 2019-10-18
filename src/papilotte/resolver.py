"""A custom resolver which maps operationIds to functions in modules.

A request to eg. `GET /api/factoids` will be mapped to 
`api.factoids.get_factoids` because the operationId of this operation
is `getFactoids`.

This could also be done using qualified operationIds but I try to 
keep packages/modules out of the spec.
"""
import re
from connexion.resolver import RestyResolver

class PapiResolver(RestyResolver):

    def resolve_operation_id(self, operation):
        """
        Resolves the operationId in snake_case using a mechanism similar to RestyResolver.

        eg. `GET /api/factoids` is resolved to `api.factoids.get_factoids()` because the operationId is `getFactoids`.

        Uses RestyResolver as fallback for missing operationIds.
        """
        if operation.operation_id:
            operation_id = RestyResolver.resolve_operation_id(self, operation)
            pythonic_operation_id = re.sub(r'([A-Z])', lambda m: '_' + m.group(1).lower(), operation_id)
            path_match = re.search(r'^/?(?P<resource_name>([\w\-](?<!/))*)(?P<trailing_slash>/*)(?P<extended_path>.*)$', 
                                   operation.path)
            resource_name = path_match.group('resource_name')
            return self.default_module_name + '.' + resource_name + "." + pythonic_operation_id 

        return self.resolve_operation_id_using_rest_semantics(operation)