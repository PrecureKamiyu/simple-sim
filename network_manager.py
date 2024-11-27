import random
import logging

logging.basicConfig(level=logging.INFO)

class NetworkTopologyManager:
    def __init__(self):
        self.devices = {}
        self.frequencies = {}

    def add_device(self, device_id, device_info):
        self.devices[device_id] = device_info
        self.frequencies[device_id] = random.randint(100, 1000)

    def remove_device(self, device_id):
        if device_id in self.devices:
            del self.devices[device_id]
            del self.frequencies[device_id]

    def update_topology(self):
        # Simulate network events and update the topology
        self.simulate_device_failure()
        self.simulate_device_recovery()

    def simulate_device_failure(self):
        # Simulate a device failure by removing a random device
        if self.devices:
            device_id = random.choice(list(self.devices.keys()))
            self.remove_device(device_id)
            logging.info(f"Simulated device failure: Device {device_id} removed.")

    def simulate_device_recovery(self):
        # Simulate a device recovery by adding a new device
        new_device_id = max(self.devices.keys(), default=-1) + 1
        self.add_device(new_device_id, {'name': f'Device{new_device_id}', 'type': 'EdgeDevice'})
        logging.info(f"Simulated device recovery: Device {new_device_id} added.")

    def get_device_info(self, device_id):
        return self.devices.get(device_id, None)

    def get_frequency(self, device_id):
        return self.frequencies.get(device_id, None)

    def assign_frequency(self, device_id, frequency):
        self.frequencies[device_id] = frequency

class NetworkManager:
    def __init__(self, network_topology_manager: NetworkTopologyManager):
        self.network_topology_manager = network_topology_manager

    def get_device_info(self, device_id):
        return self.network_topology_manager.get_device_info(device_id)

    def get_frequency(self, device_id):
        return self.network_topology_manager.get_frequency(device_id)

    def assign_frequency(self, device_id, frequency):
        self.network_topology_manager.assign_frequency(device_id, frequency)
        
