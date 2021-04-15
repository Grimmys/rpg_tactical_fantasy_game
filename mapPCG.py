import os 
import glob
from PIL import Image
import random
import xml.etree.ElementTree as ET
from io import BytesIO

TILE_SIZE = 48
CUR_DIR = os.getcwd()
FLOOR_DIR = CUR_DIR+"/imgs/dungeon_crawl/dungeon/floor/"
LEVEL_DIR = CUR_DIR+"/maps/"
WALL_DIR = CUR_DIR+"/imgs/dungeon_crawl/dungeon/wall/"
TREE_DIR = CUR_DIR+"/imgs/dungeon_crawl/dungeon/trees/"
CHARAC_SHEET = CUR_DIR+"/data/characters.xml"
FOES_SHEET = CUR_DIR+"/data/foes.xml"
THEMES = {0: ["autumn", "forest", "field"]}

#Splits file basename to text and numerical
#	path:	Path string to split
def basename_num_split(path):
	path = path.split("/")[-1]
	for index, letter in enumerate(path, 0):
		if letter.isdigit():
			return [path[:index],path[index:]]

#Combines two images into one
#	front:	Front layer image
#	back:	Background image
#returns: combined image
def overlay2Images(front, back):
	image = Image.new("RGBA", (TILE_SIZE, TILE_SIZE))
	image.paste(back.convert("RGBA"), (0,0), back.convert("RGBA"))
	image.paste(front.convert("RGBA"), (0,0), front.convert("RGBA"))
	return image.convert("RGB")

#Check if tile is present in texture set
#	texts:	texture set
#	tile:	texture tile to check
#returns: if tile is present in texture set
def isinTextures(texts, tile):
	return any(elem == tile for elem in texts)

#place (overlapping) mud patches on grass floor
#	levelMap:		2d image array of grass floor
#	grassTexts: 	Set of grass textures used in the floor
#	textures:		Set of mud patch textures
#	nPatches:		Amount of patches to place
#	width, height:	Dimensions of level
def placeMudpatches(levelMap, grassTexts, textures, nPatches, width, height):
	count = 0
	while count < nPatches:
		x_loc = random.randint(0, width-1)
		y_loc = random.randint(0, height-1)
		if levelMap[x_loc][y_loc] != textures["full"][0]:
			levelMap[x_loc][y_loc] = textures["full"][0]
		else:
			continue
		if x_loc - 1 >= 0:
			if isinTextures(grassTexts, levelMap[x_loc-1][y_loc]):
				levelMap[x_loc-1][y_loc] = textures["west"][0]
			else:
				levelMap[x_loc-1][y_loc] = textures["full"][0]
		if x_loc + 1 < width:
			if isinTextures(grassTexts, levelMap[x_loc+1][y_loc]):
				levelMap[x_loc+1][y_loc] = textures["east"][0]
			else:
				levelMap[x_loc+1][y_loc] = textures["full"][0]
		if y_loc - 1 >= 0:
			if isinTextures(grassTexts, levelMap[x_loc][y_loc-1]):
				levelMap[x_loc][y_loc-1] = textures["north"][0]
			else:
				levelMap[x_loc][y_loc-1] = textures["full"][0]
		if y_loc + 1 < height:
			if isinTextures(grassTexts, levelMap[x_loc][y_loc+1]):
				levelMap[x_loc][y_loc+1] = textures["south"][0]
			else:
				levelMap[x_loc][y_loc+1] = textures["full"][0]
		if y_loc - 1 >= 0 and x_loc + 1 < width:
			if isinTextures(grassTexts, levelMap[x_loc+1][y_loc-1]):
				levelMap[x_loc+1][y_loc-1] = textures["northeast"][0]
			else:
				levelMap[x_loc+1][y_loc-1] = textures["full"][0]
		if y_loc - 1 >= 0 and x_loc - 1 >= 0:
			if isinTextures(grassTexts, levelMap[x_loc-1][y_loc-1]):
				levelMap[x_loc-1][y_loc-1] = textures["northwest"][0]
			else:
				levelMap[x_loc-1][y_loc-1] = textures["full"][0]
		if y_loc + 1 < height and x_loc + 1 < width:
			if isinTextures(grassTexts, levelMap[x_loc+1][y_loc+1]):
				levelMap[x_loc+1][y_loc+1] = textures["southeast"][0]
			else:
				levelMap[x_loc+1][y_loc+1] = textures["full"][0]
		if y_loc + 1 < height and x_loc - 1 >= 0:
			if isinTextures(grassTexts, levelMap[x_loc-1][y_loc+1]):
				levelMap[x_loc-1][y_loc+1] = textures["southwest"][0]
			else:
				levelMap[x_loc-1][y_loc+1] = textures["full"][0]
		count += 1

