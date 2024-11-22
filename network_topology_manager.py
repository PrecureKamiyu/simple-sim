import random
import logging

logging.basicConfig(level=logging.INFO)

class NetworkTopologyManager:
    def __init__(self):
        self.devices = {}

    def add_device(self, device_id, device_info):
        self.devices[device_id] = device_info

    def remove_device(self, device_id):
        if device_id in self.devices:
            del self.devices[device_id]

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
