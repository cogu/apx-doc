def _decode(data, mode=16):
   """
   Decodes numheader from data (which is byte or bytearray).
   Mode can be either 16 or 32 (number of bits parsed when long_bit is 1)
   
   Returns tuple (bytesParsed, value)
   """   
   bytesParsed=0
   value=None
   if(1<=len(data)):
      b1=data[0]
      if b1 & 0x80:         
         b1&=0x7F
         #MSB is set, parse next 1 or 3 bytes depending on mode
         if mode == 16: #NumHeader16
            if(2<=len(data)):
               bytesParsed=2
               b2=data[1]
               value=(b1<<8 | b2)
               if value < 128: #range(0,128) with MSB set to 1 shall be interpreted as 32768..32895
                  value+=32768
         elif mode == 32: #NumHeader32
            if(4<=len(data)):
               bytesParsed=4
               b2,b3,b4=data[1:4]               
               value=(b1<<24)|(b2<<16)|(b3<<8)|b4
         else:
            raise ValueError('invalid mode argument: '+str(mode))
      else:
         bytesParsed=1
         value=b1
   return (bytesParsed,value)

def decode16(data):
   """
   Decodes NumHeader16 value from bytearray
   
   Returns tuple (bytesParsed, value)   
   """
   return _decode(data,16)

def decode32(data):
   """
   Decodes NumHeader32 value from bytearray
   
   Returns tuple (bytesParsed, value)   
   """
   return _decode(data,32)


def _encode(value, mode):
   """   
   Mode can be either 16 or 32 (number of bits written when long_bit is 1)
   
   returns a bytes object
   """
   
   bytesWritten=0
   
   if value<128:
      return bytes([value])
   else:
      if mode==16:
         if value<32768:
            return bytes([0x80 | (value >> 8),value & 0xFF])
         elif value < 32896:
            return bytes([0x80,(value-32768) &0xFF])
         else:
            raise ValueError("value must be an integer in range(0,32896)")
      elif mode == 32:
         if value < 2147483648:
            return bytes([(0x80 | ( (value >> 24) & 0xFF)),(value >> 16) & 0xFF, (value >> 8) & 0xFF, (value & 0xFF) ])            
         else:
            raise ValueError("value must be an integer in range(0,2147483648)")
      else:
          raise ValueError('invalid mode argument: '+str(mode))
   

def encode16(value):
   """
   Encodes NumHeader16 value 
   
   returns bytes object
   """   
   return _encode(value, 16)

def encode32(value):
   """
   Encodes NumHeader32 value
   
   returns bytes object
   """   
   return _encode(value, 32)

   