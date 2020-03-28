# Nuthouse01 - 03/14/2020 - v3.01
# This code is free to use and re-distribute, but I cannot be held responsible for damages that it may or may not cause.
#####################

import sys
# first, version check: verify that this is using python3
# i don't know if it will actually work in 3.4 but i know it will fail in any python2 version
# actually written/tested with 3.6.6 so guaranteed to work on that or higher
# between 3.4 and 3.6, who knows
if sys.version_info < (3, 4):
	print("Your version of Python is too old to run this script, please update!")
	print("Your current version = " + sys.version)
	print("...press ENTER to exit...")
	input()
	exit()

# second, wrap custom imports with a try-except to catch it if files are missing
try:
	import nuthouse01_core as core
	import nuthouse01_pmx_parser as pmxlib
except ImportError as eee:
	print(eee)
	print("ERROR: failed to import some of the necessary files, all my scripts must be together in the same folder!")
	print("...press ENTER to exit...")
	input()
	exit()
	core = pmxlib = None


# when debug=True, disable the catchall try-except block. this means the full stack trace gets printed when it crashes,
# but if launched in a new window it exits immediately so you can't read it.
DEBUG = False


# just take a wild guess what this field controls
PRINT_AFFECTED_MORPHS = True


# opacity, edge size, edge alpha
#template = [0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
# opacity, edge size, edge alpha, tex, toon, sph
template = [0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0]


def begin():
	# print info to explain the purpose of this file
	print("This file fixes improper 'material hide' morphs in a model.")
	print("Many models simply set the opacity to 0, but forget to zero out the edging effects or other needed fields.")
	# print info to explain what inputs it needs
	print("Inputs: PMX file 'model.pmx'")
	# print info to explain what outputs it creates
	print("Outputs: PMX file '[model]_alphamorph.pmx'")
	print("")
	
	# prompt PMX name
	print("Please enter name of PMX model file:")
	input_filename_pmx = core.prompt_user_filename(".pmx")
	pmx = pmxlib.read_pmx(input_filename_pmx)
	return pmx, input_filename_pmx

def alphamorph_correct(pmx):
	num_fixed = 0
	total_morphs_affected = 0
	
	# for each morph:
	for morph in pmx[6]:
		# if not a material morph, skip it
		if morph[3] != 8:
			continue
		this_num_fixed = 0
		# for each material in this material morph:
		for mat in morph[4]:
			# (mat_idx, is_add, diffR, diffG, diffB, diffA, specR, specG, specB, specpower, ambR, ambG, ambB, edgeR,
			# edgeG, edgeB, edgeA, edgesize, texR, texG, texB, texA, sphR, sphG, sphB, sphA, toonR, toonG, toonB, toonA)
			# is_add=1, diffA(opacity)=5, edgeA=16, edgesize=17, texA=21, sphA=25, toonA=29
			# if (mult opacity by 0) OR (add -1 to opacity)
			# opacity, edge size, edge alpha, tex, toon, sph
			if (mat[1]==0 and mat[5]==0) or (mat[1]==1 and mat[5]==-1):
				# then replace the entire set of material-morph parameters
				before = list(mat)  # make a copy
				mat[1:] = template  # write into the structure
				if before != mat:   # see if it actually changed
					this_num_fixed += 1
		if this_num_fixed != 0:
			total_morphs_affected += 1
			num_fixed += this_num_fixed
			if PRINT_AFFECTED_MORPHS:
				print("JP: '%s' --- EN: '%s'" % (morph[0], morph[1]))
	
	if num_fixed == 0:
		print("No changes are required")
		return pmx, False
	
	print("Fixed %d locations from among %d affected morphs" % (num_fixed, total_morphs_affected))
	return pmx, True

def end(pmx, input_filename_pmx):
	# write out
	output_filename_pmx = "%s_alphamorph.pmx" % core.get_clean_basename(input_filename_pmx)
	# output_filename_pmx = input_filename_pmx[0:-4] + "_translate.pmx"
	output_filename_pmx = core.get_unused_file_name(output_filename_pmx)
	pmxlib.write_pmx(pmx, output_filename_pmx)
	
	return None

def main():
	pmx, name = begin()
	pmx, is_changed = alphamorph_correct(pmx)
	if is_changed:
		end(pmx, name)
	core.pause_and_quit("Done with everything! Goodbye!")

if __name__ == '__main__':
	print("Nuthouse01 - 03/14/2020 - v3.01")
	if DEBUG:
		main()
	else:
		try:
			main()
		except (KeyboardInterrupt, SystemExit):
			# this is normal and expected, do nothing and die normally
			pass
		except Exception as ee:
			# if an unexpected error occurs, catch it and print it and call pause_and_quit so the window stays open for a bit
			print(ee)
			core.pause_and_quit("ERROR: something truly strange and unexpected has occurred, sorry, good luck figuring out what tho")