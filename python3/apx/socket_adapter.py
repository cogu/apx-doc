import socket
import numheader
import threading

class TcpClient:
   """
   APX TCP client
   """
   def __init__(self):
      self.connection = TcpClientConnection()

   def connect(self, address, port):
      self.connection.connect(address, port)
      self.connection.start()
   
   def stop(self):
      self.connection.stop()

class TcpClientConnection:
   """
   TCP Client Connection
   """
   def __init__(self):
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      
      
      def worker():
         while True:
            try:
               chunk = self.socket.recv(2048)
               if len(chunk)==0:                  
                  break
               else:
                  print('received %d bytes'%len(chunk))
            except ConnectionAbortedError:               
               break
         print("socket worker shutting down")
                  
      
      self.worker = threading.Thread(target=worker)
   
   def connect(self, address, port):
      self.socket.connect(('localhost', 4000))
      self.socket.send(bytes('RMFTP/1.0\n\n',encoding='ascii'))
   
   def start(self):
      self.worker.start()
      
   def stop(self):
      self.socket.shutdown(socket.SHUT_RD)
      self.socket.close()
      self.worker.join()
      
#msg_data = remotefile.packHeader(remotefile.RMF_CMD_START_ADDR)+remotefile.packFileInfo(file_info)
#print(type(msg_data),len(msg_data))
#msg_header = numheader.encode32(len(msg_data))
#clientsocket.send(msg_header+msg_data)
