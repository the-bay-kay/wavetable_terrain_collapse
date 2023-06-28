#!/usr/bin/python3
import bpy
import os

USER = '/home/lauraipsum'

LOCATION_OF_SCRIPT = '/Documents/'

PATHSTR = USER + LOCATION_OF_SCRIPT

filename = os.path.join(PATHSTR, "blender_mash.py")
exec(compile(open(filename).read(), filename, 'exec'))