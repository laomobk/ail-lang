
from copy import copy
from typing import List, Dict, Union

from .objects import AILImporter as _AILImporter, AILStruct as _AILStruct

from . import exceptions as _exceptions


_IMPORTER = _AILImporter()


def ail_input(prompt: str, value_count: int):
    m = input(prompt)
    if value_count == 1:
        return m
    if value_count == 0:
        return None

    vals = m.split(maxsplit=value_count)
    if len(vals) < value_count:
        raise _exceptions.AILInputException('')

    return vals


def ail_import(
        mode: int, name: str, namespace: dict, alias: str=None, members: List[str]=[]):
    if alias is None:
        alias = name

    return _IMPORTER.import_module(mode, name, namespace, alias, members)


def contains(o, iterable):
    return o in iterable


def make_struct(name: str, members: List[str], protected: List[str]) -> _AILStruct:
    if not isinstance(name, str):
        raise TypeError('struct name must be string')
    if not isinstance(members, list) or not isinstance(protected, list):
        raise TypeError('struct members or protecteds must be list')
    return _AILStruct(name, members, protected)


def new_struct_object(struct: _AILStruct, attrs: Union[Dict, List] = None):
    if not isinstance(struct, _AILStruct):
        raise TypeError('new() requires a struct')

    obj = copy(struct)
    obj.__ail_as_object__ = True

    if attrs is None:
        return obj

    members_len = len(obj.__ail_members__)

    if isinstance(attrs, dict):
        items = attrs.items()
        try:
            obj.__ail_as_instance__ = True
            for k, v in items:
                setattr(obj, k, v)
        finally:
            obj.__ail_as_instance__ = False
    elif isinstance(attrs, list):
        if len(attrs) != members_len:
            raise ValueError('struct \'%s\' initializing needs %s value(s)' % 
                             (obj.__ail_struct_name__, members_len))
        try:
            obj.__ail_as_instance__ = True
            for k, v in zip(obj.__ail_members__, attrs):
                setattr(obj, k, v)
        finally:
            obj.__ail_as_instance__ = False
    else:
        raise ValueError('struct \'%s\' initializing needs a list' % 
                         obj.__ail_struct_name__)

    return obj

