import apx
import apx.parser
import apx.context


@apx.ApxNodeDataHandler.register
class NodeData():
   """
   APX NodeData class
   """
   
   def __init__(self,node):
      parser = apx.parser.ApxParser()
      if isinstance(node, apx.Node):         
         ctx = apx.context.Context()
         ctx.append(node)
         apx_text = ctx.dumps()
         parsed_node = parser.loads(apx_text)
      elif isinstance(node, str):
         apx_text=node
         parsed_node = parser.loads(apx_text)
      else:
         raise NotImplementedError(type(node))
      self.name=parsed_node.name
      self.inPortDataFile = self._createInPortDataFile(parsed_node)
      self.outPortDataFile = self._createOutPortDataFile(parsed_node)
      self.definitionFile = self._createDefinitionFile(node.name,apx_text)
      
         
         
   def _createInPortDataFile(self, node):
      fileLen=0
      for port in node.requirePortList:
         packLen = port.dsg.packLen(node.typeList)
         fileLen+=packLen
      if fileLen > 0:
         file = apx.ApxInputFile(node.name+'.in', fileLen)
         #TODO: implement support for init values
         return file
      return None

   def _createOutPortDataFile(self, node):
      fileLen=0
      for port in node.providePortList:
         packLen = port.dsg.packLen(node.typeList)
         fileLen+=packLen
      if fileLen > 0:
         file = apx.ApxOutputFile(node.name+'.out', fileLen)
         #TODO: implement support for init values
         return file
      return None

   
   def _createDefinitionFile(self, node_name, apx_text):
      file = apx.ApxOutputFile(node_name+'.apx', len(apx_text))      
      file.write(0,bytes(apx_text, encoding='ascii'))
      return file
      
   def inPortDataWriteNotification(self, offset: int, length, int):
      """
      Called by FileManager when it receives a remote write in the node's inPortData file
      """
      pass