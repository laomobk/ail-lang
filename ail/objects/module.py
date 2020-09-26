# module object

from .types import I_MODULE_TYPE

from ..core.aobjects import AILObject, AILObjectType, ObjectCreater
from ..core.error import AILRuntimeError


def module_init(self, module_name: str, namespace: dict):
    self['__namespace__'] = namespace
    self['__name__'] = module_name


def module_setattr(self, name: str, value: AILObject):
    namespace = self['__namespace__']

    assert isinstance(name, str)

    namespace[name] = value


def module_getattr(self, name: str) -> AILObject:
    namespace = self['__namespace__']

    assert isinstance(name, str)

    if name not in namespace:
        return AILRuntimeError(
                'module \'%s\' has no attribute \'%s\'' % (
                    self['__name__'], name))

    return namespace[name]


def module_str(self) -> str:
    return '<module \'%s\'>' % self['__name__']


MODULE_TYPE = AILObjectType('<module type>', I_MODULE_TYPE, 
                            __init__=module_init,
                            __setattr__=module_setattr,
                            __getattr__=module_getattr,
                            __str__=module_str,
                            __repr__=module_str,
                            )


def new_module_object(module_name: str, namespace: dict) -> AILObject:
    return ObjectCreater.new_object(MODULE_TYPE, module_name, namespace)

