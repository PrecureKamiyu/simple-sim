import unittest
from network_topology_manager import NetworkTopologyManager

class TestNetworkTopologyManager(unittest.TestCase):

    def setUp(self):
        self.topology_manager = NetworkTopologyManager()

    def test_add_device(self):
        self.topology_manager.add_device(1, {'name': 'Device1', 'type': 'EdgeDevice'})
        self.assertEqual(self.topology_manager.get_device_info(1), {'name': 'Device1', 'type': 'EdgeDevice'})

    def test_remove_device(self):
        self.topology_manager.add_device(1, {'name': 'Device1', 'type': 'EdgeDevice'})
        self.topology_manager.remove_device(1)
        self.assertIsNone(self.topology_manager.get_device_info(1))

    def test_update_topology(self):
        # Placeholder test for update_topology method
        self.topology_manager.update_topology()
        # Add assertions if needed

    def test_get_device_info(self):
        self.topology_manager.add_device(1, {'name': 'Device1', 'type': 'EdgeDevice'})
        self.assertEqual(self.topology_manager.get_device_info(1), {'name': 'Device1', 'type': 'EdgeDevice'})
        self.assertIsNone(self.topology_manager.get_device_info(2))

if __name__ == '__main__':
    unittest.main()
