import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import apx
import unittest
import remotefile
import time

class TestFileManager(unittest.TestCase):
 
   def setUp(self):
      pass
 
   def test_workerStartStop(self):
      #test explicit shutdown using stop method
      mgr = apx.ApxFileManager()
      mgr.start()      
      mgr.stop()
      self.assertEqual(mgr.worker, None)
   
   def test_fileManagerWithNode(self):      
      node = apx.Node('Simulator')

      node.dataTypes.append(apx.RawDataType('PSNoFaultFault_T','C(0,3)'))
      node.providePorts.append(apx.RawProvidePort('PV_VehicleSpeed','S','=65535'))
      node.providePorts.append(apx.RawProvidePort('PS_MainBeam','C(0,3)','=3'))
      node.providePorts.append(apx.RawProvidePort('PV_FuelLevel','C'))
      node.providePorts.append(apx.RawProvidePort('PS_ParkBrakeFault','T[0]','=3'))
      node.requirePorts.append(apx.RawRequirePort('ACCTimeGap_StalkStatus','C(0,7)','=7'))
      node.requirePorts.append(apx.RawRequirePort('AdjustRheostatLevel_GUIrqst','C','=255'))
      nodeData = apx.NodeData(node)
      fileManager = apx.ApxFileManager()
      fileManager.attachNodeData(nodeData)
      fileManager.start()
      fileManager.stop()
      


if __name__ == '__main__':
    unittest.main()   

