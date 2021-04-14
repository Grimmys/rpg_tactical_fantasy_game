import os 
import glob
from PIL import Image
import random

TILE_SIZE = 32
CUR_DIR = os.getcwd()
FLOOR_DIR = CUR_DIR+"/imgs/dungeon_crawl/dungeon/floor/"
LEVEL_DIR = CUR_DIR+"/maps/"
WALL_DIR = CUR_DIR+"/imgs/dungeon_crawl/dungeon/wall/"
TREE_DIR = CUR_DIR+"/imgs/dungeon_crawl/dungeon/trees/"
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
	#back.paste(front.convert("RGBA"), (0, 0), front.convert("RGBA"))

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
	levelMap = [[] for i in range(height)]
	floorFiles = glob.glob(FLOOR_DIR + "grass/*.bmp")
	for file in floorFiles:
		found = False
		for texture in mud_tiles.keys():
			if deprecated not in file:
				if texture in file:#discard deprecated
					mud_tiles[texture].append(Image.open(file))
					found = True
					break
		if deprecated not in file and not found:
			if chosen_cat in file:
				grass_species.append(Image.open(file))
	cat_len = len(grass_species)
	for y in range(height):
		for x in range(width):
			levelMap[y].append(grass_species[random.randint(0, cat_len-1)])
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
			walls[category] = [Image.open(wall).copy()]
		else:
			walls[category].append(Image.open(wall).copy())
	chosen_wall = random.choice(list(walls.keys()))
	for y in range(height):
		for x in range(width):
			if x == 0 or y == 0 or x == width-1 or y == height-1:
				levelMap[x][y] = walls[chosen_wall][random.randint(0, len(walls[chosen_wall])-1)]

def placeMisc(miscDir):
	return

#Add trees to grass floor image
#	levelMap:		2d image array of grass floor
#	nTrees:			Amount of trees to place
#	grassTexts: 	Set of grass textures used in the floor
#	chosen_tree:	Tree category to place
#	width,height:	Dimensions of level	
def placeTrees(levelMap, nTrees, grassTexts, chosen_tree, width, height):
	count = 0
	trees = {chosen_tree: []}
	treeImages = glob.glob(TREE_DIR + "*.bmp")
	for tree in treeImages:
		if chosen_tree in tree.split("/")[-1]:
			trees[chosen_tree].append(Image.open(tree).copy())
	cat_len = len(trees[chosen_tree])
	while count < nTrees:
		x_loc = random.randint(0, width-1)
		y_loc = random.randint(0, height-1)
		if isinTextures(grassTexts, levelMap[x_loc][y_loc]):
			levelMap[x_loc][y_loc] = overlay2Images(trees[chosen_tree][random.randint(0, cat_len-1)], levelMap[x_loc][y_loc])
		else:
			continue
		count += 1

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

#coordinates level/map generation according to parameters
#	difficulty: 	normalized difficulty to base PCG on
def generateMap(difficulty):
	for level in range(1):
		theme = random.choice(THEMES[level])
		if theme == "autumn":
			image, grassTexts, mudTexts = placeGrassFloor(25, 25, "grass0")
			placeTrees(image, 18, grassTexts, "tree_", 25, 25)#amount of trees based on difficulty
		elif theme == "forest":
			image, grassTexts, mudTexts = placeGrassFloor(25, 25, "grass_flowers")
			placeTrees(image, 18, grassTexts, "mangrove_", 25, 25)#amount of trees based on difficulty
		elif theme == "field":
			image, grassTexts, mudTexts = placeGrassFloor(25, 25, "grassfield")
			placeMudpatches(image, grassTexts, mudTexts, 20, 25, 25)
		writeLevel(image, LEVEL_DIR+"level_"+str(level)+"/"+theme+".bmp")

	#placeWalls(image, width, height)

generateMap(0)