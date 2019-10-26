'''
Created on Jul 23, 2017

@author: User
'''

from struct import *


#file_path = r'C:\Partition\Bren\Projects\3D\Photogrametry\WoodBowl\bowlMesh.ply'
'''
verts 37748
faces 75445
#print 37748*6
#226488
'''

file_path = r'C:\Partition\Bren\Projects\3D\Photogrametry\WoodBowl\bowl.0.ply'
'''
verts 330447
'''

#file_path = r'C:\Partition\Bren\Projects\3D\Photogrametry\RichmondPark\RichmondParl_Tree3\Tree_003_001.1.ply'


def test():
    with open(file_path, 'rb') as f:
        parse = True
        header = ''
        
        while parse:
            byte = f.read(1)
            header += byte
            if header.endswith('end_header\n'):
                parse = False
        
        print header
        data = f.read()
        print len(data)
        count = 330447
        uchar_byte_size = 1
        float_byte_size = 4
        
        pos_byte_count = 3*4*count
        normal_byte_count = 3*4*count
        color_byte_count = 3*count
        psz_byte_count = 4*count
        
        calc_count = pos_byte_count+normal_byte_count+color_byte_count+psz_byte_count
        print calc_count
        
        fmt = '<{}f'.format(count) # < means little endian
        unpacked_data = unpack(fmt, data[:count*4])
        #print unpacked_data
        print len(unpacked_data)
        



def testA():
    with open(file_path, 'r') as f:
        #lines = f.readlines() # this method keeps \n useful or no?
        ''' somethin not quite right here '''
        lines = f.read().splitlines()
        print len(lines)
    
    print len(lines)
    data = lines[14:]
    print len(data)
    
    # print pack('<3f', 4.2, 2.1, 5.1)
    
    print lines[13]
    
    pos = lines[14][:-1]
    float_byte_size = 4
    repeat_count = len(pos)/float_byte_size
    fmt = '<{}f'.format(repeat_count) # < means little endian
    unpacked_data = unpack(fmt, pos)
    print unpacked_data
    print len(unpacked_data)
    
    normals = lines[15]
    float_byte_size = 4
    repeat_count = len(normals)/float_byte_size
    fmt = '<{}f'.format(repeat_count) # < means little endian
    unpacked_data = unpack(fmt, normals)
    print unpacked_data
    print len(unpacked_data)
    
    
    colors = lines[16]
    uchar_byte_size = 1
    repeat_count = len(colors)/uchar_byte_size
    fmt = '<{}B'.format(repeat_count) # < means little endian
    unpacked_data = unpack(fmt, colors)
    print unpacked_data
    print len(unpacked_data)
    
    psz = lines[17]
    float_byte_size = 4
    repeat_count = len(psz)/float_byte_size
    fmt = '<{}f'.format(repeat_count) # < means little endian
    unpacked_data = unpack(fmt, psz)
    print unpacked_data
    print len(unpacked_data)
    
    
def testB():
    
    a = [float(i)/16.0 for i in range(3)]
    b = [i*11 for i in range(3)]
    c = a+b
    c *= 10
    print c
    #fmt = '<{}f'.format(count) # < means little endian
    fmt = (('f'*3)+('i'*3))*10
    fmt = '<'+fmt
    print fmt
    packed_data = pack(fmt, *c)
    print packed_data
    #fmt = '<60f'
    unpacked_data = unpack(fmt, packed_data)
    print unpacked_data
    print len(unpacked_data)

testB()
    
