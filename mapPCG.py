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
EFFECT_DIR = CUR_DIR+"/imgs/dungeon_crawl/effect/"
STATUE_DIR = CUR_DIR+"/imgs/dungeon_crawl/dungeon/statues/"
ALTAR_DIR = CUR_DIR+"/imgs/dungeon_crawl/dungeon/altars/"
CHARAC_SHEET = CUR_DIR+"/data/characters.xml"
FOES_SHEET = CUR_DIR+"/data/foes.xml"
HOUSE_DIR = CUR_DIR+"/imgs/houses/"
WATER_DIR = CUR_DIR+"/imgs/dungeon_crawl/dungeon/water/"
DUNGEON_DIR = CUR_DIR+"/imgs/dungeon_crawl/dungeon/"
MONSTER_DIR = CUR_DIR+"/imgs/dungeon_crawl/monster/"
N_LEVELS = {0.0: 1, 0.25: 2, 0.5: 3, 0.75: 4}
THEMES = {0: ["autumn", "forest", "field"], 1: ["city", "village", "graveyard"], 2: ["cave", "temple", "beach"], 3: ["volcano", "hell", "frozen_lake"]}

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
#	tile:	texture tile to check
#	texts:	texture set
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
#returns: floor image, grass textures, mud textures
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

#Generates floor according to dimensions
#	width,height:	Dimensions of level
#	dirPath:		Path to fetch item textures at
#	category:		Category of floor
#returns floor image
def placeFloor(category, dirPath, width, height):
	deprecated = "old"
	levelMap = [[] for i in range(width)]
	images = []
	floorFiles = glob.glob(dirPath + "*.bmp")
	for floor in floorFiles:
		basename = floor.split("/")[-1]
		if category in basename and deprecated not in basename:
			images.append(Image.open(floor).resize((TILE_SIZE,TILE_SIZE)).copy())
	cat_len = len(images)
	for y in range(height):
		for x in range(width):
			levelMap[x].append(images[random.randint(0, cat_len-1)])
	return levelMap

#Places line of images on top of floor
#	levelMap:		2d image array of grass floor
#	lineLength:		Length of line to be placed
#	axis:			Horizontal or vertical axis
#	category:		What to place
#	dirPath:		Path to item
#	obstacles:		List of all obstacles in level image
#	width,height:	Dimensions of level
#	placeDims:		If present, attempt to place line here
def placeLine(levelMap, lineLength, axis, category, dirPath, obstacles, width, height, placeDims=(-1,-1), walkable=False):
	items = []
	images = glob.glob(dirPath + "*.bmp")
	for image in images:
		if category in image.split("/")[-1]:
			items.append(Image.open(image).resize((TILE_SIZE,TILE_SIZE)).copy())
	cat_len = len(items)
	while True:
		if placeDims == (-1,-1):#place random
			x_loc = random.randint(0, width-1)
			y_loc = random.randint(0, height-1)
		else:
			(x_loc, y_loc) = placeDims
		if axis == 0:
			if x_loc + lineLength > width:
				continue
			line = [(x, y_loc) for x in range(x_loc, x_loc+lineLength)]
		else:
			if y_loc + lineLength > height:
				continue
			line = [(x_loc, y) for y in range(y_loc, y_loc+lineLength)]
		if all([elem not in obstacles for elem in line]):
			if not walkable:
				obstacles.extend(line)
			for dim in line:
				levelMap[dim[0]][dim[1]] = overlay2Images(items[random.randint(0, cat_len-1)], levelMap[dim[0]][dim[1]])
			break
		if placeDims != (-1,-1):#always break for non-random placement
			break

#Add structure/shape of items to levelmap image
#	levelMap:		2d image array of grass floor
#	size:			Size of shape
#	shape:			Shape of items to place
#	category:		Category to place
#	dirPath:		Path to fetch item textures at
#	obstacles:		Locations which are occupied
#	width,height:	Dimensions of level
def placeShape(levelMap, size, shape, category, dirPath, obstacles, width, height, walkable=False):
	items = []
	images = glob.glob(dirPath + "*.bmp")
	while True:
		x = random.randint(0, width-1)
		y = random.randint(0, height-1)
		if shape == 'L':#L
			space = [(x, i) for i in range(y, y+size)] + [(i, y+size-1) for i in range(x+1, x+size)]
			if x+size >= width or y+size >= height or not all([elem not in obstacles for elem in space]):
				continue
			placeLine(levelMap, size, 1, category, dirPath, obstacles, width, height, (x,y), walkable=walkable)
			placeLine(levelMap, size-1, 0, category, dirPath, obstacles, width, height, (x+1,y+size-1), walkable=walkable)
			break
		elif shape == 'diagonal':#Diagonal
			gradient = random.choice([-1,1])
			space = []
			while len(space) < size:
				space.append((x+(len(space)*gradient),y+(len(space)*gradient)))
			if not all([elem[0] < width and elem[1] < height and elem not in obstacles for elem in space]):
				continue
			for loc in space:
				placeLine(levelMap, 1, 1, category, dirPath, obstacles, width, height, placeDims=loc, walkable=walkable)
			break
		elif shape == 'block':#block
			space = [[(i,j) for i in range(x,x+size-1)] for j in range(y,y+size-1)]
			if x+size >= width or y+size >= height or not all([elem not in obstacles for elem in space]):
				continue
			for i in range(size):
				placeLine(levelMap, size, 1, category, dirPath, obstacles, width, height, (x+i,y), walkable=walkable)
			break

