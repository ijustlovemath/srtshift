import math
import sys
def main():
    filename = sys.argv[1]

    offset = sys.argv[2]

    units = 'sec'
    if offset.endswith('m'):
        units = 'min'

    offset = float(offset[:-1])
    if units == 'min':
        offset = offset * 60.0

    with open(filename, 'r') as f:
        lines = f.readlines()

    offset = Timestamp(offset)

    emit = False
    emit_buffer = []

    for line in lines:
        try:
            int(line)
            # we're in a new block of text, emit any cached blocks
            # clear the buffer for this block, set emit flag to false until we check everything
            flush(emit_buffer, emit) # is emit even a word? i've been coding too long
            emit_buffer = []
            emit = False
                
        except ValueError:
            pass

        if '-->' not in line:
            emit_buffer.append(line)
            continue
        try:
            start, end = line.split(' --> ')
            start = Timestamp(start) + offset
            end = Timestamp(end) + offset
            emit_buffer.append(f"{start} --> {end}")
            emit = True
        except AssertionError:
            # these timestamps are going negative, dont print them
            pass
        #start = start + 

    if emit_buffer and emit:
        for message in emit_buffer:
            print(message)

def flush(emit_buffer, emit):
    if emit_buffer and emit:
        for message in emit_buffer:
            print(message)
    if emit_buffer and not emit:
        print(f"[WARNING] Quashing messages '{emit_buffer}' due to incompatible/negative timestamp", file=sys.stderr)
    

class Timestamp:
    def __init__(self, *args):
        arg = args[0]
        if len(args) == 4:
            self.hours = args[0]
            self.minutes = args[1]
            self.secs = args[2]
            self.ms = args[3]
            return
        if isinstance(arg, str):
            self.from_string(arg)
        elif isinstance(arg, float):
            self.from_secs(arg)
        elif isinstance(arg, int):
            self.from_secs(arg * 1.0)
        else:
            raise TypeError("unexpected type to Timestamp constructor")
    def from_string(self, timestring):
        hours, minutes, secms = timestring.split(':')
        secs, ms = secms.split(',')
        self.hours = int(hours)
        self.minutes = int(minutes)
        self.secs = int(secs)
        self.ms = int(ms)

    def from_secs(self, secs):
        sign = 1
        if secs < 0:
            sign = -1
            secs = -secs

        hours = math.floor(secs / 3600.0)
        self.hours = int(sign * hours)
        secs = secs - hours * 3600.0
        
        minutes = math.floor(secs / 60.0)
        self.minutes = int(sign * minutes)
        secs = secs - minutes * 60.0

        frac, secs = math.modf(secs)
        self.ms = int(sign * math.floor(frac *1000))
        self.secs = int(sign * secs)
        return self

    def __add__(self, other):
        hours = self.hours
        minutes = self.minutes
        secs = self.secs
        ms = self.ms + other.ms
        if ms > 1000:
            secs = secs + 1
            ms = ms - 1000
        elif ms < 0:
            secs = secs - 1
            ms = ms + 1000

        secs = secs + other.secs
        if secs > 60:
            minutes = minutes + 1
            secs = secs - 60
        elif secs < 0:
            minutes = minutes - 1
            secs = secs + 60

        minutes = minutes + other.minutes
        if minutes > 60:
            hours = hours + 1
            minutes = minutes - 60
        elif minutes < 0:
            hours = hours - 1
            minutes = minutes + 60

        self.hours = self.hours + other.hours

        tmp = Timestamp(hours, minutes, secs, ms)
        tmp.check()
        return tmp

    def check(self):
        assert 0 <= self.ms < 1000, "ms inconsistent"
        assert 0 <= self.secs < 60, "secs inconsistent"
        assert 0 <= self.minutes < 60, "minutes inconsistent"
        assert self.hours >= 0, "hours inconsistent"

    def __repr__(self):
        return f"{self.hours:02d}:{self.minutes:02d}:{self.secs:02d},{self.ms:03d}"
    def debug(self):
        return f"{self.hours} hours, {self.minutes} minutes, {self.secs} seconds, {self.ms} milliseconds"



def test():
    t1 = Timestamp(1342445.0)
    t1.check()
    t2 = Timestamp(-600.475)
    print(t1)
    print(t2)
    print(t1+t2)
    t3 = t1 + t2
    print(t3.hours)
    print(t3)
    print(t3)

test()
main()
