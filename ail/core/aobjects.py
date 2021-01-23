import inspect

from types import FunctionType
from typing import Union

from . import error
from ..objects import types


INVISIBLE_ATTRS = (
    '__value__',
    '__class__',
    '__init__',
    '__add__',
    '__div__',
    '__muit__',
    '__sub__',
    '__div__',
    '__getattr__',
    '__setattr__',
    '__getitem__',
    '__setitem__',
    '__name__'
)


class AILConstant:
    __slots__ = ['const', 'type_']

    def __init__(self, const, type_: int):
        self.const = const
        self.type_ = type_


class NullType:
    def __str__(self):
        return 'null'

    __repr__ = __str__


# null = NullType()

class AILCodeObject:
    __slots__ = ('consts', 'varnames', 'bytecodes', 'firstlineno', 'lineno_list',
                 'argcount', 'name', 'lnotab', 'closure', 'is_main', 'filename',
                 '_closure_outer', 'global_names', 'nonlocal_names', 'var_arg')

    def __init__(self, consts: list, varnames: list,
                 bytecodes: list, firstlineno: int, filename: str,
                 argcount: int, name: str, lnotab: list, lineno_list: tuple,
                 closure: bool = False, is_main: bool = False,
                 global_names: list=None, nonlocal_names: list=None,):
        self.consts = consts
        self.varnames = varnames
        self.bytecodes = tuple(bytecodes)
        self.firstlineno = firstlineno
        self.argcount = argcount  # if function or -1
        self.name = name
        self.filename = filename
        self.lnotab = lnotab
        self.closure = closure
        self.is_main = is_main
        self.lineno_list = lineno_list
        self.global_names = global_names
        self.nonlocal_names = nonlocal_names

        self.var_arg: str = None
        self._closure_outer: list = list()  # empty if not closure

    def __str__(self):
        return '<AIL CodeObject \'%s\'>' % self.name

    __repr__ = __str__


class AILObject:
    """Base object, do noting..."""

    def __init__(self, **ps):
        self.__hash_target = object()  # hash
        self.properties = ps
        self.reference = 0

    def __getitem__(self, key: str):
        if key in self.properties:
            k = self.properties[key]
            return k
        return None

    def __setitem__(self, key: str, value):
        self.properties[key] = value

    def __getattr__(self, item: str):
        if item[:5] == 'aprop':
            return self.__getitem__(item[6:])
        return super().__getattribute__(item)

    def __setattr__(self, key: str, value):
        if key[:5] == 'aprop':
            self.__setitem__(key[6:])
        super().__setattr__(key, value)

    def __str__(self):
        try:
            return self['__str__'](self)
        except TypeError:
            return '<AIL %s object at %s>' % (
                    self['__class__'].name, hex(id(self)))

    def __eq__(self, o):
        try:
            b = self['__eq__'](self, o)
            if isinstance(b, error.AILRuntimeError):
                return False
            if isinstance(b, AILObject):
                v = b['__value__']
                if v is None:
                    return True  # 若无value， 默认返回 True
                return v
            return bool(b)

        except TypeError:
            return super().__eq__(o)

    def __repr__(self):
        try:
            return self['__repr__'](self)
        except TypeError:
            return self.__str__()

    def __hash__(self) -> int:
        return hash(self.__hash_target)


class AILObjectType:
    """Object Type"""

    def __init__(self, 
            tname: str, otype=None, methods: dict = None, **required):
        super().__init__()
        self.name = tname
        self.required = required
        self.otype = types.I_TYPE_TYPE if otype is None else otype
        self.methods = methods if methods is not None else dict()

    def __str__(self):
        return '<AIL Type \'%s\'>' % self.name

    __repr__ = __str__


