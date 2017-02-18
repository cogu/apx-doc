from apx.node import *
from apx.base import *
from apx.file import *
from apx.file_map import *
from apx.file_manager import *
from apx.node_data import *
import apx.generator #this is old stuff that needs to be rewritten/refactored
import apx.parser #this is old stuff that needs to be rewritten/refactored
import apx.context #this is old stuff that needs to be rewritten/refactored
from apx.socket_adapter import TcpClient



#helper functions
def Context():
   return apx.context.Context()

def node_from_swc(ws, swc):
   node = Node(swc.name)
   node.import_swc(ws, swc)
   return node

def ApxParser():
   return apx.parser.ApxParser()

def OutPortDataGenerator():
   return apx.generator.OutPortDataGenerator()

def NodeGenerator():
   return apx.generator.NodeGenerator()

def NodeData(node):
   return apx.node_data.NodeData(node)

   

