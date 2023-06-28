# A Blender Terrain Generator
A Terrain Generation Script for blender, written utalizing a version of the [Wave Function Collapse Algorithm](https://en.wikipedia.org/wiki/Wave_function_collapse)
![Tiled terrain mesh, inside a Blender Project](https://raw.githubusercontent.com/the-bay-kay/wavetable_terrain_collapse/main/example.png)
## How To Run
(This has been tested on Linux only!  Will test on Windows eventually)
1. Modify the blender_socket.py file, such that the USER and LOCATION_OF_SCRIPT strings match the current user and the path of the script.
2. Open a Blender Project, and use the Text Editor to open blender_socket.py
3. After opening the script, run in order to generate the terrain!

## What (And Why) is this project?
After watching [Martin Donald's video](https://www.youtube.com/watch?v=2SuvO4Gi7uY) on the ways that wave function collapse algorithms can be used for video game development, I wanted to try my own hand at implementing terrain generation!  This code is working, 
but far from "production quality" - there is no GUI, parameters need to be manipulated in the code itself,
and execution relies on a helper script.  It's a good proof of concept - if I have time in the future, I'll clean this up! 
