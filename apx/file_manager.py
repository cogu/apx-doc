import apx
import remotefile

class ApxFileManager(remotefile.FileManager):
   def __init__(self):
      super().__init__(apx.FileMap(), apx.FileMap())
   
   def attachNodeData(self, nodeData):
      if nodeData.outPortDataFile is not None:
         self.attachLocalFile(nodeData.outPortDataFile)
      if nodeData.definitionFile is not None:
         self.attachLocalFile(nodeData.definitionFile)
      if nodeData.inPortDataFile is not None:
         self.requestRemoteFile(nodeData.inPortDataFile)
   