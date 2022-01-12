import numpy as np
class Box(object):
    def __init__(self, id, w, h, d, orientation, priority):
        self.ID = id
        self.width = w
        # Swapped because matplotlib considers y as depth and z as height.
        # We would like to receive x,y,z as w,h,d, respectively.
        self.height = h
        self.depth = d
        self.orientation = orientation
        self.volume = w * h * d
        self.priority = priority
        self.color = np.random.choice(['b', 'g', 'r', 'c', 'm', 'y', 'k', '#FF6000', '#43FF00', '#FCFF00', '#8400FF', '#0095FF', '#603702',
                  '#8B8B8B'])
    # used to pack box inside the bins after the EMS operation
    def pack_box(self, min_coord):
        self.bottom_left_coordinates = min_coord
        # if our bottom_left is (1,1,1) and w,h,d are 5,5,5 we our maximum coordinates(top right of the box) are (6,6,6)
        self.upper_right_coordinates = (min_coord[0] + self.width, min_coord[1] + self.height, min_coord[2] + self.depth)
        self.vertices = self.get_vertices()

    def set_priority(self, priority):
        self.priority = priority

    def get_vertices(self):
        vertices = []
        x, z, y = self.bottom_left_coordinates
        X, Z, Y= self.upper_right_coordinates
        vertices.append((x, y, z))
        vertices.append((x, Y, z))
        vertices.append((X, Y, z))
        vertices.append((X, y, z))
        vertices.append((X, y, Z))
        vertices.append((x, y, Z))
        vertices.append((x, Y, Z))
        vertices.append((X, Y, Z))
        return vertices

    def get_box_faces(self):
        faces = [[self.vertices[0], self.vertices[1], self.vertices[2], self.vertices[3]],
                     [self.vertices[4], self.vertices[5], self.vertices[6], self.vertices[7]],
                     [self.vertices[3], self.vertices[4], self.vertices[7], self.vertices[2]],
                     [self.vertices[1], self.vertices[6], self.vertices[7], self.vertices[2]],
                     [self.vertices[0], self.vertices[1], self.vertices[6], self.vertices[5]],
                     [self.vertices[0], self.vertices[5], self.vertices[4], self.vertices[3]]]
        return faces