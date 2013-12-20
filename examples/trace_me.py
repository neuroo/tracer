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

