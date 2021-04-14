import os
import subprocess

png_list = str(subprocess.check_output("find . -type f -name \"*.png\"",shell=True)).split('\n')
png_list.extend(str(subprocess.check_output("find . -type f -name \"*.PNG\"",shell=True)).split('\n'))
jpg_list = str(subprocess.check_output("find . -type f -name \"*.jpg\"",shell=True)).split('\\n')
bmp_list = str(subprocess.check_output("find . -type f -name \"*.bmp\"",shell=True)).split('\\n')

#delete old png
#for png in png_list:
#	if os.path.isfile(png):
#		os.remove(png)
#		print("Removed "+png)

#conversion jpg
#for jpg in jpg_list:
#	if os.path.isfile(jpg):
#		os.system("magick "+jpg+" "+os.path.splitext(jpg)[0]+".bmp")
#		print(jpg+" -> "+os.path.splitext(jpg)[0]+".bmp")

#conversion png
#for png in png_list:
#	if os.path.isfile(png):
#		os.system("magick "+png+" "+os.path.splitext(png)[0]+".bmp")
#		print(png+" -> "+os.path.splitext(png)[0]+".bmp")

#conversion bmp uncompressed
for bmp in bmp_list:
	if os.path.isfile(bmp):
		os.system("magick "+bmp+" -compress none "+bmp)
		print(bmp +" uncompressed")