class app:
  def __init__(self, name, instanceCount, memory, diskQuota, buildpack, state):
    self.name = name
    self.instanceCount = instanceCount
    self.memory = memory
    self.diskQuota = diskQuota
    self.buildpack = buildpack
    self.state = state