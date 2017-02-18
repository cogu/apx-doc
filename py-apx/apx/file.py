import remotefile
import threading
import abc

class ApxNodeDataHandler(metaclass=abc.ABCMeta):
   @abc.abstractmethod
   def inPortDataWriteNotification(self, offset: int, length, int):
      """
      Notification called when inPortDataFile has been written to (from ApxFileManager)
      """


class ApxFile(remotefile.File):
   """
   This is the ApxFile class. It inherits from remotefile.File.
   
   In the C implementation this type is called apx_file_t.
   """
   def __init__(self, name, length):
      super().__init__(name, length)
      self.data = bytearray(length)
      self.dataLock = threading.Lock()

class ApxInputFile(ApxFile):
   """
   Represents input files, like nodename.in. It has the ability to notify application when ApxFileManager writes to it
   """
   def __init__(self, name, length):
      super().__init__(name, length)

class ApxOutputFile(ApxFile):
   """
   Represents an output file like nodename.out and nodename.apx. The ApxFileManager is allowed to read from it and ApxFileManager gets notifications when written to.
   """
   def __init__(self, name, length):
      super().__init__(name, length)
      self.fileManager = None

   def write(self, offset: int, data: bytes):
      """
      writes data at the given offset in the file
      """
      if(offset < 0) or (offset+len(data)>len(self.data) ):
         raise IndexError('file write outside file boundary detected')
      self.dataLock.acquire()
      self.data[offset:offset+len(data)]=data
      self.dataLock.release()
      if self.fileManager is not None:
         self.fileManager.outPortDataWriteNotificaion(offset, len(data))
      