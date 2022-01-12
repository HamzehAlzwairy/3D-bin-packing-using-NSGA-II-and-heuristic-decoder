class Container(object):
    def __init__(self, w, h, d):
        self.boxes = []
        self.width = w
        self.height = h
        self.depth = d
        self.volume = w * h * d
        self.bottom_left_coordinates = (0, 0, 0)
        self.upper_right_coordinates = (self.width, self.height, self.depth)

    def get_coordinates(self):
        return self.bottom_left_coordinates, self.upper_right_coordinates

    def add_box(self, box):
        self.boxes.append(box)

    def get_packed_volume(self):
        volume = 0
        for box in self.boxes:
            volume += box.volume
        return volume

    def get_container_faces(self):
        vertices = []
        x, z, y = self.bottom_left_coordinates
        X, Z, Y = self.upper_right_coordinates
        vertices.append((x, y, z))
        vertices.append((x, Y, z))
        vertices.append((X, Y, z))
        vertices.append((X, y, z))
        vertices.append((X, y, Z))
        vertices.append((x, y, Z))
        vertices.append((x, Y, Z))
        vertices.append((X, Y, Z))
        self.vertices = vertices
        faces = [[self.vertices[0], self.vertices[1], self.vertices[2], self.vertices[3]],
                     [self.vertices[4], self.vertices[5], self.vertices[6], self.vertices[7]],
                     [self.vertices[3], self.vertices[4], self.vertices[7], self.vertices[2]],
                     [self.vertices[1], self.vertices[6], self.vertices[7], self.vertices[2]],
                     [self.vertices[0], self.vertices[1], self.vertices[6], self.vertices[5]],
                     [self.vertices[0], self.vertices[5], self.vertices[4], self.vertices[3]]]
        return faces