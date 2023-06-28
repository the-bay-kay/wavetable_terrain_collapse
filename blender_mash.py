#!/usr/bin/python3
import bpy
from enum import Enum
import random
import time 

SCALE_FACTOR = 30.0
class Height(Enum):
    HI = 76
    MH = 30
    ME = 24
    ML = 12
    LO = 6

HEIGHT_UNIT = 6
'''
class Height(Enum):
    HI = 135
    MH = 108
    ME = 81
    ML = 54
    LO = 27 
'''
HEIGHT_UNIT = 27
TYPE_TOTAL = 5
TYPE_SET = set([Height.HI, Height.MH, Height.ME, Height.ML, Height.LO])
TYPE_COMPATABILITIES = {
    Height.HI: set([Height.HI, Height.MH, Height.ML]),
    Height.MH: set([Height.HI, Height.MH, Height.ME]),
    Height.ME: set([Height.MH, Height.ME, Height.ML, Height.LO]),
    Height.ML: set([Height.HI, Height.ME, Height.ML, Height.LO]),
    Height.LO: set([Height.ME, Height.ML, Height.LO])
}
DEFAULT_ENTROPY = 0.0
COLLAPSED = -1.0

class TileObj:
    def __init__(self, id):
        self.id = id # Hi, MH, M, ML, L
        self.generated_height = id.value - random.randint(0, HEIGHT_UNIT)

    def __str__(self) -> str:
        return "(" + str(self.generated_height) + ")" 

    def __repr__(self):
        return self.id
    
    def get_height(self):
        return self.generated_height
# 
class TileContainer:
    def __init__(self, x_coord, y_coord):
        self.tile_obj = None 

        self.x_coord = x_coord
        self.y_coord = y_coord

        self.potential_types = TYPE_SET.copy() 
        self.entropy = DEFAULT_ENTROPY

    def __str__(self) -> str:
        return "X: " + str(self.x_coord) + " Y: " + str(self.y_coord) + " " + str(self.tile_obj)

    def is_collapsed(self):
        return self.tile_obj is not None

    def type_abbreviations(self) -> str:
        out_str = "["
        for i in self.potential_types:
            out_str += i.name[0] + i.name[1] + '|'
        out_str = out_str[:-1] + "]" #+ str(self.entropy)
        return out_str

    # For each potential type, get the compatable types and add them to a set
    def get_sockets(self):
        sockets = set()
        for tile_type in self.potential_types:
            sockets.update(TYPE_COMPATABILITIES[tile_type])
        return sockets

    def update_types(self, type_set):
        self.potential_types = self.potential_types.intersection(type_set)
        self.entropy = 1 - len(self.potential_types) / TYPE_TOTAL;

    # specific tile can be given, otherwise perform entropy collapse 
    def collapse_container(self, tile_obj = None):
        if tile_obj is not None:
            self.tile_obj = tile_obj
        else:
            self.tile_obj = TileObj(random.choice(list(self.potential_types)))
        self.potential_types = set([self.tile_obj.id])
        self.entropy = COLLAPSED 

