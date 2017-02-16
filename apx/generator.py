import apx.base
import cfile as C

def _genCommentHeader(comment):
   lines = []  
   lines.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
   lines.append(C.line('// %s'%comment))
   lines.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
   return lines


class SignalInfo:
   def __init__(self, offset, pack_len, func, dsg, operation, init_value=None):
      self.offset=offset
      self.pack_len=pack_len
      self.init_value=init_value
      self.func=func
      self.dsg=dsg
      if operation == 'pack' or operation == 'unpack':
         self.operation=operation
      else:
         raise ValueError("operation: invalid parameter value '%s', expected 'pack' or 'unpack'"%operation)
        

class NodeGenerator:
   def __init__(self):
      self.includes=None

   def genPackUnpackInteger(self, code, buf, operation, valname, dsg, localvar, offset, indent):   
      dataLen=0
      resolvedDsg = dsg.resolveType()
      if resolvedDsg.data['type']=='c' or resolvedDsg.data['type']=='C':
         dataLen=1
         basetype='sint8' if resolvedDsg.data['type']=='c' else 'uint8'
      elif resolvedDsg.data['type']=='s' or resolvedDsg.data['type']=='S':
         dataLen=2
         basetype='sint16' if resolvedDsg.data['type']=='s' else 'uint16'
      elif resolvedDsg.data['type']=='l' or resolvedDsg.data['type']=='L':
         dataLen=4
         basetype='sint32' if resolvedDsg.data['type']=='l' else 'uint32'
      else:
         raise NotImplementedError(resolvedDsg.data['type'])
      if 'bufptr' in localvar:
         #relative addressing
         if operation == 'pack':
            code.append(C.statement('packLE(%s,(uint32) %s,(uint8) sizeof(%s))'%(localvar['bufptr'].name,valname,basetype),indent=indent))
         else:
            code.append(C.statement('%s = (%s) unpackLE(%s,(uint8) sizeof(%s))'%(valname, basetype, localvar['bufptr'].name, basetype), indent=indent))
         code.append(C.statement('%s+=(uint8) sizeof(%s)'%(localvar['bufptr'].name,basetype),indent=indent))
      else:
         #absolute addressing
         if dataLen==1:
            if operation == 'pack':
               code.append(C.statement("%s[%d]=(uint8) %s"%(buf.name,offset,valname),indent=indent))
            else: #unpack               
               code.append(C.statement("*%s = (%s) %s[%d]"%(valname, basetype, buf.name, offset),indent=indent))
         else:
            if operation == 'pack':
               code.append(C.statement('packLE(&%s[%d],(uint32) %s,(uint8) %du)'%(buf.name,offset,valname,dataLen),indent=indent))
            else: #unpack
               code.append(C.statement('*%s = (%s) unpackLE(&%s[%d],(uint8) %du)'%(valname, basetype, buf.name, offset, dataLen),indent=indent))
      return dataLen
   
   def genPackUnpackItem(self, code, buf, operation, val, dsg, localvar, offset, indent, indentStep):
      packLen=0
      if isinstance(val,C.variable):
         valname=val.name
      elif isinstance(val,str):
         valname=val
      else:
         raise ValueError(val)      
      if (dsg.isComplexType()):
         #raise NotImplemented('complex types not yet fully supported')
         if dsg.data['type'].startswith('a'): #string         
            if 'bufptr' in localvar:
               #use relative addressing using 'p' pointer
               if operation == 'pack':
                  if dsg.data['arrayLen']>1:
                     code.append(C.statement('memcpy(%s,%s,%d)'%(localvar['bufptr'].name,valname,dsg.data['arrayLen']-1),indent=indent))
                  code.append(C.statement("%s[%d]='\\0'"%(localvar['bufptr'].name,dsg.data['arrayLen']),indent=indent))
               else:
                  code.append(C.statement('memcpy(%s,%s,%d)'%(valname,localvar['bufptr'].name,dsg.data['arrayLen']),indent=indent))
               code.append(C.statement('%s+=%d'%(localvar['bufptr'].name,dsg.data['arrayLen']),indent=indent))
            else:               
               #use absolute addressing using buf variable and offset
               if operation == 'pack':
                  if dsg.data['arrayLen']>1:
                     code.append(C.statement('memcpy(&%s[%d],%s,%d)'%(buf.name,offset,valname,dsg.data['arrayLen']-1),indent=indent))
                  code.append(C.statement("%s[%d]='\\0'"%(buf.name,offset+dsg.data['arrayLen']-1),indent=indent))
               else:
                  code.append(C.statement('memcpy(%s,&%s[%d],%d)'%(valname,buf.name,offset,dsg.data['arrayLen']),indent=indent))
            packLen=dsg.data['arrayLen']
         elif dsg.data['type']=='record':
            if 'bufptr' not in localvar:
               localvar['bufptr']=C.variable('p','uint8',pointer=True)      
            for elem in dsg.data['elements']:                     
               if isinstance(val,C.variable):
                  #TODO: replace following lines with call to user hook that instead applies the _RE-rule to record elements
                  if val.pointer:
                     childName="%s->%s_RE"%(valname,elem['name'])
                  else:
                     childName="%s.%s_RE"%(valname,elem['name'])
               elif isinstance(val,str):
                  childName="%s.%s"%(valname,elem['name'])
               assert(elem is not None)
               itemLen=genPackUnpackItem(code, buf, operation, childName, apx.ApxDataSignature(elem), localvar, offset, indent, indentStep)
               offset+=itemLen
               packLen+=itemLen
         elif dsg.isArray():      
            if 'loopVar' not in localvar:            
               if dsg.data['arrayLen']<256:
                  typename='uint8'
               elif dsg.data['arrayLen']<65536:
                  typename='uint16'
               else:
                  typename='uint32' 
               localvar['loopVar']=C.variable('i',typename)
            else:
               if localvar['loopVar'].typename=='uint8' and (typename=='uint16' or typename=='uint32'):
                  localvar['loopVar'].typename=typename
               elif localvar['loopVar'].typename=='uint16' and typename=='uint32':
                  localvar['loopVar'].typename=typename
            if 'bufptr' not in localvar:         
               localvar['bufptr']=C.variable('p','uint8',pointer=True)         
            code.append(C.statement('for({0}=0;{0}<{1};{0}++)'.format(localvar['loopVar'].name,dsg.data['arrayLen']),indent=indent))
            block=C.block(indent=indent)
            indent+=indentStep
            itemLen=genPackUnpackItem(block, buf, operation, valname+'[%s]'%localvar['loopVar'].name, childType, localvar, offset)
            indent-=indentStep
            code.append(block)         
      else:
         packLen=self.genPackUnpackInteger(code, buf, operation, valname, dsg, localvar, offset, indent)
      return packLen
   
   def genPackUnpackFunc(self, func, buf, offset, operation, dsg, indent, indentStep):
      indent+=indentStep
      packLen=0
      code=C.block()
      localvar={'buf':'m_outPortdata'}
      val=func.arguments[0]
            
      codeBlock=C.sequence()
      packLen=self.genPackUnpackItem(codeBlock, buf, operation, val, dsg, localvar, offset, indent, indentStep)
      initializer=C.initializer(None,['(uint16)%du'%offset,'(uint16)%du'%packLen])
      if 'p' in localvar:
         code.append(C.statement(localvar['p'],indent=indent))
      for k,v in localvar.items():
         if k=='p' or k=='buf':
            continue
         else:
            code.append(C.statement(v,indent=indent))
      if operation=='pack':
         code.append(C.statement('apx_nodeData_lockOutPortData(&m_nodeData)', indent=indent))
      else:
         code.append(C.statement('apx_nodeData_lockInPortData(&m_nodeData)', indent=indent))
      if 'bufptr' in localvar:
         code.append(C.statement('%s=&%s[%d]'%(localvar['bufptr'].name,buf.name,offset),indent=indent))      
      code.extend(codeBlock)
      if operation=='pack':      
         code.append(C.statement(C.fcall('outPortData_writeCmd', params=[offset, packLen]),indent=indent))
      else:
         code.append(C.statement('apx_nodeData_unlockInPortData(&m_nodeData)', indent=indent))
      code.append(C.statement('return E_OK',indent=indent))
      indent-=indentStep
      return code,packLen
   
   def writeHeaderFile(self, fp, signalInfo, signalInfoMap, guard, node):
      #indent=0
      #indentStep=3
            
      headerFile=C.hfile(None,guard=guard)
      headerFile.code.append(C.blank(1))
      headerFile.code.append(C.include('Std_Types.h'))
      headerFile.code.append(C.include('Rte_Type.h'))
      headerFile.code.append(C.include('apx_nodeData.h'))
      headerFile.code.append(C.blank(1))
      headerFile.code.extend(_genCommentHeader('CONSTANTS'))
      
      shortDefines=[]
      for port in node.requirePortList:
         tmp = (['APX',self.name.upper(), 'OFFSET',port.name.upper()])
         if self.name.upper().startswith('APX'):
            del tmp[0]  
         identifier = '_'.join(tmp)
         signalInfoElem=signalInfoMap[port.name]
         assert(signalInfoElem.operation == 'unpack')
         id_len=len(identifier)
         headerFile.code.append(C.define(identifier, str(signalInfoElem.offset).rjust(60-id_len)))
         shortDefines.append(C.define('APX_OFFSET_'+port.name.upper(),identifier))
      headerFile.code.append(C.blank(1))
      if len(shortDefines)>0:
         headerFile.code.extend(shortDefines)
      headerFile.code.append(C.blank(1))
      headerFile.code.extend(_genCommentHeader('FUNCTION PROTOTYPES'))      
      initFunc = C.function('%s_init'%self.name,'void')
      nodeDataFunc = C.function('%s_getNodeData'%self.name,'apx_nodeData_t',pointer=True) 
      headerFile.code.append(C.statement(initFunc))
      headerFile.code.append(C.statement(nodeDataFunc))
      headerFile.code.append(C.blank(1))      
      for elem in signalInfo:
         headerFile.code.append(C.statement(elem.func))
         
      fp.write(str(headerFile))
      return (initFunc,nodeDataFunc)
   
   def writeSourceFile(self, fp, signalInfo, initFunc, nodeDataFunc, node, inPortDataLen, outPortDataLen):
      indent=0
      indentStep=3      
      sourceFile=C.cfile(None)
      code = sourceFile.code
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      code.append(C.line('// INCLUDES'))
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      code.append(C.sysinclude('string.h'))
      code.append(C.include('%s.h'%self.name))
      code.append(C.include('pack.h'))
      if self.includes is not None:
         for filename in self.includes:
            code.append(C.include(filename))
      code.append(C.blank(1))
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      code.append(C.line('// CONSTANTS AND DATA TYPES'))
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      code.append(C.define('APX_DEFINITON_LEN', str(len(node.text)+1)+'u')) #add 1 for empty newline
      code.append(C.define('APX_IN_PORT_DATA_LEN', str(inPortDataLen)+'u'))
      code.append(C.define('APX_OUT_PORT_DATA_LEN', str(outPortDataLen)+'u'))
      
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      code.append(C.line('// LOCAL FUNCTIONS'))
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      if outPortDataLen>0:
         code.append(C.statement('static void outPortData_writeCmd(apx_offset_t offset, apx_size_t len )'))

      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      code.append(C.line('// LOCAL VARIABLES'))
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      
      if (outPortDataLen) > 0:
         outDatabuf=C.variable('m_outPortdata','uint8', static=True, array='APX_OUT_PORT_DATA_LEN')
         outInitData=C.variable('m_outPortInitData','uint8_t', static=True, const=True, array='APX_OUT_PORT_DATA_LEN')
         code.append(str(outInitData)+'= {')
         #TODO: implement support for init values
         #initBytes=[]
         #for port in requirePorts:
         #   initBytes.extend(list(port['initValue']))
         #assert(len(initBytes) == databuf.array)
         code.append('   0')
         code.append('};')      
         code.append(C.blank(1))       
         code.append(C.statement(outDatabuf))
         code.append(C.statement(C.variable('m_outPortDirtyFlags','uint8_t', static=True, array='APX_OUT_PORT_DATA_LEN')))
      else:
         outDatabuf,outInitData = None,None         
      
      if (inPortDataLen) > 0:
         inDatabuf=C.variable('m_inPortdata','uint8', static=True, array='APX_IN_PORT_DATA_LEN')
         inInitData=C.variable('m_inPortInitData','uint8_t', static=True, const=True, array='APX_IN_PORT_DATA_LEN')
         code.append(str(inInitData)+'= {')
         #TODO: implement support for init values
         code.append('   0')
         code.append('};')      
         code.append(C.blank(1))       
         code.append(C.statement(inDatabuf))
         code.append(C.statement(C.variable('m_inPortDirtyFlags','uint8_t', static=True, array='APX_OUT_PORT_DATA_LEN')))
      else:
         inDatabuf,inInitData = None,None
      
      code.append(C.statement(C.variable('m_nodeData','apx_nodeData_t',static=True)))
      code.append(C.line('static const char *m_apxDefinitionData='))
      for line in node.text.split('\n'):
         line=line.replace('"','\\"')
         code.append(C.line('"%s\\n"'%line))         
      code.elements[-1].val+=';'
      code.append(C.blank(1))


      
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      code.append(C.line('// GLOBAL FUNCTIONS'))
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))

      sourceFile.code.append(initFunc)
      body=C.block(innerIndent=indentStep)
      if inPortDataLen>0:
         body.append(C.statement('memcpy(&m_inPortdata[0], &m_inPortInitData[0], APX_IN_PORT_DATA_LEN)'))
         body.append(C.statement('memset(&m_inPortDirtyFlags[0], 0, sizeof(m_inPortDirtyFlags))'))
      if outPortDataLen>0:
         body.append(C.statement('memcpy(&m_outPortdata[0], &m_outPortInitData[0], APX_OUT_PORT_DATA_LEN)'))
         body.append(C.statement('memset(&m_outPortDirtyFlags[0], 0, sizeof(m_outPortDirtyFlags))'))
      args = ['&m_nodeData', '"%s"'%(node.name), '(uint8_t*) &m_apxDefinitionData[0]', 'APX_DEFINITON_LEN']
      if inPortDataLen>0:
         args.extend(['&m_inPortdata[0]', '&m_inPortDirtyFlags[0]', 'APX_IN_PORT_DATA_LEN'])
      else:
         args.extend(['0','0','0'])
      if outPortDataLen>0:         
         args.extend(['&m_outPortdata[0]', '&m_outPortDirtyFlags[0]', 'APX_OUT_PORT_DATA_LEN'])
      else:
         args.extend(['0','0','0'])
      body.append(C.statement('apx_nodeData_create(%s)'%(', '.join(args))))
      body.append(C.line('#ifdef APX_POLLED_DATA_MODE', indent=0))
      body.append(C.statement('rbfs_create(&m_outPortDataCmdQueue, &m_outPortDataCmdBuf[0], APX_NUM_OUT_PORTS, APX_DATA_WRITE_CMD_SIZE)'))
      body.append(C.line('#endif', indent=0))
               
      sourceFile.code.append(body)
      sourceFile.code.append(C.blank(1))
    
      sourceFile.code.append(nodeDataFunc)
      body=C.block(innerIndent=indentStep)
      
      body.append(C.statement('return &m_nodeData'))
      sourceFile.code.append(body)
      sourceFile.code.append(C.blank(1))
    
      for signal in signalInfo:
         sourceFile.code.append(signal.func)
         if signal.operation == 'pack':
            databuf = outDatabuf
         else:
            databuf = inDatabuf
         body,packLen=self.genPackUnpackFunc(signal.func, databuf, signal.offset, signal.operation, signal.dsg.resolveType(), indent, indentStep)
         code.append(body)
         code.append(C.blank())
      
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      code.append(C.line('// LOCAL FUNCTIONS'))
      code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
      if outPortDataLen>0:
         code.append('''static void outPortData_writeCmd(apx_offset_t offset, apx_size_t len )
{
   if ( (apx_nodeData_getDataWriteMode(&m_nodeData) == true) && (m_outPortDirtyFlags[offset] == 0) )
   {      
      apx_dataWriteCmd_t cmd;
      cmd.offset=offset;
      cmd.len=len;
      m_outPortDirtyFlags[offset] = (uint8_t) 1u;
      apx_nodeData_unlockOutPortData(&m_nodeData);
      apx_nodeData_outPortDataWriteCmd(&m_nodeData, &cmd);
      return;
   }
   apx_nodeData_unlockOutPortData(&m_nodeData);
}
''')
      
      
      fp.write(str(sourceFile))
    
   def generate(self, node, header_fp, source_fp, name=None, includes=None):
      signalInfo=[]
      signalInfoMap={}
      inPortDataLen=0
      outPortDataLen=0
      offset=0
      if name is None:
         name='Apx_'+node.name
      self.name=name
      self.includes=includes
      #require ports (in ports)
      for port in node.requirePortList:
         is_pointer=False        
         func = C.function("%s_Read_%s"%(name,port.name),"Std_ReturnType")
         is_pointer=True
         func.add_arg(C.variable('val',port.dsg.typename(node.typeList),pointer=is_pointer))         
         packLen=port.dsg.packLen(node.typeList)
         port.dsg.typeList= node.typeList
         tmp = SignalInfo(offset,packLen,func,port.dsg,'unpack', 0) #TODO: implement init value
         signalInfo.append(tmp)
         signalInfoMap[port.name]=tmp
         inPortDataLen+=packLen
         offset+=packLen
      #provide ports (out ports)
      offset=0      
      for port in node.providePortList:
         is_pointer=False        
         func = C.function("%s_Write_%s"%(name,port.name),"Std_ReturnType")
         if port.dsg.isComplexType(node.typeList) and not port.dsg.isArray(node.typeList):
            is_pointer=True    
         func.add_arg(C.variable('val',port.dsg.typename(node.typeList),pointer=is_pointer))         
         packLen=port.dsg.packLen(node.typeList)
         port.dsg.typeList= node.typeList
         tmp = SignalInfo(offset,packLen,func,port.dsg,'pack',0)
         signalInfo.append(tmp) #TODO: implement init value
         signalInfoMap[port.name]=tmp
         outPortDataLen+=packLen
         offset+=packLen
            
      (initFunc,nodeDataFunc) = self.writeHeaderFile(header_fp, signalInfo, signalInfoMap, name.upper()+'_H', node)
      self.writeSourceFile(source_fp,signalInfo,initFunc,nodeDataFunc, node, inPortDataLen, outPortDataLen)
