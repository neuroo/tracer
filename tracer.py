
"""
    Tracer
    by Romain Gaucher <@rgaucher> - http://rgaucher.info

    Copyright (c) 2013 Romain Gaucher <r@rgaucher.info>

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
import inspect
import sys
import traceback
import types
import functools
import time

TRACER_MODE = True

class VirtualModule(object):
    def __init__(self, name):
        sys.modules[name] = self

    def __getattr__(self, name):
        return globals()[name]


class TraceInspector:
    INST = None

    ENTER = 0
    EXIT = 1

    def __init__(self):
        self.counter = 0
        self.level = 0
        self.trace, self.prev = [], []

    def __new__(self):
        if TraceInspector.INST is None:
            return TraceInspector.__init__()
        return self

    def record(self, class_name, func, args, kwargs, _type):
        self.counter += 1
        self.trace.append((self.counter, self.level, \
                           _type, class_name, func.__name__, time.clock()))

    def enter(self, class_name, func, args, kwargs):
        self.level += 1
        self.record(class_name, func, args, kwargs, TraceInspector.ENTER)

    def exit(self, class_name, func, args, kwargs):
        self.record(class_name, func, args, kwargs, TraceInspector.EXIT)
        self.level -= 1

    # Using the first 2 sub elements of the trace to know if there
    # might be a common parent
    def consolidate_trace(self):
        if not self.prev: return
        pos = len(self.prev) - len(self.trace)
        if pos < 0:
            return
        pivot = self.prev[pos]
        if self.trace[0] == pivot:
            self.trace = self.prev[pos:] + self.trace

    def get_trace(self):
        return self.trace

    def reset(self):
        self.consolidate_trace()
        self.counter = 0
        self.level = 0
        self.prev_trace = list(self.trace)
        self.trace = []

    def print_current_trace(self):
        prev_func = None
        for cnt, level, _type, cls, func, t in self.trace:
            rts = ""
            if prev_func and prev_func == func:
                rts = "<<>>"
            else:
                rts = ">>" if _type == TraceInspector.ENTER else "<<"

            indent = "  " * level
            print "%s%s %s::%s(%d) (%f)" % (indent, rts, cls, func, cnt, t)

    def __repr__(self):
        buffer, skip_next = '', False
        length = len(self.trace)
        for i in range(length):
            if skip_next:
                skip_next = False
                continue
            cnt, level, _type, cls, func, t = self.trace[i]
            rts = ''
            if i < length - 1 and func == self.trace[i + 1][4]:
                skip_next = True
                rts = '<<>>'
            else:
                rts = ">>" if _type == TraceInspector.ENTER else "<<"
            indent = "  " * level
            buffer += "%s%s %s::%s(%d) (%f)\n" % (indent, rts, cls, func, cnt, t)
        return buffer


# Getting frame infos requires this
VirtualModule("__main__")

CLASS_TYPES_CACHE = {
    'types' : {},
    'killpaths': {}
}

TRACE_INSPECTOR = TraceInspector()

BLACKLIST_FUNC = ('__init__',)

# This is to make sure to restart
DEFAULT_KILLPATH = ('main', '__main__')

class MethodType:
    METHOD = 0
    CLASSMETHOD = 1
    STATICMETHOD = 2
    UNKNOWN = 3


def get_class_fields(clazz, slots=None, record_all=True):
    global CLASS_TYPES_CACHE
    types = CLASS_TYPES_CACHE['types']
    class_name = clazz.__name__
    if class_name not in types:
        types[class_name] = {}

        for field_name in dir(clazz):
            meth = getattr(clazz, field_name, None)
            if not meth or not callable(meth):
                continue
            if field_name.startswith('_') or field_name in BLACKLIST_FUNC:
                continue

            instr_type = MethodType.METHOD if 'function ' not in repr(meth) else MethodType.STATICMETHOD

            types[class_name][field_name] = instr_type

    if record_all or not slots:
        return types[class_name]
    return set([f for f in types[class_name] if f in slots])


class TracMethod(object):
    def __init__(self, func, class_name, is_static=False, is_kill_path=False):
        self.func = func
        self.class_name = class_name
        self.is_static = is_static
        self.is_kill_path = is_kill_path

    def __get__(self, obj, cls=None):
        def wrapper(*args, **kwargs):
            TRACE_INSPECTOR.enter(self.class_name, self.func, args, kwargs)

            if self.is_static:
                ret = self.func(*args, **kwargs)
            else:
                ret = self.func(obj, *args, **kwargs)

            TRACE_INSPECTOR.exit(self.class_name, self.func, args, kwargs)

            if self.is_kill_path or self.func.__name__ in DEFAULT_KILLPATH:
                TRACE_INSPECTOR.reset()

            return ret
        return wrapper


def trace(slots=None, record_all=False, killpath=None, initpath=None):
    # Inspect the fields of the class to
    def trace_class(clazz):
        if not TRACER_MODE:
            return clazz

        class_name = clazz.__name__

        to_wrap_fields = get_class_fields(clazz, slots, record_all)
        if not to_wrap_fields:
            # Nothing to wrap...
            return clazz

        for field_name in to_wrap_fields:
            meth_type = CLASS_TYPES_CACHE['types'][class_name][field_name]
            is_kill_path = killpath is not None and field_name in killpath
            is_static =  meth_type != MethodType.METHOD
            meth = getattr(clazz, field_name, None)
            if meth is None:
                continue
            setattr(clazz, field_name, \
                    TracMethod(meth, class_name, is_static, is_kill_path))

        return clazz

    return trace_class



class TraceUtils(object):
    def __init__(self):
        pass

    @staticmethod
    def get_trace():
        return TRACE_INSPECTOR.get_trace()

    @staticmethod
    def print_trace():
        print TRACE_INSPECTOR

    @staticmethod
    def get_trace_string():
        return repr(TRACE_INSPECTOR)
