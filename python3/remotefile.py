import struct
import abc
import queue
import threading

#constants

RMF_CMD_START_ADDR = 0x3FFFFC00

RMF_FILE_TYPE_FIXED =   0
RMF_FILE_TYPE_DYNAMIC = 1
RMF_FILE_TYPE_STREAM =  2

RMF_CMD_FILE_INFO = 3

RMF_DIGEST_TYPE_NONE = 0

def unpackHeader(data):
   """   
   Returns tuple (byte_parsed, more_bit, address)
   """
   i=0
   bytesParsed=0
   more_bit=False
   address=None
   if((i+1)<len(data)): #parse 16-bits
      b1,b2=data[i:i+2];i+=2
      if b1 & 0x40: more_bit=True
      if b1 & 0x80:
         #high_bit is set set, parse next 16 bits to form a full 30-bit address (2 bits reserved for flags)
         b1&=0x3F
         if (i+2)<len(data):
            b3,b4=data[i:i+2];i+=2            
            address=(b1<<24)|(b2<<16)|(b3<<8)|b4
      else:
         #parse 2 or 3 bytes as header depending on mode
         b1&=0x3F
         address=(b1<<8)|(b2)
      if address is not None:
         bytesParsed = i
   return (bytesParsed,more_bit,address)

def packHeader(address, more_bit=False):
   """
   packs address and more_bit into bytearray
   
   returns bytes
   """
   if address<16384:
      #address will fit into 16 bits
      b1,b2=(address>>8)&0x3F,address&0xFF
      if more_bit: b1|=0x40
      return bytes([b1,b2])
   elif address <1073741824:
      b1,b2,b3,b4=(address>>24)&0x3F,(address>>16)&0xFF,(address>>8)&0xFF,address&0xFF
      if more_bit: b1|=0x40
      return bytes([b1|0x80,b2,b3,b4])
   else:
      raise ValueError('address must be less than 1073741824')



def packFileInfo(info, byte_order='<'):
   """packs FileInfo object into bytearray b"""
   if info.address is None:
      raise ValueError('FileInfo object does not have an address')
   if (byte_order != '<') and (byte_order != '>'):
      raise ValueError('unknown byte_order: '+str(byte_order))
   fmt='%s3I2H32s%ds'%(byte_order,len(info.name))
   return struct.pack(fmt, RMF_CMD_FILE_INFO, info.address, info.length, info.fileType, info.digestType,
                      info.digestData,bytes(info.name,encoding='ascii'))


class File:
   """
   Base class for File. This can be inherited from in case you need more properties (e.g. APX).
   Note: in C implemenation this class is called FileInfo_t
   """
   def __init__(self, name, length, fileType=RMF_FILE_TYPE_FIXED, address=None):
      self.name = str(name)                      #part of FILEINFO struct 
      self.length = int(length)                  #part of FILEINFO struct 
      self.fileType = int(fileType)              #part of FILEINFO struct 
      self.address = address                     #part of FILEINFO struct 
      self.digestType = RMF_DIGEST_TYPE_NONE     #part of FILEINFO struct 
      self.digestData = bytes([0]*32)            #part of FILEINFO struct 
      self.isRemoteFile=False                    #not part of FILEINFO struct
      

class FileMap(metaclass=abc.ABCMeta):
   """
   abstract baseclass of FileMap
   
   FileMaps are used by the FileManager class.
   
   It is expected that files in the FileMap are sorted by address (in ascending order)
   """
   
   @abc.abstractmethod
   def insert(self, file):
      """
      inserts file into the FileMap. The FileMap must assign an address to the file when inserted
      """
   @abc.abstractmethod
   def remove(self, file):
      """
      removes file from FileMap.
      """

class FileManager:
   """
   The FileManager manages local and remote files mapped to a point-to-point connection
   """
   def __init__(self, localFileMap, remoteFileMap):
      assert(isinstance(localFileMap, FileMap))
      assert(isinstance(remoteFileMap, FileMap))
      self.localFileMap = localFileMap
      self.remoteFileMap = remoteFileMap
      
      def worker():
         """
         this is the worker thread.
         
         It awaits commands in the message queue q. When the special message None arrives it quits
         """
         
         #create handlerTable using closures to self
         handlerTable = [
            None,       #0
            None,       #1
            None,       #2
            self._FileInfo_handler #3, RMF_CMD_FILE_INFO
            ]
         while True:            
            msg = self.msgQueue.get()
            if msg is None:
               break
            if msg.id < len(handlerTable) and handlerTable[msg.id] is not None:
               handlerTable[msg.id](msg)
               
            
      self.msgQueue = queue.Queue()
      self.worker = threading.Thread(target=worker)
   
   def start(self):      
      self.worker.start()

   def stop(self):
      if self.worker is not None and self.worker.is_alive():
         #send special message None to stop the worker thread
         self.msgQueue.put(None)
         self.worker.join()
         self.worker=None
      
   def _FileInfo_handler(self, msg):
      print("_FileInfo_handler")
   
   def attachLocalFile(self, file):
      pass
   
   def requestRemoteFile(self, file):
      pass
      