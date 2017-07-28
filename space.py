class space:
  def __init__(self, name, quotaName):
    self.name = name
    self.quotaName = quotaName
    self.apps = []
    self.serviceInstances = []
