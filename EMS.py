class EMS(object):
    def __init__(self, bottom_left_coordinates, upper_right_coordinates):
        self.bottom_left_coordinates = bottom_left_coordinates
        self.upper_right_coordinates = upper_right_coordinates
        self.width = upper_right_coordinates[0] - bottom_left_coordinates[0]
        self.height = upper_right_coordinates[1] - bottom_left_coordinates[1]
        self.depth = upper_right_coordinates[2] - bottom_left_coordinates[2]
        self.volume = self.width * self.height * self.depth
