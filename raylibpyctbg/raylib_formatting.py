
# region HEADER

TPL_HEADER_IMPORTS = '''
import sys
import re
import os
import platform
import ctypes
from enum import IntEnum
from typing import Optional as Opt, Any, Sequence as Seq, Union
from ctypes import (
    CDLL, wintypes,
    c_bool, c_char, c_byte, c_short, c_long, c_longlong, c_ubyte, c_ushort, c_ulong, c_ulonglong, c_float, c_double, c_char_p, c_void_p,
    Structure, POINTER, CFUNCTYPE, byref, cast
) 


__all__ = [
    '{lib_name}',
    'Bool',
    'BoolPtr',
    'Byte',
    'BytePtr',
    'Char',
    'CharPtr',
    'Short',
    'ShortPtr',
    'Int',
    'IntPtr',
    'Long',
    'LongPtr',
    'UByte',
    'UBytePtr',
    'UShort',
    'UShortPtr',
    'UInt',
    'UIntPtr',
    'ULong',
    'ULongPtr',
    'Float',
    'FloatPtr',
    'Double',
    'DoublePtr',
    'VoidPtr',
    'VoidPtrPtr',
{exports}
]

# region LIBRARY LOADING

# region CDLLEX

if sys.platform == 'win32':
    DONT_RESOLVE_DLL_REFERENCES = 0x00000001
    LOAD_LIBRARY_AS_DATAFILE = 0x00000002
    LOAD_WITH_ALTERED_SEARCH_PATH = 0x00000008
    LOAD_IGNORE_CODE_AUTHZ_LEVEL = 0x00000010  # NT 6.1
    LOAD_LIBRARY_AS_IMAGE_RESOURCE = 0x00000020  # NT 6.0
    LOAD_LIBRARY_AS_DATAFILE_EXCLUSIVE = 0x00000040  # NT 6.0

    # These cannot be combined with LOAD_WITH_ALTERED_SEARCH_PATH.
    # Install update KB2533623 for NT 6.0 & 6.1.
    LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR = 0x00000100
    LOAD_LIBRARY_SEARCH_APPLICATION_DIR = 0x00000200
    LOAD_LIBRARY_SEARCH_USER_DIRS = 0x00000400
    LOAD_LIBRARY_SEARCH_SYSTEM32 = 0x00000800
    LOAD_LIBRARY_SEARCH_DEFAULT_DIRS = 0x00001000

    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)


    def check_bool(result, func, args):
        if not result:
            raise ctypes.WinError(ctypes.get_last_error())
        return args


    kernel32.LoadLibraryExW.errcheck = check_bool
    kernel32.LoadLibraryExW.restype = wintypes.HMODULE
    kernel32.LoadLibraryExW.argtypes = (wintypes.LPCWSTR,
                                        wintypes.HANDLE,
                                        wintypes.DWORD)


    class CDLLEx(ctypes.CDLL):
        def __init__(self, name, mode=0, handle=None,
                    use_errno=True, use_last_error=False):
            if handle is None:
                handle = kernel32.LoadLibraryExW(name, None, mode)
            super(CDLLEx, self).__init__(name, mode, handle,
                                        use_errno, use_last_error)


    class WinDLLEx(ctypes.WinDLL):
        def __init__(self, name, mode=0, handle=None,
                    use_errno=False, use_last_error=True):
            if handle is None:
                handle = kernel32.LoadLibraryExW(name, None, mode)
            super(WinDLLEx, self).__init__(name, mode, handle,
                                        use_errno, use_last_error)


# endregion (cdllex)


_lib_fname = {{
    'win32': '{win32_lib_filename}',
    'linux': '{linux_lib_filename}',
    'darwin': '{darwin_lib_filename}'
}}

_lib_platform = sys.platform

if _lib_platform == 'win32':
    _bitness = platform.architecture()[0]
else:
    _bitness = '64bit' if sys.maxsize > 2 ** 32 else '32bit'

_lib_fname_abspath = os.path.join({lib_basedir}, _bitness, _lib_fname[_lib_platform])
_lib_fname_abspath = os.path.normcase(os.path.normpath(_lib_fname_abspath))

print(
    """Library loading info:
    platform: {{}}
    bitness: {{}}
    absolute path: {{}}
    exists: {{}}
    is file: {{}}
    """.format(
        _lib_platform,
        _bitness,
        _lib_fname_abspath,
        'yes' if os.path.exists(_lib_fname_abspath) else 'no',
        'yes' if os.path.isfile(_lib_fname_abspath) else 'no'
    )
)

{lib_name} = None
if _lib_platform == 'win32':

    try:
        {lib_name} = CDLLEx(_lib_fname_abspath, LOAD_WITH_ALTERED_SEARCH_PATH)
    except OSError:
        print("Unable to load {{}}.".format(_lib_fname[_lib_platform]))
        {lib_name} = None
else:
    {lib_name} = CDLL(_lib_fname_abspath)

if {lib_name} is None:
    print("Failed to load shared library.")
    exit()
else:
    print("Shared library loaded succesfully.", {lib_name})
'''