#Generates grass floor according to dimensions
#	width,height:	Dimensions of level
#	chosen_cat:		Category of grass
def placeGrassFloor(width, height, chosen_cat):
	grass_species = []
	mud_tiles = {"northeast": [], "northwest": [], "southeast": [], "southwest": [], "north" : [], "west": [], "east": [], "south": [], "full": []}
	deprecated = "old"
	category = ""
	levelMap = [[] for i in range(width)]
	floorFiles = glob.glob(FLOOR_DIR + "grass/*.bmp")
	for file in floorFiles:
		found = False
		for texture in mud_tiles.keys():
			if deprecated not in file:
				if texture in file:#discard deprecated
					mud_tiles[texture].append(Image.open(file).resize((TILE_SIZE,TILE_SIZE)))
					found = True
					break
		if deprecated not in file and not found:
			if chosen_cat in file:
				grass_species.append(Image.open(file).resize((TILE_SIZE,TILE_SIZE)))
	cat_len = len(grass_species)
	for y in range(height):
		for x in range(width):
			levelMap[x].append(grass_species[random.randint(0, cat_len-1)])
	return levelMap, grass_species, mud_tiles 

#Add walls to levelmap image
#	levelMap:		2d image array of grass floor
#	width,height:	Dimensions of level
def placeWalls(levelMap, width, height):#categories not yet correct
	#first row, last row, first column, last column
	walls = {}
	category = ""
	wallImages = glob.glob(WALL_DIR + "*.bmp")
	for wall in wallImages:
		temp = wall.split("/")[-1].split("_")[0]
		if temp != category:
			category = temp
			walls[category] = [Image.open(wall).resize((TILE_SIZE,TILE_SIZE)).copy()]
		else:
			walls[category].append(Image.open(wall).resize((TILE_SIZE,TILE_SIZE)).copy())
	chosen_wall = random.choice(list(walls.keys()))
	for y in range(height):
		for x in range(width):
			if x == 0 or y == 0 or x == width-1 or y == height-1:
				levelMap[x][y] = walls[chosen_wall][random.randint(0, len(walls[chosen_wall])-1)]

def placeMisc(miscDir):
	return

#Add trees to grass floor image
#	levelMap:		2d image array of grass floor
#	nItem:			Amount of items to place
#	freeTexts: 		Set of textures where items can be placed
#	chosen_cat:		Category to place
#	dirPath:		Path to fetch item textures at
#	width,height:	Dimensions of level	
#returns: list of tree locations
def placeRandom(levelMap, nItem, freeTexts, chosen_cat, dirPath, width, height):
	count = 0
	items = {chosen_cat: []}
	locs = []
	images = glob.glob(dirPath + "*.bmp")
	for image in images:
		if chosen_cat in image.split("/")[-1]:
			items[chosen_cat].append(Image.open(image).resize((TILE_SIZE,TILE_SIZE)).copy())
	cat_len = len(items[chosen_cat])
	while count < nItem:
		x_loc = random.randint(0, width-1)
		y_loc = random.randint(0, height-1)
		if isinTextures(freeTexts, levelMap[x_loc][y_loc]):
			levelMap[x_loc][y_loc] = overlay2Images(items[chosen_cat][random.randint(0, cat_len-1)], levelMap[x_loc][y_loc])
			locs.append((x_loc, y_loc))
		else:
			continue
		count += 1
	return locs

#Get area where protagonists can be placed on the map
#	obstacles:		List of location tuples where obstalces reside
#	nTiles:			Amount of tiles to place
#	width,height:	Dimensions of level
#returns: list of location tuples
def getFreeArea(obstacles, nTiles, width, height):
	areaSize = nTiles if (nTiles % 2) == 0 else nTiles+1
	while True:
		area = []
		count = 0
		x_loc = random.randint(0, width-1)
		y_loc = random.randint(0, height-1)
		if nTiles == 1:
			if (x_loc,y_loc) not in obstacles:
				return [(x_loc,y_loc)]
			else:
				continue
		if y_loc+1 == height:
			continue
		while x_loc < width and (x_loc,y_loc) not in obstacles and (x_loc,y_loc+1) not in obstacles:
			count += 2
			area.extend([(x_loc,y_loc), (x_loc,y_loc+1)])
			x_loc = x_loc+1
			if count >= areaSize:
				return area
	return []

#Get list of available characters from XML sheet
#returns: list of character names
def getCharacters(path):
	tree = ET.parse(path).getroot() #read in the XML
	return [elem.tag for elem in tree]

