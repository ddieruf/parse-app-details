import pprint
import linecache
import re
import csv

from org import org
from quota import quota
from space import space
from app import app
from serviceInstance import serviceInstance

pp = pprint.PrettyPrinter(indent=2)
data = {
  "endpoint":"",
  "quotas":[],
  "orgs":[]
}
filePath = ""

def searchFileLines(searchCollection):
  global filePath
  ret = [(line, l, idx) for l in searchCollection for idx,line in enumerate(file(filePath)) if l in line]
  return ret

def getFileLine(lineNum):
  global filePath
  return linecache.getline(filePath, lineNum+1) #because it's zero based
def parseEndpoint():
  lineText = getFileLine(0)
  data["endpoint"] = lineText[lineText.find("Retrieved Authentication Endpoint:")+34:].strip()
def parseOrgs(): #find the first and last line of each org
  orgLines = searchFileLines(["Processing Org:","Finished processing Organization:"])
  startLineNum = 0

  for (line, searchStr, lineNum) in sorted(orgLines,key=lambda org: org[2]): #sort by line number
    if "Processing Org:" in searchStr:#the beginning of the org description
      startLineNum = lineNum
      continue

    if "Finished processing Organization:" in searchStr:
      if(startLineNum < 1 | startLineNum > lineNum):
        print "Could not parse org, invalid values were found"
        startLineNum = 0
        continue
      
      o = parseOrg(startLineNum, lineNum)
      data["orgs"].append(o)
      startLineNum = 0
      
def parseOrg(startLineNum, endLineNum):
  orgName = getFileLine(startLineNum).replace("Processing Org:","").replace(":","").strip()
  quotaName = getFileLine(startLineNum+1).replace("Using Quota :","").replace("null","").strip()
  o = org(orgName, quotaName)
  spaceStartLineNum = 0
  spaceServiceStartLineNum = 0
  
  #go through each line of the org and test for value
  for lineNum in range(startLineNum,endLineNum):
    lineText = getFileLine(lineNum)

    if "UserName is:" in lineText:
      o.users.append(lineText.replace("UserName is:","").strip())
      continue
    
    if "Processing space:" in lineText:#the beginning of a space description
      spaceStartLineNum = lineNum
      continue

    if "Processing Space Services for:" in lineText:
      spaceServiceStartLineNum = lineNum
      continue

    if "Processing for Space:" in lineText:
      if(spaceStartLineNum < 1 | spaceStartLineNum > lineNum):
        print "Could not parse space, invalid values were found"
        spaceStartLineNum = 0
        continue
      
      sp = parseSpace(spaceStartLineNum, lineNum)
      sp.serviceInstances = parseServiceInstances(spaceServiceStartLineNum, lineNum)
      o.spaces.append(sp)
      spaceStartLineNum = 0

  return o

def parseSpace(startLineNum, endLineNum):
  firstLine = getFileLine(startLineNum)
  spaceName = firstLine[firstLine.find("Processing space:")+17 : firstLine.find("using space quota")].strip()
  quotaName = firstLine[firstLine.find("using space quota:")+18 :].replace("null","").strip()
  s = space(spaceName, quotaName)
  appStartLineNum = 0

  #go through each line of the space and test for value
  for lineNum in range(startLineNum,endLineNum):
    lineText = getFileLine(lineNum)

    if "App Name is:" in lineText:
      appStartLineNum = lineNum
      continue

    if "instance state is:" in lineText:
      if(appStartLineNum < 1 | appStartLineNum > lineNum):
        print "Could not parse apps, invalid values were found"
        appStartLineNum = 0
        continue
      
      a = parseApp(appStartLineNum, lineNum)
      s.apps.append(a)
      appStartLineNum = 0

  return s