#Add trees to grass floor image
#	levelMap:		2d image array of grass floor
#	nItem:			Amount of items to place
#	freeTexts: 		Set of textures where items can be placed
#	chosen_cat:		Category to place
#	dirPath:		Path to fetch item textures at
#	width,height:	Dimensions of level	
def placeRandom(levelMap, nItem, obstacles, chosen_cat, dirPath, width, height, walkable=False):
	count = 0
	items = []
	images = glob.glob(dirPath + "*.bmp")
	for image in images:
		if chosen_cat in image.split("/")[-1]:
			items.append(Image.open(image).resize((TILE_SIZE,TILE_SIZE)).copy())
	cat_len = len(items)
	while count < nItem:
		x_loc = random.randint(0, width-1)
		y_loc = random.randint(0, height-1)
		if (x_loc,y_loc) not in obstacles:
			levelMap[x_loc][y_loc] = overlay2Images(items[random.randint(0, cat_len-1)], levelMap[x_loc][y_loc])
			if not walkable:
				obstacles.append((x_loc, y_loc))
		else:
			continue
		count += 1

#Place resized item randomly
#	levelMap:		2d image array of grass floor
#	dirPath:		Path to texture set
#	category:		Category to place
#	size:			Size of item to place
#	obstacles:		Locations which are occupied
#	width,height:	Dimensions of level
def placeResized(levelMap, dirPath, category, size, obstacles, width, height, walkable=False):
	deprecated = "old"
	locs = getFreeArea(obstacles, size**2, width, height)
	orig = locs[0]
	items = []
	images = glob.glob(dirPath + "*.bmp")
	for image in images:
		if category in image.split("/")[-1] and deprecated not in image:
			items.append(Image.open(image).resize((TILE_SIZE*size,TILE_SIZE*size)).copy())
	cat_len = len(items)
	chosen_item = random.choice(items)
	for x in range(size):
		for y in range(size):
			levelMap[orig[0]+x][orig[1]+y] = overlay2Images(chosen_item.crop((x*TILE_SIZE, y*TILE_SIZE, (x+1)*TILE_SIZE, (y+1)*TILE_SIZE)),levelMap[orig[0]+x][orig[1]+y])# (left, upper, right, lower)
	if not walkable:
		obstacles.extend(locs)

#Parses normalized difficulty from options.xml file
#returns: float difficulty
def getDifficulty():
	tree = ET.parse(CUR_DIR+'/saves/options.xml').getroot()
	try:
		return float(tree.findall("difficulty")[0].text)
	except:
		print("No difficulty found in the options.xml file!")

#Get area where protagonists can be placed on the map
#	obstacles:		List of location tuples where obstalces reside
#	nTiles:			Amount of tiles to place
#	width,height:	Dimensions of level
#returns: list of location tuples
def getFreeArea(obstacles, nTiles, width, height):
	areaSize = int(nTiles) if (nTiles % 2) == 0 else int(nTiles+1)
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
#	obstacles:	List of location tuples where obstacles reside
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

#delete previous levels
def deleteLevels():
	for root, dirnames, filenames in os.walk(CUR_DIR+"/maps/"):
		if filenames:
			for file in filenames:
				os.remove(root+"/"+file)
		
