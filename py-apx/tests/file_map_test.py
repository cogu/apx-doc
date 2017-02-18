import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import apx
import unittest
import apx

class TestFileMap(unittest.TestCase):
 
   def setUp(self):
      pass
 
   def test_assignFileAddress(self):
      file_map = apx.FileMap()
      f1 = apx.ApxFile('test.out',6840)
      file_map.assignFileAddress(f1,0,65536,1024)
      file_map.insert(f1)
      f2 = apx.ApxFile('test.in',64)
      file_map.assignFileAddress(f2,0,65536,1024)
      file_map.insert(f2)
      f3 = apx.ApxFile('test.txt',64)
      file_map.assignFileAddress(f3,65536,131072,4096)
      file_map.insert(f3)
      f4 = apx.ApxFile('test.bin',100)
      file_map.assignFileAddress(f4,0,65536,1024)
      file_map.insert(f4)
      f5 = apx.ApxFile('test2.bin',8000)
      file_map.assignFileAddress(f5,65536,131072,4096)
      file_map.insert(f5)
      f6 = apx.ApxFile('test3.bin',400)
      file_map.assignFileAddress(f6,65536,131072,4096)
      file_map.insert(f6)
      self.assertEqual(len(file_map),6)
      self.assertEqual(file_map[0], f1)
      self.assertEqual(file_map[1], f2)
      self.assertEqual(file_map[2], f4)
      self.assertEqual(file_map[3], f3)
      self.assertEqual(file_map[4], f5)
      self.assertEqual(file_map[5], f6)
      self.assertEqual(file_map[0].address,0)
      self.assertEqual(file_map[1].address,1024*7)
      self.assertEqual(file_map[2].address,1024*8)
      self.assertEqual(file_map[3].address,65536)
      self.assertEqual(file_map[4].address,65536+4096)
      self.assertEqual(file_map[5].address,65536+4096*3)

   def test_assignFileAddressDefault(self):
      file_map = apx.FileMap()
      f1 = apx.ApxFile('test1.in',6840)
      file_map._assignFileAddressDefault(f1)
      file_map.insert(f1)
      f2 = apx.ApxFile('test1.out',64)
      file_map._assignFileAddressDefault(f2)
      file_map.insert(f2)
      f3 = apx.ApxFile('test1.apx',64)
      file_map._assignFileAddressDefault(f3)
      file_map.insert(f3)
      f4 = apx.ApxFile('test2.apx',100)
      file_map._assignFileAddressDefault(f4)
      file_map.insert(f4)
      f5 = apx.ApxFile('test2.out',8000)
      file_map._assignFileAddressDefault(f5)
      file_map.insert(f5)
      f6 = apx.ApxFile('test2.in',400)
      file_map._assignFileAddressDefault(f6)
      file_map.insert(f6)
      f7 = apx.ApxFile('test2.bin',6200)
      file_map._assignFileAddressDefault(f7)
      file_map.insert(f7)
      f8 = apx.ApxFile('test2.png',1234)
      file_map._assignFileAddressDefault(f8)
      file_map.insert(f8)
      self.assertEqual(len(file_map),8)
      self.assertEqual(file_map[0], f1) #port data
      self.assertEqual(file_map[1], f2) #port data
      self.assertEqual(file_map[2], f5) #port data
      self.assertEqual(file_map[3], f6) #port data
      self.assertEqual(file_map[4], f3) #apx data
      self.assertEqual(file_map[5], f4) #apx data
      self.assertEqual(file_map[6], f7) #user data
      self.assertEqual(file_map[7], f8) #user data
      self.assertEqual(file_map[0].address,0)
      self.assertEqual(file_map[1].address,1024*7)
      self.assertEqual(file_map[2].address,1024*8)
      self.assertEqual(file_map[3].address,1024*16)
      self.assertEqual(file_map[4].address,apx.DEFINITION_START)
      self.assertEqual(file_map[5].address,apx.DEFINITION_START+apx.DEFINITION_BOUNDARY)
      self.assertEqual(file_map[6].address,apx.USER_DATA_START)
      self.assertEqual(file_map[7].address,apx.USER_DATA_START+apx.USER_DATA_BOUNDARY)

   def test_insert(self):
      #this is identical to test_assignFileAddressDefault except that we removed the explicit call to filemap._assignFileAddressDefault
      file_map = apx.FileMap()
      f1 = apx.ApxFile('test1.in',6840)
      file_map.insert(f1)
      f2 = apx.ApxFile('test1.out',64)
      file_map.insert(f2)
      f3 = apx.ApxFile('test1.apx',64)
      file_map.insert(f3)
      f4 = apx.ApxFile('test2.apx',100)
      file_map.insert(f4)
      f5 = apx.ApxFile('test2.out',8000)
      file_map.insert(f5)
      f6 = apx.ApxFile('test2.in',400)
      file_map.insert(f6)
      f7 = apx.ApxFile('test2.bin',6200)
      file_map.insert(f7)
      f8 = apx.ApxFile('test2.png',1234)
      file_map.insert(f8)
      self.assertEqual(len(file_map),8)
      self.assertEqual(file_map[0], f1) #port data
      self.assertEqual(file_map[1], f2) #port data
      self.assertEqual(file_map[2], f5) #port data
      self.assertEqual(file_map[3], f6) #port data
      self.assertEqual(file_map[4], f3) #apx data
      self.assertEqual(file_map[5], f4) #apx data
      self.assertEqual(file_map[6], f7) #user data
      self.assertEqual(file_map[7], f8) #user data
      self.assertEqual(file_map[0].address,0)
      self.assertEqual(file_map[1].address,1024*7)
      self.assertEqual(file_map[2].address,1024*8)
      self.assertEqual(file_map[3].address,1024*16)
      self.assertEqual(file_map[4].address,apx.DEFINITION_START)
      self.assertEqual(file_map[5].address,apx.DEFINITION_START+apx.DEFINITION_BOUNDARY)
      self.assertEqual(file_map[6].address,apx.USER_DATA_START)
      self.assertEqual(file_map[7].address,apx.USER_DATA_START+apx.USER_DATA_BOUNDARY)



if __name__ == '__main__':
    unittest.main()   

