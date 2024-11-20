class NetworkTopologyManager:
    def __init__(self):
        self.devices = {}

    def add_device(self, device_id, device_info):
        self.devices[device_id] = device_info

    def remove_device(self, device_id):
        if device_id in self.devices:
            del self.devices[device_id]

    def update_topology(self):
        # Placeholder for updating the network topology
        pass

    def get_device_info(self, device_id):
        return self.devices.get(device_id, None)