class ObjectCreater:
    from ..objects import ailobject as __aobj
    from ..objects.function import \
        convert_to_func_wrapper as __to_wrapper

    __required_normal = {
        '__str__': __aobj.obj_func_str,
        '__init__': __aobj.obj_func_init,
        '__eq__': __aobj.obj_func_eq,
        '__getattr__': __aobj.obj_getattr,
        '__setattr__': __aobj.obj_setattr,
        '__equals__': __aobj.obj_equals
    }

    @staticmethod
    def new_object(obj_type: AILObjectType, *args) -> AILObject:
        """
        ATTENTION : 返回的对象的引用为0
        :return : obj_type 创建的对象，并将 *args 作为初始化参数
        """

        obj = AILObject()  # create an object
        obj.properties['__class__'] = obj_type

        for k, v in obj_type.required.items():
            obj.properties[k] = v

        if obj_type.methods is not None:
            for mn, mo in obj_type.methods.items():
                if not isinstance(mo, AILObject):
                    f = ObjectCreater.__to_wrapper(mo)

                    f.properties['__this__'] = obj  # bound self to __this__
                    obj.properties[mn] = f

        # check normal required
        t_req_keys = set(obj_type.required.keys())

        for name, default in ObjectCreater.__required_normal.items():
            if name in t_req_keys:
                continue
            obj.properties[name] = default

        # call init method
        init_mthd = obj.properties['__init__']
        r = init_mthd(obj, *args)

        if isinstance(r, error.AILRuntimeError):
            return r

        return obj


def check_object(obj):
    if isinstance(obj, error.AILRuntimeError):
        error.print_global_error(obj)


# cache
_STRING_TYPE = None
_INTEGER_TYPE =None
_FLOAT_TYPE = None
_COMPLEX_TYPE = None
_ARRAY_TYPE = None
_WRAPPER_TYPE = None
_PY_FUNCTION_TYPE = None
_null = None
_not_loaded = True


def convert_to_ail_object(pyobj: object) -> AILObject:
    global _not_loaded
    global _STRING_TYPE
    global _INTEGER_TYPE
    global _FLOAT_TYPE
    global _COMPLEX_TYPE
    global _ARRAY_TYPE
    global _WRAPPER_TYPE
    global _PY_FUNCTION_TYPE
    global _null

    if isinstance(pyobj, AILObject):
        return pyobj
    
    if _not_loaded:
        from ..objects.string import STRING_TYPE as _STRING_TYPE
        from ..objects.integer import INTEGER_TYPE as _INTEGER_TYPE
        from ..objects.float import FLOAT_TYPE as _FLOAT_TYPE
        from ..objects.complex import COMPLEX_TYPE as _COMPLEX_TYPE
        from ..objects.array import ARRAY_TYPE as _ARRAY_TYPE
        from ..objects.wrapper import WRAPPER_TYPE as _WRAPPER_TYPE
        from ..objects.function import PY_FUNCTION_TYPE as _PY_FUNCTION_TYPE
        from ..objects.null import null as _null
        _not_loaded = False

    if pyobj is None:
        return _null

    py_t = type(pyobj)
    ail_t = _WRAPPER_TYPE

    if py_t is int:
        ail_t = _INTEGER_TYPE
    elif py_t is float:
        ail_t  = _FLOAT_TYPE
    elif py_t is complex:
        ail_t = _COMPLEX_TYPE
    elif py_t is str:
        ail_t = _STRING_TYPE
    elif py_t is bool:
        from .abuiltins import true, false
        return true if pyobj else false
    elif py_t is list:
        ail_t = _ARRAY_TYPE
    elif py_t is FunctionType:
        ail_t = _PY_FUNCTION_TYPE

    return ObjectCreater.new_object(ail_t, pyobj)


def convert_to_ail_number(pynum: Union[int, float]) -> AILObject:
    from ..objects import integer
    from ..objects import float as afloat
    from ..objects import complex as acomplex

    if isinstance(pynum, int):
        return integer.get_integer(pynum)
    elif isinstance(pynum, float):
        return afloat._new_object(afloat.FLOAT_TYPE, pynum)
    elif isinstance(pynum, complex):
        return acomplex.to_complex(pynum)
    else:
        return pynum



def compare_type(o, *t):
    if isinstance(o, AILObject):
        if o['__class__'] in t:
            return True
    return False


def has_attr(aobj: AILObject, name: str):
    if isinstance(aobj, AILObject):
        return name in aobj.properties
    return False


def unpack_ailobj(ailobj: AILObject):
    if has_attr(ailobj, '__value__'):
        return ailobj['__value__']
    return ailobj