class WaveTable:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.table_matrix = [[0]*width for i in range(height)] # 2d array of TileContainers, template
        for i in range(height):
            for j in range(width):
                self.table_matrix[i][j] = TileContainer(i, j)


    def __str__(self) -> str:
        buffer = "+=+=+=+=+=+=+=+=+=+=+=+=+"
        out_str = ""
        for i in range(len(self.table_matrix)):
            for j in range(len(self.table_matrix[i])):
                cur_tile = self.table_matrix[i][j].tile_obj
                if cur_tile is not None:
                    out_str += str(cur_tile) + ' '
                else:
                    out_str += self.table_matrix[i][j].type_abbreviations() + ' '
            out_str += '\n'
        return buffer + '\n' + out_str

    def find_neighbors(self, x_coord, y_coord):
        neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if x_coord + i >= 0 and x_coord + i < len(self.table_matrix) and y_coord + j >= 0 and y_coord + j < len(self.table_matrix[0]):
                    neighbors.append(self.table_matrix[x_coord + i][y_coord + j])
        return set(neighbors)

    def seed_tile(self, x_coord, y_coord, tile_obj):
        self.table_matrix[x_coord][y_coord].collapse_container(tile_obj)

    # one iteration of wave collapse, starts from seed coords and propegates outwards.
    def wave_collapse(self, x_coord, y_coord, tile_obj = None):
        self.table_matrix[x_coord][y_coord].collapse_container(tile_obj)

        queue = self.find_neighbors(x_coord, y_coord)
        highest_entropy = COLLAPSED # used to determin next tile to collapse
        next_tile = None
        
        while len(queue) != 0:
            curr = queue.pop()
            if curr.is_collapsed():
                continue
            else:
                neighbors = self.find_neighbors(curr.x_coord, curr.y_coord)
                new_potential_types = curr.potential_types.copy() # set of potential types for neighbors
                for neighbor in neighbors:
                   new_potential_types = new_potential_types.intersection(neighbor.get_sockets())
                old_set = curr.potential_types.copy()
                curr.update_types(new_potential_types) 
                if old_set != curr.potential_types: # if a change was made, add neighbors to be checked 
                    queue.update(neighbors)
                    # If no more options, collapse!
                    if len(curr.potential_types) == 1:
                        curr.collapse_container()
                    # If updated, check if it is the highest entropy tile
                if curr.entropy > highest_entropy:
                    highest_entropy = curr.entropy
                    next_tile = curr
        return next_tile
        
    def wave_table_collapse(self, x_coord = 0, y_coord = 0, tile_obj = None, print_table = False):
        # if given a seed coord, seed the table: otherwise, randomly select a seed coord
        next_tile = None
        if x_coord != 0 or y_coord != 0 or tile_obj is not None:
            next_tile = self.wave_collapse(x_coord, y_coord, tile_obj)
        else:
            x_coord = random.randint(0, len(self.table_matrix) - 1)
            y_coord = random.randint(0, len(self.table_matrix[0]) - 1)
            next_tile = self.wave_collapse(x_coord, y_coord)
        if next_tile == None: # 1x1 table, no need to continue
            return
        if(print_table): print(self)
        count = 1
        while True:
            if next_tile == None:
                for i in range(len(self.table_matrix)):
                    for j in range(len(self.table_matrix[i])):
                        if not self.table_matrix[i][j].is_collapsed():
                            next_tile = self.table_matrix[i][j]
                            break
                if next_tile is None:
                    print("Done generating table!") 
                    return

            next_tile = self.wave_collapse(next_tile.x_coord, next_tile.y_coord)
            if(print_table): print(self)
            count += 1
            #print(count, end = ' ')
        if(print_table): print(self)

    def table_to_matrix(self):
        out_matrix = [[0]*self.width for i in range(self.height)] # 2d array of TileContainers, template
        for i in range(len(self.table_matrix)):
            for j in range(len(self.table_matrix[i])):
                out_matrix[i][j] = self.table_matrix[i][j].tile_obj.get_height()
        return out_matrix


# Beginning of 'Blender Pipe', what we care about for the socket

# generates & collapses a table, then converts it to a simple height value matrix
def generate_table_values(print_debug=False):
    terrain_table = WaveTable(15,15) 
    terrain_table.wave_table_collapse(print_table = print_debug)
    if print_debug: print('Debug\n', terrain_table)
    return terrain_table.table_to_matrix()


# converts a height value matrix to a coordinate matrix
def height_to_coordinates(matrix, scale = 1):
    coord_array= []
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            coord_array.append((i * scale, j * scale, matrix[i][j]))
    return coord_array 

class TerrainObj:
    # vert_coords: (x,y,z) tuples
    # face_tuples: (a,b,c,d) tuples | a,b,c,d are indices of the vert_coords array
    def __init__(self, matrix, scale, coord_noise = False):
        row_size = len(matrix) # M in test code
        column_size = len(matrix[0]) # N in test code

        coord_array = []
        face_array = []
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                x_val = i * scale
                y_val = j * scale
                if coord_noise:
                    x_val += random.uniform(-0.5, 0.5)
                    y_val += random.uniform(-0.5, 0.5)
                coord_array.append((x_val, y_val, matrix[i][j]))
                #print(len(coord_array) - 1, (i, j, matrix[i][j]))
        self.vert_coords = coord_array 
        for i in range(0, row_size-1, 1):
            for j in range(0, column_size-1, 1):
                new_face = (i*column_size + j, i*column_size + j + 1, (i+1)*column_size + j + 1, (i+1)*column_size + j)
                print(new_face)
                #print(coord_array[j], coord_array[j+1], coord_array[i+column_size], coord_array[i+column_size+1])
                face_array.append(new_face)
        self.face_tuples = face_array

def generate_mesh(terrain_obj):
    mesh = bpy.data.meshes.new("Heightmap_Mesh")    
    blend_obj = bpy.data.objects.new("Heightmap", mesh)
    mesh.from_pydata(terrain_obj.vert_coords, [], terrain_obj.face_tuples)
    #mesh.from_pydata(terrain_obj.vert_coords, [], [])

    blend_obj.show_name = True
    mesh.update()
    return blend_obj



def main():
    values = generate_table_values()
    # terrain = TerrainObj(values, SCALE_FACTOR)
    terrain = TerrainObj(values, SCALE_FACTOR, coord_noise = True)
    point_object = generate_mesh(terrain)

    bpy.context.scene.collection.objects.link(point_object)


if __name__ == '__main__':
    main()