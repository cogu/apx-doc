import apx
import remotefile
import bisect
from bisect import bisect_left, bisect_right

#constants
PORT_DATA_START     = 0x0
PORT_DATA_BOUNDARY  = 0x400 #1KB, this must be a power of 2
DEFINITION_START    = 0x4000000 #64MB, this must be a power of 2
DEFINITION_BOUNDARY = 0x100000 #1MB, this must be a power of 2
USER_DATA_START     = 0x20000000 #512MB, this must be a power of 2
USER_DATA_END       = 0x3FFFFC00 #Start of remote file cmd message area
USER_DATA_BOUNDARY  = 0x100000 #1MB, this must be a power of 2

@remotefile.FileMap.register
class FileMap:
   """
   concrete implementation of remotefile.FileMap
   
   It maps:
     * .in and .out files in the range 0..64MB (using 1KiB boundary).
     * .apx files in the range 64MB-512MB (using 1MiB boundary).
     
     
   This class uses a variant/subset of the SortedCollection recipe (https://code.activestate.com/recipes/577197-sortedcollection/) to implement a sorted list of files sorted by their address
   """
   
   def __init__(self):
      self._keys = []
      self._items = []
      
   def index(self, file):
        'Find the position of an item.  Raise ValueError if not found.'
        k = file.address
        i = bisect_left(self._keys, k)
        j = bisect_right(self._keys, k)
        return self._items[i:j].index(file) + i
   
   def insert(self, file):
      assert(isinstance(file, apx.ApxFile))
      #assign address to file
      if file.address is None:
         self._assignFileAddressDefault(file)
      assert(file.address is not None)
      k = file.address
      i = bisect_left(self._keys, k)
      self._keys.insert(i, k)
      self._items.insert(i, file)
   
   
   def remove(self, file):
      'Remove file from FileMap'
      assert(isinstance(file, apx.ApxFile))       
      i = self.index(file)
      del self._keys[i]
      del self._items[i]
   
   def findByAddress(self, address):
        'finds file based on address'
        i = bisect_left(self._keys, k)
        if i != len(self) and self._keys[i] == k:
            return self._items[i]
        raise ValueError('No item found with key equal to: %r' % (k,))
      
   def findByName(self, name):
      'finds file based on its file name'
      for file in self._items:
         if file.name == name:
            return file
   
   def _assignFileAddressDefault(self, file):
      """
      Default address assigner. It calls self.assignAddress with "correct" arguments based on the file name 
      
      - .in and .out files goes into the first 64MB area
      - .apx files goes into the area between 64MB and 512MB
      - user data goes into the area above 512MB (these are files that doesn't match the file suffix .in, .out or .apx)      
      """
      if file.name.endswith('.in') or file.name.endswith('.out'):
         self.assignFileAddress(file, PORT_DATA_START, DEFINITION_START, PORT_DATA_BOUNDARY)
      elif file.name.endswith('.apx'):
         self.assignFileAddress(file, DEFINITION_START, USER_DATA_START, DEFINITION_BOUNDARY)
      else:
         self.assignFileAddress(file, USER_DATA_START, USER_DATA_END, USER_DATA_BOUNDARY)
   
   def assignFileAddress(self, file, start_address, end_address, address_boundary):
      """
      sets the address attribute in file by searching the FileMap (self) for an empty slot in the address range(start_address,end_address)
      
      arguments start_address, end_address and address_boundary must all be a power of 2 (2,4,8,16,32,64,...)
      
      """
      
      #check that arguments are a power of 2
      if (start_address!=0) and ((start_address & (start_address-1)) != 0) :
         raise ValueError('start_address must be a power of 2')
      if (end_address<start_address) != 0 :
         raise ValueError('end_address must be larger than start_address')
      if (address_boundary & (address_boundary-1)) != 0 :
         raise ValueError('address_boundary must be a power of 2')
      
      if len(self._keys)==0:
         placement_address=start_address
      else:
         i = bisect_left(self._keys, end_address)
         if i>=len(self._keys):            
            i=len(self._keys)-1
         #start from item i (first item at end_address) and move backward until you find a free slot
         while i>=0:
            other=self._items[i]
            if other.address<start_address:
               #first item in this address range
               placement_address=start_address
               break            
            elif other.address<end_address:
               placement_address=(other.address+other.length+address_boundary-1) & (~(address_boundary-1))
               break            
            i-=1
      if placement_address+file.length <= end_address:
         file.address=placement_address
      else:
         raise ValueError('cannot file file into range(%d,%d)'%(start_address, end_address))

      
   def __len__(self):
      return len(self._keys)
      
   def __getitem__(self, index):
      return self._items[index]
      
      