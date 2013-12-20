# tracer
This is a small utility to embed in your python applications. It will help you trace what's happening.

You can specify what slot in a class you want to record the trace to, kill traces, etc.

## Example from `trace_me`
Assuming the following snippet:
```python
from tracer import trace, TraceUtils

@trace(record_all=True)
class foo:
    def __init__(self):
        pass

    def call_me(self):
        print "I'm being called"

@trace(slots=('call_too',))
class bar:
    def __init__(self):
        pass

    def call_too(self):
        print "call_too"
        self.wont_trace()

    def wont_trace(self):
        print "Don't trace me..."

if __name__ == '__main__':
    o = foo()
    m = bar()
    i = 0
    while i < 10:
        o.call_me()
        m.call_too()
        i += 1
    TraceUtils.print_trace()
```

You'll get the following trace:
```
  <<>> foo::call_me(1) (0.074104)
  <<>> bar::call_too(3) (0.074142)
  <<>> foo::call_me(5) (0.074158)
  <<>> bar::call_too(7) (0.074169)
  <<>> foo::call_me(9) (0.074182)
  <<>> bar::call_too(11) (0.074193)
  <<>> foo::call_me(13) (0.074206)
  <<>> bar::call_too(15) (0.074216)
  <<>> foo::call_me(17) (0.074228)
  <<>> bar::call_too(19) (0.074239)
  <<>> foo::call_me(21) (0.074252)
  <<>> bar::call_too(23) (0.074262)
  <<>> foo::call_me(25) (0.074274)
  <<>> bar::call_too(27) (0.074285)
  <<>> foo::call_me(29) (0.074298)
  <<>> bar::call_too(31) (0.074308)
  <<>> foo::call_me(33) (0.074320)
  <<>> bar::call_too(35) (0.074330)
  <<>> foo::call_me(37) (0.074344)
  <<>> bar::call_too(39) (0.074354)
```
