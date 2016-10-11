#!/usr/bin/python2
# encoding: utf8

from struct import Struct
from collections import deque, namedtuple
from string import printable
from textwrap import wrap
import mido

from tc_globals import *
from gforce_luts import *

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


def sysex_to_rawdata(messages):
    data_buffer = deque()
    for message in messages:
        if message.type == 'sysex':
            chunk = deque(message.data)
            manufacturer_id = (chunk.popleft() ,chunk.popleft(), chunk.popleft())
            print "Manufacturer ID: %02x-%02x-%02x" % manufacturer_id
            if manufacturer_id == TC_MANUFACTURER_ID:
                print "Manufacturer: TC Electronic"
                device_id = chunk.popleft()
                print "Device ID: %02x" % device_id

                model_id = chunk.popleft()
                if model_id in TC_MODELS_SUPPORTED:
                    model_name = TC_MODELS[model_id]
                    print "Model: %02x (%s)" % (model_id, model_name)

                    chunk_id = chunk.popleft()
                    print "Chunk Number: %d" % chunk_id

                    checksum = chunk.pop()
                    print "Checksum: %d" % checksum

                    print "Chunk Size: %d" % len(chunk)
                    data_buffer += chunk

                    print ("%02x "*len(chunk)) % tuple(chunk)
                else:
                    print "Skipping, header block or unsupported model"
                    #print ("%02x "*len(chunk)) % tuple(chunk)
            else:
                print "Skipping, unsupported manufacturer"
        else:
            print "Skipping, not a SysEx message"
        print
    return data_buffer


def rawdata_to_bytes(raw_data):
    byte_buffer = deque()
    while len(raw_data) > 1:
        a = raw_data.popleft()
        b = raw_data.popleft()
        #print "a %s" % format(a, '08b')
        #print "b %s" % format(b, '08b')
        byte_buffer.append(unpack_bytes(a, b))
        #print "c %s" % format(c, '08b')
        #print "%5d 0x%04x %s" % (c, c, format(c, '14b'))
    return byte_buffer


def extract_presets(preset_data):
    print 'Size of presets area: %d' % len(preset_data)

    header = []
    presets = []

    for i in range(104):
        header = preset_data.popleft()

    while len(preset_data):
        preset = ''
        for i in range(614):
            try:
                preset += chr(preset_data.popleft())
            except IndexError:
                print "Hit end of preset data while parsing presets"
        presets.append(preset)
    return(presets)


StructPreset = Struct('<' # Little Endian
    + 'x' # padding
    + 'B' # Preset Number
    + '20s' # Preset Name
    + 'B'*18 # States
    + 'B'*32 # Routing
    + 'B'*542 # unknown data
)


TuplePreset = namedtuple('Preset', [
    'p000_gate_enable',
    'p001',
    'p002_compressor_enable',
    'p003',
    'p004_filter_enable',
    'p005',
    'p006_pan_tremolo_enable',
    'p007',
    'p008_pitch_enable',
    'p009',
    'p010_delay_enable',
    'p011',
    'p012_drive_enable',
    'p013',
    'p014_chorus_enable',
    'p015',
    'p016_reverb_enable',
    'p017',

    'p018_route_0_0',
    'p019_route_0_1',
    'p020_route_0_2',
    'p021_route_0_3',

    'p022_route_1_0',
    'p023_route_1_1',
    'p024_route_1_2',
    'p025_route_1_3',

    'p026_route_2_0',
    'p027_route_2_1',
    'p028_route_2_2',
    'p029_route_2_3',

    'p030_route_3_0',
    'p031_route_3_1',
    'p032_route_3_2',
    'p033_route_3_3',

    'p034_route_4_0',
    'p035_route_4_1',
    'p036_route_4_2',
    'p037_route_4_3',

    'p038_route_5_0',
    'p039_route_5_1',
    'p040_route_5_2',
    'p041_route_5_3',

    'p042_route_6_0',
    'p043_route_6_1',
    'p044_route_6_2',
    'p045_route_6_3',

    'p046_route_7_0',
    'p047_route_7_1',
    'p048_route_7_2',
    'p049_route_7_3',
])


def parse_preset(preset):
    """
    Preset Structure (total size 614 bytes)
        padding     1 byte (null)
        number      1 byte (display value + 224)
        name        20 chars
        payload:
            states      18 bytes
            routing     32 bytes
            data        543 bytes
    """
    return StructPreset.unpack(preset)


def print_preset(preset):
    text = []
    for p in preset:
        t = filterchar(p)
        if t != '·':
            text.append(('___%s' % t))
        else:
            text.append("%04x" % p)
    print 'Preset:'
    print '\n'.join(wrap(' '.join(text).replace('0000', '....'), 4*16+15))

messages = mido.read_syx_file('dump.syx')

print 'Reading raw data from SysEx'
data = sysex_to_rawdata(messages)
print 'Extracting bytes from raw data'
data = rawdata_to_bytes(data)
print 'Extracting presets...'
data = extract_presets(data)
print 'Done'

for d in data:
    p = parse_preset(d)
    print p[1]
    for i in range(4):
        row = ''
        for v in p[20+i:21+33+i:4]:
            print v
            row += '[%-14s] ' % EFFECT_TYPES[v]
        print row
    print

    with open('/tmp/preset_%03d_%s.hex' % (p[0]-224, p[1].strip()), 'w') as f:
        f.write('\n'.join(["0x%02x" % i for i in p[2:]]))
        f.write('\n')