#coordinates level/map generation according to parameters
def generateMaps():
	width = 22
	height = 14
	nLevels = 0
	deleteLevels()
	difficulty = getDifficulty()
	#delete previous levels

	for diff in N_LEVELS.keys():
		if difficulty >= diff:
			nLevels = N_LEVELS[diff]
	for level in range(nLevels):
		theme = random.choice(THEMES[level])
		obstacles = []
		if theme == "autumn":
			image, grassTexts, _ = placeGrassFloor(width, height, "grass0")
			placeRandom(image, 18, obstacles, "tree_", TREE_DIR, width, height)#amount of trees based on difficulty
		elif theme == "forest":
			image, grassTexts, mudTexts = placeGrassFloor(width, height, "grass_flowers")
			placeRandom(image, 18, obstacles, "mangrove_", TREE_DIR, width, height)#amount of trees based on difficulty
			placeRandom(image, 18, obstacles, "cloud_spectral_", EFFECT_DIR, width, height)
		elif theme == "field":
			image, grassTexts, mudTexts = placeGrassFloor(width, height, "grassfield")
			placeMudpatches(image, grassTexts, mudTexts, 20, width, height)
		elif theme == "graveyard":
			image = placeFloor("floor_vines", FLOOR_DIR, width, height)
			for _ in range(8):
				placeLine(image, 10, 0, "altar_base", ALTAR_DIR, obstacles, width, height)
		elif theme == "city":
			image = placeFloor("pedestal_full", FLOOR_DIR, width, height)
			for i in range(4):
				placeLine(image, i, 0, "_house", HOUSE_DIR, obstacles, width, height)			
				placeShape(image, i, "block", "_house", HOUSE_DIR, obstacles, width, height)
				placeLine(image, 1, 0, "church", HOUSE_DIR, obstacles, width, height)	
				placeShape(image, i, "block", "floor_sand_rock", FLOOR_DIR, obstacles, width, height, walkable=True)
		elif theme == "village":
			image = placeFloor("dirt_", FLOOR_DIR, width, height)
			placeLine(image, width, 0, "fence_south.bmp", HOUSE_DIR, obstacles, width, height, placeDims=(0,0))
			placeLine(image, width, 0, "fence_south.bmp", HOUSE_DIR, obstacles, width, height, placeDims=(0,height-1))
			for _ in range(4):
				placeShape(image, 4, "diagonal", "_house", HOUSE_DIR, obstacles, width, height)
				placeLine(image, 10, 0, "_house", HOUSE_DIR, obstacles, width, height)	
		elif theme == "cave":
			image = placeFloor("cobble", FLOOR_DIR, width, height)
			placeResized(image, DUNGEON_DIR, "boulder", 2, obstacles, width, height)
			placeRandom(image, 10, obstacles, "boulder", DUNGEON_DIR, width, height)
			placeRandom(image, 10, obstacles, "rock", EFFECT_DIR, width, height)
			placeRandom(image, 10, obstacles, "stone_0", EFFECT_DIR, width, height, walkable=True)
			placeRandom(image, 3, obstacles, "eye_filled_portal", EFFECT_DIR, width, height, walkable=True)
			placeRandom(image, 2, obstacles, "tomahawk", EFFECT_DIR, width, height, walkable=True)
		elif theme == "temple":
			image = placeFloor("limestone", FLOOR_DIR, width, height)
			placeLine(image, height, 1, "crumbled_column_1", STATUE_DIR, obstacles, width, height, placeDims=(0,0))
			placeLine(image, height, 1, "crumbled_column_1", STATUE_DIR, obstacles, width, height, placeDims=(width-1,0))
			placeLine(image, width-2, 0, "crumbled_column_1", STATUE_DIR, obstacles, width, height, placeDims=(1,0))
			for i in range(5):
				placeShape(image, i, "diagonal", "statue_angel", STATUE_DIR, obstacles, width, height)
				placeLine(image, i, "L", "shining_one", ALTAR_DIR, obstacles, width, height)
		elif theme == "beach":
			image = placeFloor("floor_sand_stone", FLOOR_DIR, width, height)
			placeLine(image, width, 0, "shoals_shallow_water_6.bmp", WATER_DIR, obstacles, width, height, placeDims=(0,0))
			placeLine(image, width, 0, "shoals_shallow_water_6.bmp", WATER_DIR, obstacles, width, height, placeDims=(0,1))
			placeLine(image, width, 0, "shallow_water_wave_north_new.bmp", WATER_DIR, obstacles, width, height, placeDims=(0,2), walkable=True)
			placeRandom(image, 4, obstacles, "turtle", MONSTER_DIR+"animals/", width, height)
			placeRandom(image, 5, obstacles, "rock", EFFECT_DIR, width, height)
		elif theme == "volcano":
			image = placeFloor("pebble_red", WALL_DIR, width, height)
			for i in range(6):
				placeShape(image, i, "block", "lava_", FLOOR_DIR, obstacles, width, height)
				placeShape(image, i, "L", "lava_", FLOOR_DIR, obstacles, width, height)
		elif theme == "hell":
			image = placeFloor("hell", WALL_DIR, width, height)
			placeLine(image, height, 1, "wraith", STATUE_DIR, obstacles, width, height, placeDims=(0,0))
			placeLine(image, height, 1, "wraith", STATUE_DIR, obstacles, width, height, placeDims=(width-1,0))
			placeLine(image, width-2, 0, "wraith", STATUE_DIR, obstacles, width, height, placeDims=(1,0))
			placeRandom(image, 5, obstacles, "torch", WALL_DIR+"torches/", width, height)
			placeRandom(image, 10, obstacles, "cloud_fire", EFFECT_DIR, width, height, walkable=True)
			placeRandom(image, 5, obstacles, "banner", WALL_DIR+"banners/", width, height)
		elif theme == "frozen_lake":
			image = placeFloor("frozen", FLOOR_DIR, width, height)
			placeLine(image, 10, 1, "block_of_ice", MONSTER_DIR+"statues/", obstacles, width, height)
		writeLevel(image, LEVEL_DIR+"level_"+str(level)+"/map.bmp")
		writeXML(difficulty, obstacles, image, (width, height), LEVEL_DIR+"level_"+str(level)+"/data.xml")