TPL_HEADER_UTILS = """


Bool = c_bool
BoolPtr = POINTER(c_bool)
Byte = c_byte
BytePtr = POINTER(c_byte)
Char = c_char
CharPtr = POINTER(c_char)
Short = c_short
ShortPtr = POINTER(c_short)
Int = c_long
IntPtr = POINTER(c_long)
Long = c_long
LongPtr = POINTER(c_long)
LongLong = c_longlong
LongLongPtr = POINTER(c_longlong)
UChar = c_ubyte
UCharPtr = POINTER(c_ubyte)
UByte = c_ubyte
UBytePtr = POINTER(c_ubyte)
UShort = c_ushort
UShortPtr = POINTER(c_ushort)
UInt = c_ulong
UIntPtr = POINTER(c_ulong)
ULong = c_ulong
ULongPtr = POINTER(c_ulong)
ULongLong = c_ulonglong
ULongLongPtr = POINTER(c_ulonglong)
Float = c_float
FloatPtr = POINTER(c_float)
Double = c_double
DoublePtr = POINTER(c_double)
VoidPtr = c_void_p
VoidPtrPtr = POINTER(c_void_p)
CharPtr = c_char_p
CharPtrPtr = POINTER(c_char_p)


# Vector component swizzling helppers
_VEC2_GET_SWZL = re.compile(r'[xy]{,4}')
_VEC3_GET_SWZL = re.compile(r'[xyz]{,4}')
_VEC4_GET_SWZL = re.compile(r'[xyzw]{,4}')
_RGBA_GET_SWZL = re.compile(r'[rgba]{4}')
_RECT_GET_SWZL = re.compile(r'(width|height|[xywh]{4})')

_VEC2_SET_SWZL = re.compile(r'[xy]{,2}')
_VEC3_SET_SWZL = re.compile(r'[xyz]{,3}')
_VEC4_SET_SWZL = re.compile(r'[xyzw]{,4}')
_RGBA_SET_SWZL = re.compile(r'[rgba]{1,4}')
_RECT_SET_SWZL = re.compile(r'(width|height|[xywh]{1,4})')

# region FUNCTIONS


def _clsname(obj):
    return obj.__class__.__name__


def is_number(obj):
    return isinstance(obj, (int, float))


def is_component(value):
    return isinstance(value, int) and 0 <= value <= 255


def _clamp_rgba(*args):
    return tuple(value & 255 for value in args)


def _str_in(value):
    return value.encode('utf-8', 'ignore') if isinstance(value, str) else value


def _str_in2(values):
    return _arr_in(CharPtr, tuple(_str_in(value) for value in values))


def _str_out(value):
    return value.decode('utf-8', 'ignore') if isinstance(value, bytes) else value


def _arr_in(typ, data):
    if isinstance(data, POINTER(typ)):
        return data
    return (typ * len(data))(*data)


def _arr2_in(typ, data):
    arr = typ * len(data[0])
    return (arr * len(data))(*data)


def _arr_out(data):
    return data.values


def _ptr_out(ptr, length=0):
    [ptr.contents] if length == 1 else ([] if not length else ptr[:length])

# region TYPE CAST FUNCS


def _float(value):
    return float(value)


def _int(value, ranged=None):
    if ranged:
        return max(ranged[0], min(int(value), ranged[1]))
    return int(value)


def _vec2(seq):
    if isinstance(seq, Vector2):
        return seq
    x, y = seq
    return Vector2(_float(x), _float(y))


def _vec3(seq):
    if isinstance(seq, Vector3):
        return seq
    x, y, z = seq
    return Vector3(float(x), float(y), float(z))


def _vec4(seq):
    if isinstance(seq, Vector4):
        return seq
    x, y, z, w = seq
    return Vector4(float(x), float(y), float(z), float(w))


def _rect(seq):
    if isinstance(seq, Rectangle):
        return seq
    x, y, w, h = seq
    return Rectangle(float(x), float(y), float(w), float(h))


def _color(seq):
    if isinstance(seq, Color):
        return seq
    r, g, b, q = seq
    rng = 0, 255
    return Color(_int(r, rng), _int(r, rng), _int(b, rng), _int(q, rng))

# endregion (type cast funcs)


def _wrap(api, argtypes, restype):
    api.argtypes = argtypes
    api.restype = restype
    return api

# endregion (functions)


# Struct not exposed in raylib.h
class rAudioBufferPtr(Structure):
    pass


# Struct not exposed in raylib.h
class rAudioProcessorPtr(Structure):
    pass


"""

