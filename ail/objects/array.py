from collections import Iterable as IterableType
from typing import Iterable

from . import types
from . import integer
from ..core import aobjects as objs
from ..core.error import AILRuntimeError


def array_init(self: objs.AILObject, pylist: list):
    # check object
    pl = pylist.copy()

    for index, item in enumerate(pl):
        pl[index] = objs.convert_to_ail_object(item)

    self['__value__'] = pl


def array_str(self: objs.AILObject):
    return '[%s]' % (', '.join([repr(x) for x in self['__value__']]))


def _check_index(self, index):
    if isinstance(index, objs.AILObject) and \
            index['__class__'] == integer.INTEGER_TYPE:
        i = index['__value__']

    elif isinstance(index, int):
        i = index

    else:
        return AILRuntimeError('array subscript index must be integer.', 'TypeError')

    l = self['__value__']

    if i >= len(l):
        return AILRuntimeError('index out of range (len %s, index %s)' %
                               (len(l), str(i)), 'IndexError')
    return i


def array_getitem(self, index: int):
    i = _check_index(self, index)
    if isinstance(i, AILRuntimeError):
        return i

    l = self['__value__']

    return objs.convert_to_ail_object(l[i])


def array_setitem(self, index, value):
    i = _check_index(self, index)
    if isinstance(i, AILRuntimeError):
        return i

    l = self['__value__']

    l[i] = value


def array_len(self):
    return len(self['__value__'])


def array_append(self, value):
    arr = self['__value__']

    arr.append(value)


def array_pop(self):
    arr = self['__value__']
    
    if len(arr) == 0:
        return AILRuntimeError('pop from empty array', 'IndexError')
    return arr.pop()


def array_contains(self, value):
    arr = self['__value__']
    val = objs.unpack_ailobj(value)

    for x in arr:
        x = objs.unpack_ailobj(x)
        if x == val:
            return True
    return False


def array_count(self, value):
    arr = self['__value__']
    arr = [objs.unpack_ailobj(x) for x in arr]

    return arr.count(objs.unpack_ailobj(value))


def array_insert(self, index, value):
    arr = self['__value__']
    index = objs.unpack_ailobj(index)

    if not isinstance(index, int):
        return AILRuntimeError(
                'array.insert(x) required an integer', 'TypeError')

    arr.insert(index, value)


def array_remove(self, value):
    arr = self['__value__']
    arr = [objs.unpack_ailobj(x) for x in arr]
    
    try:
        return arr.remove(objs.unpack_ailobj(value))
    except ValueError:
        return AILRuntimeError('array.remove(x): x not in array', 'ValueError')


def array_sort(self):
    self['__value__'].sort()


def array_index(self, value):
    arr = self['__value__']
    arr = [objs.unpack_ailobj(x) for x in arr]
    
    try:
        return arr.index(objs.unpack_ailobj(value))
    except ValueError:
        return -1


def array_extend(self, x):
    arr = self['__value__']
    x = objs.unpack_ailobj(x)

    if not isinstance(x, list):
        return AILRuntimeError('array.extend(x): x must a array')


def array_clear(self):
    self['__value__'].clear()


def array_reverse(self):
    self['__value__'].reverse()


def array_copy(self):
    return self['__value__'].copy()


ARRAY_TYPE = objs.AILObjectType('<AIL array type>', types.I_ARRAY_TYPE,
                                methods={
                                    'append': array_append,
                                    'pop': array_pop,
                                    'contains': array_contains,
                                    'count': array_count,
                                    'insert': array_insert,
                                    'remove': array_remove,
                                    'sort': array_sort,
                                    'index': array_index,
                                    'extend': array_extend,
                                    'clear': array_clear,
                                    'reverse': array_reverse,
                                    'copy': array_copy,
                                },
                                __init__=array_init,
                                __getitem__=array_getitem,
                                __setitem__=array_setitem,
                                __str__=array_str,
                                __repr__=array_str,
                                __len__=array_len,
                                )


def convert_to_array(iterable: Iterable):
    if isinstance(iterable, IterableType):
        return objs.ObjectCreater.new_object(ARRAY_TYPE, list(iterable))
    return None
