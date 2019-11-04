import sys
from xml.dom import minidom

# parse an xml file by name
mydoc = minidom.parse('ConfigureFramework.xml')

items = mydoc.getElementsByTagName('Framework')

path = items[0].attributes['path'].value
sys.path.insert(0,path)
from Frameworks import PartitioningFramework as dP