def parseApp(startLineNum, endLineNum):
  for (idx, lineNum) in enumerate(range(startLineNum,endLineNum+1)):
    lineText = getFileLine(lineNum)
    if idx is 0:
      appName = lineText[lineText.find("App Name is:")+12:].strip()
      continue

    if idx is 1:
      instanceCount = lineText[lineText.find("App instances are:")+18:].strip()
      continue

    if idx is 2:
      memory = lineText[lineText.find("App memory allocated is:")+24:].strip()
      continue

    if idx is 3:
      disk = lineText[lineText.find("Disk quota allocated is:")+24:].strip()
      continue

    if idx is 4:
      buildpack = lineText[lineText.find("Build Pack is:")+14:].strip()
      continue

    if idx is 5:
      state = lineText[lineText.find("instance state is:")+18:].strip()
      continue
  
  return app(appName, instanceCount, memory, disk, buildpack, state)

def parseQuotas():
  quotaLines = searchFileLines(["Quota Details for:"])

  for (line, searchStr, lineNum) in quotaLines:
    name = line.replace(searchStr,"").replace(":","").strip()
    lineInfo = getFileLine(lineNum+1).strip()
    delimiters = ["Total Memory:", "Instance Memory:", "Number of Routes:", "Number of Service Instances:"]
    regexPattern = '|'.join(map(re.escape, delimiters))
    splitValues = re.split(regexPattern, lineInfo)
    q = quota(name, int(splitValues[1]), int(splitValues[2]), int(splitValues[3]), int(splitValues[4]))
    data["quotas"].append(q)

  #print data["quotas"][0].__dict__
def parseServiceInstances(startLineNum, endLineNum):
  servStartLineNum = 0
  instances = []

  for lineNum in range(startLineNum,endLineNum):
    lineText = getFileLine(lineNum)

    if "Service Instance Name is:" in lineText:
      servStartLineNum = lineNum
      continue

    if "Service description is:" in lineText:
      if(servStartLineNum < 1 | servStartLineNum > lineNum):
        print "Could not parse service, invalid values were found"
        servStartLineNum = 0
        continue
      
      si = parseServiceInstance(servStartLineNum, lineNum)
      instances.append(si)
      servStartLineNum = 0
  return instances

def parseServiceInstance(startLineNum, endLineNum):
  for (idx, lineNum) in enumerate(range(startLineNum,endLineNum+1)):
    lineText = getFileLine(lineNum)
    if idx is 0:
      instanceName = lineText[lineText.find("Service Instance Name is:")+25:].strip()
      continue

    if idx is 1:
      serviceType = lineText[lineText.find("Service type is:")+16:].strip()
      continue

    if idx is 2:
      serviceName = lineText[lineText.find("Service name is:")+16:].strip()
      continue

    if idx is 3:
      plan = lineText[lineText.find("Service plan is:")+16:].strip()
      continue

    if idx is 4:
      description = lineText[lineText.find("Service description is:")+23:].strip()
      continue
  
  return serviceInstance(instanceName, serviceType, serviceName, plan, description)

def parseFile(file_path):
  global filePath
  filePath = file_path

  parseEndpoint()
  parseQuotas()
  parseOrgs()

  #print pp.pprint(data['orgs'][0].__dict__)
  #print pp.pprint(data['orgs'][0].spaces[0].__dict__)
  #print pp.pprint(data['orgs'][0].spaces[0].apps[0].__dict__)
  #print pp.pprint(data['orgs'][0].spaces[0].serviceInstances[0].__dict__)
  #print pp.pprint(data)

def exportToCSV():
  with open('export.csv', 'wb') as f:  # Just use 'w' mode in 3.x
    w = csv.writer(f,delimiter=',', quotechar='\"', quoting=csv.QUOTE_MINIMAL)
    w.writerow(["Org","Space","App","Instance Count","Memory","Disk Quota","Buildpack","State"])

    for org in data["orgs"]:
      if(len(org.spaces) == 0):
        w.writerow([org.name])
        continue

      for space in org.spaces:
        if(len(space.apps) == 0):
          w.writerow([org.name, space.name])
          continue

      for app in space.apps:
          w.writerow([org.name,space.name,app.name, app.instanceCount,app.memory,app.diskQuota,app.buildpack,app.state])

if __name__ == "__main__":
  parseFile("FoundationDetails_api.system.nwhackathon.com.txt")
  exportToCSV()
