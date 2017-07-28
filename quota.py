class quota:
  def __init__(self, name, totalMemory, instanceMemory, numRoutes, numServiceInstances):
    self.name = name
    self.totalMemory = totalMemory
    self.instanceMemory = instanceMemory
    self.numRoutes = numRoutes
    self.numServiceInstances = numServiceInstances