# endregion (header)

# region DEFINES

TPL_DEFINE_CONST = '''
{name}{annotation} = {value}{type_hint}
'''

TPL_DEFINE_COLOR = '''# {description}
{name}{annotation} = {struct_name}({rgba}){type_hint}
'''

# endregion (defines)

# region STRUCTS

TPL_STRUCTURE = """
class {name}(Structure):
    '''{description}'''
{field_map}

    @classmethod
    def array_of(cls, {py_name}_sequence):
        '''Creates and returns an array of {name}s'''
        arr = cls * len({py_name}_sequence)
        return arr(*{py_name}_sequence)
{extra_classmethods}

    def __init__(self, {init_params}):{type_hint}
        '''Initializes this {name} struct'''
        super({name}, self).__init__(
            {init_fields}
        )
{dunder_methods}

    @property
    def byref(self):
        '''Gets a reference to this {name} instance'''
        return byref(self)
{extra_props}
{extra_methods}

# Pointer type to {name}s
{name}Ptr = POINTER({name})
{alias}

"""

TPL_STRUCTURE_FIELD_MAP = """    _fields_ = [
{fields}
    ]
"""

TPL_STRUCTURE_GETTER = '''
    {decorator}
    def {py_name}(self){annotation}:{type_hint}
        """{description}"""{before}
        {result}{a}{prefix}{c_name}({arg_list}){b}{after}
'''

TPL_STRUCTURE_METHOD = '''
    {decorator}def {py_name}({param_list}){annotation}:{type_hint}
        """{description}"""{before}
        {result}{a}{prefix}{c_name}({arg_list}){b}{after}
'''

TPL_VECTOR2_SWIZZLING = """
    def __len__(self):
        return 2

    def __getitem__(self, key):
        return (self.x, self.y).__getitem__(key)

    def __getattr__(self, attr):
        m = _VEC2_GET_SWZL.match(attr)
        if not m:
            raise AttributeError("Vector2 object does not have attribute '{}'.".format(attr))
        cls = {1: float, 2: Vector2, 3: Vector3, 4: Vector4}.get(len(attr))
        v = self.todict()
        return cls(*(v[ch] for ch in attr))

    def __setattr__(self, attr, value):
        m = _VEC2_SET_SWZL.match(attr)
        if not m:
            raise AttributeError("Vector2 object does not have attribute '{}'.".format(attr))
        if len(attr) == 1:
            super(Vector2, self).__setattr__(attr, float(value))
        else:
            for i, ch in enumerate(attr):
                super(Vector2, self).__setattr__(ch, float(value[i]))

    def todict(self):
        '''Returns a dict mapping this Vector2's components'''
        return {'x': self.x, 'y': self.y}

    def fromdict(self, d):
        '''Apply the mapping `d` to this Vector2's components'''
        self.x = float(d.get('x', self.x))
        self.y = float(d.get('y', self.y))

"""
TPL_VECTOR3_SWIZZLING = """
    def __len__(self):
        return 3

    def __getitem__(self, key):
        return (self.x, self.y, self.z).__getitem__(key)

    def __getattr__(self, attr):
        m = _VEC3_GET_SWZL.match(attr)
        if not m:
            raise AttributeError("Vector3 object does not have attribute '{}'.".format(attr))
        cls = {1: float, 2: Vector2, 3: Vector3, 4: Vector4}.get(len(attr))
        v = self.todict()
        return cls(*(v[ch] for ch in attr))

    def __setattr__(self, attr, value):
        m = _VEC3_SET_SWZL.match(attr)
        if not m:
            raise AttributeError("Vector3 object does not have attribute '{}'.".format(attr))
        if len(attr) == 1:
            super(Vector3, self).__setattr__(attr, float(value))
        else:
            for i, ch in enumerate(attr):
                super(Vector3, self).__setattr__(ch, float(value[i]))

    def todict(self):
        '''Returns a dict mapping this Vector3's components'''
        return {'x': self.x, 'y': self.y, 'z': self.z}

    def fromdict(self, d):
        '''Apply the mapping `d` to this Vector3's components'''
        self.x = float(d.get('x', self.x))
        self.y = float(d.get('y', self.y))
        self.z = float(d.get('z', self.z))
"""

