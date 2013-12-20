from tracer import trace, TraceUtils

@trace(record_all=True)
class my_class(object):
    def __init__(self):
        pass

    def call_me(self):
        print "I'm being called"

if __name__ == '__main__':
    o = my_class()
    while i < 10:
        o.call_me()
        i += 1
    print TraceUtils.get_trace()

