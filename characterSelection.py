#characterSelection PCG
import xml.etree.ElementTree as ET
from io import BytesIO

CUR_DIR = os.getcwd()
CHARAC_SHEET = CUR_DIR+"/data/characters.xml"
FOES_SHEET = CUR_DIR+"/data/foes.xml"

#Get list of available characters from XML sheet (only fetches names, not stats yet)
#returns: list of character names
def getCharacters(path):
	tree = ET.parse(path).getroot() #read in the XML
	return [elem.tag for elem in tree]

#Writes xml file for protagonists based on difficulty and level
#	difficulty:	Normalised difficulty parameter
#	nLevels:	Amount of levels to create xml files for
def protagonistSelect(difficulty, nLevels):
	nAllies = 3
	document = ET.Element('characters')
	et = ET.ElementTree(document)
	pA = ET.SubElement(document, 'placementArea')#example of returning element 
	ET.SubElement(pA, 'height').text = str(20)#example of adding element with content
	f = BytesIO()
	et.write(f, encoding='utf-8', xml_declaration=True) 
	with open("", "wb") as outfile:#missing file path for xml write file
		outfile.write(f.getbuffer())

#Writes xml file for foes based on difficulty and level
#	difficulty:	Normalised difficulty parameter
#	nLevels:	Amount of levels to create xml files for
def foesSelect(difficulty, nLevels):
	nFoes = 1
	document = ET.Element('foes')
	et = ET.ElementTree(document)
	pA = ET.SubElement(document, 'placementArea')#example of returning element 
	ET.SubElement(pA, 'height').text = str(20)#example of adding element with content
	f = BytesIO()
	et.write(f, encoding='utf-8', xml_declaration=True) 
	with open("", "wb") as outfile:#missing file path for xml write file
		outfile.write(f.getbuffer())