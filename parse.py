import argparse
import fileParser

parser = argparse.ArgumentParser(prog='python parse', description='Parse foundation details to xml')
parser.add_argument('file', help='The foundation details txt')
args = parser.parse_args()

if __name__ == "__main__":
  print "Parsing file \"" + args.file + "\""
  fileParser.parseFile(args.file)
  fileParser.exportToCSV()
