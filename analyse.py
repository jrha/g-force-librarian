#!/usr/bin/python2
# encoding: utf8

from struct import Struct
from collections import deque, namedtuple
from string import printable
from textwrap import wrap
import mido

TC_MANUFACTURER_ID = (0x00,0x20,0x1f)

TC_MODELS = {
    0x10 : 'Header',
    0x11 : 'G-Force',
    0x40 : 'FireworX',
    0x42 : 'M3000',
    0x44 : 'M-One',
    0x45 : 'D-Two',
    0x47 : 'Triple C',
    0x63 : 'Nova System',
}


def unpack_bytes(msb, lsb):
    if msb < 16:
        if lsb < 16:
            result = (msb << 4) + lsb
            return result
        else:
            raise ValueError('Invalid nibble in LSB')
    else:
        raise ValueError('Invalid nibble in MSB')

    raise RuntimeError('Unpacking failed for an unknown reason')


def filterchar(c):
    if c > 31 and c < 127:
        c = chr(c)
        if c in printable:
            return(c)
    return('·')

# Preset Structure
#   total 614 bytes
#
#   number - 1 byte (value + 224)
#   name - 20 chars
#   data - 593 bytes
StructPreset = Struct('<' # Little Endian
    + 'B' # Preset Number
    + '20s' # Preset Name
    + 'B'*593 # Unknown Data
)
TuplePreset = namedtuple("Preset", "number name data")

messages = mido.read_syx_file('boop2.syx')

presets = []

for message in messages:
    chunk = deque(message.data)
    print "ManuID: %02x-%02x-%02x" % (chunk.popleft() ,chunk.popleft(), chunk.popleft())
    print "Device: %02x" % chunk.popleft()
    model_id = chunk.popleft()
    print "Model: %02x (%s)" % (model_id, TC_MODELS[model_id])
    print "Chunk Number: %02x" % chunk.popleft()

    #print ("%02x "*len(chunk)) % tuple(chunk)

    block = []
    text = ''
    while len(chunk) > 1:
        a = chunk.popleft()
        b = chunk.popleft()
        #print "a %s" % format(a, '08b')
        #print "b %s" % format(b, '08b')
        c = unpack_bytes(a, b)
        #print "c %s" % format(c, '08b')
        #print "%5d 0x%04x %s" % (c, c, format(c, '14b'))
        block.append(" %04x" % c)
        presets.append(c)
        text += filterchar(c)
        #block.append(" %s" % chr(min(255,c)))

        if len(block) == 16:
            print 'Block: ' + ' '.join(block)
            block = []

    print 'Strings: ' + text
    #print "Checksum: %04x" % chunk.popleft()

    #data = chunk
    #for value in data:
    #    print unpack_bytes(value)
    print

print 'Size of presets area: %d' % len(presets)

print
print ' '.join(['%04x' % p for p in presets[:105]])

preset = []
text = []
for p in presets[104:]: # Skip header
    t = filterchar(p)
    if t != '·':
        preset.append(('___%s' % t))
    else:
        preset.append("%04x" % p)
    if len(preset) == 614:
        print 'Preset:'
        print '\n'.join(wrap(' '.join(preset).replace('0000', '....'), 4*16+15))
        #print
        preset = []

#print ' '.join(['%04x' % p for p in presets])

# for chunk in chunks:
#     #print chunk
#     data = chunk[4:-1]
#     i = 0
#     while len(data) > 0:
#         a = data.pop(0)
#         b = data.pop(0)
#         c = (a<<4) + b
#         stdout.write("%02d : " % i)
#         if c >= 32 and c < 127:
#             stdout.write(chr(c))
#         else:
#             stdout.write('Unprintable Data : %03d : %s' % (c, hex(c)))
#         stdout.write('\n')
#         i += 1
#     print