#creates level image file given imageTiles
#	imageTiles: 	2d array of images (width x height)
#	levelName:  	Path string to write to
def writeLevel(imageTiles, levelPath):
	width = len(imageTiles)
	height = len(imageTiles[0])
	new_level = Image.new('RGB', (width*TILE_SIZE, height*TILE_SIZE))
	for y in range(height):
		for x in range(width):
			new_level.paste(imageTiles[x][y], (x*TILE_SIZE,y*TILE_SIZE))
	new_level.save(levelPath)

#creates XML file to read level image
#	difficulty:	Normalized difficulty to base PCG on
#	levelMap:	2d image array of grass floor
#	obstacles:	List of location tuples where obstalces reside
#	dims:		Dimensions of level
#	filePath:	Path to write XML file to
def writeXML(difficulty, obstacles, levelMap, dims, filePath):
	nAllies = 3
	nFoes = 1
	document = ET.Element('level')
	characters = getCharacters(CHARAC_SHEET)
	foeCharacs = getCharacters(FOES_SHEET)
	et = ET.ElementTree(document)
	ET.SubElement(document, 'width').text = str(dims[0])
	ET.SubElement(document, 'height').text = str(dims[1])
	pA = ET.SubElement(document, 'placementArea')
	pArea = getFreeArea(obstacles, nAllies, dims[0], dims[1])
	for loc in pArea:
		position = ET.SubElement(pA, 'position')
		ET.SubElement(position, 'x').text = str(loc[0])
		ET.SubElement(position, 'y').text = str(loc[1])
	events = ET.SubElement(document, 'events')
	foes = ET.SubElement(document, 'foes')
	for _ in range(nFoes):
		foe = ET.SubElement(foes, 'foe')
		ET.SubElement(foe, 'name').text = foeCharacs.pop()
		position = ET.SubElement(foe, 'position')
		foePos = getFreeArea(obstacles, 1, dims[0], dims[1])[0]
		ET.SubElement(position, 'x').text = str(foePos[0])
		ET.SubElement(position, 'y').text = str(foePos[1])
		ET.SubElement(foe, 'level').text = '1'
	bef_init = ET.SubElement(events, 'before_init')
	for _ in range(nAllies):
		player = ET.SubElement(bef_init, 'new_player')
		ET.SubElement(player, 'name').text = characters.pop()
		position = ET.SubElement(player, 'position')
		pos = pArea.pop()
		ET.SubElement(position, 'x').text = str(pos[0])
		ET.SubElement(position, 'y').text = str(pos[1])

	obstclElem = ET.SubElement(document, 'obstacles')
	for obs in obstacles:
		position = ET.SubElement(obstclElem, 'position')
		ET.SubElement(position, 'x').text = str(obs[0])
		ET.SubElement(position, 'y').text = str(obs[1])
	#missions
	missions = ET.SubElement(document, 'missions')
	main = ET.SubElement(missions, 'main')
	ET.SubElement(main, 'type').text = "POSITION"
	ET.SubElement(main, 'description').text = "Leave the village"
	position = ET.SubElement(main, 'position')
	ET.SubElement(position, 'x').text = str(0)
	ET.SubElement(position, 'y').text = str(0)
	f = BytesIO()
	et.write(f, encoding='utf-8', xml_declaration=True) 
	with open(filePath, "wb") as outfile:
		outfile.write(f.getbuffer())

#coordinates level/map generation according to parameters
#	difficulty: 	normalized difficulty to base PCG on
def generateMaps(difficulty):
	width = 20
	height = 14
	for level in range(1):
		theme = random.choice(THEMES[level])
		obstacles = []#[(x,height-2) for x in range(width)]+[(x,height-1) for x in range(width)]#buffer for GUI overlay
		if theme == "autumn":
			image, grassTexts, mudTexts = placeGrassFloor(width, height, "grass0")
			obstacles.extend(placeRandom(image, 18, grassTexts, "tree_", TREE_DIR, width, height))#amount of trees based on difficulty
		elif theme == "forest":
			image, grassTexts, mudTexts = placeGrassFloor(width, height, "grass_flowers")
			obstacles.extend(placeRandom(image, 18, grassTexts, "mangrove_", TREE_DIR, width, height))#amount of trees based on difficulty
		elif theme == "field":
			image, grassTexts, mudTexts = placeGrassFloor(width, height, "grassfield")
			placeMudpatches(image, grassTexts, mudTexts, 20, width, height)
		writeLevel(image, LEVEL_DIR+"level_"+str(level)+"/map.bmp")
		writeXML(difficulty, obstacles, image, (width, height), LEVEL_DIR+"level_"+str(level)+"/data.xml")
	#placeWalls(image, width, height)

generateMaps(0)