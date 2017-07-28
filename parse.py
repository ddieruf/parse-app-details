import argparse
import fileParser

parser = argparse.ArgumentParser(prog='python parse', description='Parse foundation details to xml')
parser.add_argument('inputFile', help='The foundation details txt')
parser.add_argument('outputFile', help='The foundation details txt')
args = parser.parse_args()

if __name__ == "__main__":
  print "Parsing file \"" + args.inputFile + "\""
  fileParser.parseFile(args.inputFile, args.outputFile)
  print "Outputting to \"" + args.outputFile + "\""
  fileParser.exportToCSV()