TPL_VECTOR4_SWIZZLING = """
    def __len__(self):
        return 4

    def __getitem__(self, key):
        return (self.x, self.y. self.z, self.w).__getitem__(key)

    def __getattr__(self, attr):
        m = _VEC4_GET_SWZL.match(attr)
        if not m:
            raise AttributeError("Vector4 object does not have attribute '{}'.".format(attr))
        cls = {1: float, 2: Vector2, 3: Vector3, 4: Vector4}.get(len(attr))
        v = self.todict()
        return cls(*(v[ch] for ch in attr))

    def __setattr__(self, attr, value):
        m = _VEC4_SET_SWZL.match(attr)
        if not m:
            raise AttributeError("Vector4 object does not have attribute '{}'.".format(attr))
        if len(attr) == 1:
            super(Vector4, self).__setattr__(attr, float(value))
        else:
            for i, ch in enumerate(attr):
                super(Vector4, self).__setattr__(ch, float(value[i]))

    def todict(self):
        '''Returns a dict mapping this Vector4's components'''
        return {'x': self.x, 'y': self.y, 'z': self.z, 'w': self.w}

    def fromdict(self, d):
        '''Apply the mapping `d` to this Vector4's components'''
        self.x = float(d.get('x', self.x))
        self.y = float(d.get('y', self.y))
        self.z = float(d.get('z', self.z))
        self.w = float(d.get('w', self.w))

"""

TPL_RECTANGLE_SWIZZLING = """
    def __len__(self):
        return 4

    def __getitem__(self, key):
        return (self.x, self.y. self.width, self.height).__getitem__(key)

    def __getattr__(self, attr):
        m = _RECT_GET_SWZL.match(attr)
        if not m:
            raise AttributeError("Rectangle object does not have attribute '{}'.".format(attr))
        cls = {1: float, 4: Rectangle}.get(len(attr))
        v = self.todict()
        return cls(*(v[ch] for ch in attr))

    def __setattr__(self, attr, value):
        m = _RECT_SET_SWZL.match(attr)
        if not m:
            raise AttributeError("Rectangle object does not have attribute '{}'.".format(attr))
        if attr in ('width', 'height') or len(attr) == 1:
            super(Rectangle, self).__setattr__(attr, float(value))
        else:
            for i, ch in enumerate(attr):
                super(Rectangle, self).__setattr__(ch, float(value[i]))

    def todict(self):
        '''Returns a dict mapping this Rectangle's components'''
        return {'x': self.x, 'y': self.y, 'w': self.width, 'h': self.height}

    def fromdict(self, d):
        '''Apply the mapping `d` to this Rectangle's components'''
        self.x = float(d.get('x', self.x))
        self.y = float(d.get('y', self.y))
        self.width = float(d.get('w', self.width))
        self.height = float(d.get('h', self.height))

"""
TPL_COLOR_SWIZZLING = """
    def __len__(self):
        return 4

    def __getitem__(self, key):
        return (self.r, self.g, self.b, self.a).__getitem__(key)

    def __getattr__(self, attr):
        m = _RGBA_GET_SWZL.match(attr)
        if not m:
            raise AttributeError("Color object does not have attribute '{}'.".format(attr))
        cls = {1: int, 4: Color}.get(len(attr))
        v = self.todict()
        return cls(*(v[ch] for ch in attr))

    def __setattr__(self, attr, value):
        m = _RGBA_SET_SWZL.match(attr)
        if not m:
            raise AttributeError("Color object does not have attribute '{}'.".format(attr))
        if len(attr) == 1:
            super(Color, self).__setattr__(attr, int(value))
        else:
            for i, ch in enumerate(attr):
                super(Color, self).__setattr__(ch, int(value[i]))

    def todict(self):
        '''Returns a dict mapping this Color's components'''
        return {'r': self.r, 'g': self.g, 'b': self.b, 'a': self.a}

    def fromdict(self, d):
        '''Apply the mapping `d` to this Color's components'''
        self.r = int(d.get('r', self.r))
        self.g = int(d.get('g', self.g))
        self.b = int(d.get('b', self.b))
        self.a = int(d.get('a', self.a))

"""
# endregion (ALIASES)

TPL_DEFINE_ALIAS = '''# {description}
{name}{annotation} = {type}{type_hint}
{name}Ptr{annotation} = {type}Ptr{type_hint}
'''

# region (aliases)

# endregion (FUNCTIONS)

TPL_FUNCTION = '''

{decorator}def {py_name}({param_list}){annotation}:{type_hint}
    """{description}"""{before}
    {result}{a}{prefix}{c_name}({arg_list}){b}{after}
'''

TPL_FUNCTION_WRAPCALL = '''_{api_name} = _wrap({lib_name}.{api_name}, [{arg_types}], {res_type})\n'''
TPL_FUNCTION_TYPE = '''
# {description}
{name} = CFUNCTYPE({args})
'''

# region (functions)

# endregion (ENUMERATIONS)

TPL_ENUMERATION = '''class {name}(IntEnum):
    """{description}"""

{members}


{unbound_members}


'''

TPL_ENUMERATION_MEMBER = '''    {name} = {value}
    """{description}"""
'''

# region (enumerations)

# endregion ()