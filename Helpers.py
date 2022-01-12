import numpy as np
from Heuristics import *
from Container import *
from Box import *


class Helper(object):
    def __init__(self, container_width, container_height, container_depth):
        self.container_width = container_width
        self.container_height = container_height
        self.container_depth = container_depth

    def create_boxes(self, n):
        boxes = []
        possible_widths = [self.container_width * 0.75, 60, 50, 40, 30, 20, 10]
        possible_heights = [self.container_height * 0.75, 60, 50, 40, 30, 20, 10]
        possible_depths = [self.container_depth * 0.50, 60, 50, 40, 30, 20, 10]
        priorities = [*range(n)]
        np.random.shuffle(priorities)
        for i in range(n):
            w = np.random.choice(possible_widths, p=[0.05, 0.08, 0.11, 0.19, 0.19, 0.19, 0.19])
            h = np.random.choice(possible_heights, p=[0.05, 0.08, 0.11, 0.19, 0.19, 0.19, 0.19])
            d = np.random.choice(possible_depths, p=[0.05, 0.08, 0.11, 0.19, 0.19, 0.19, 0.19])
            # keep the boxes on 0 orientation for reference when applying orientation.
            boxes.append(Box(i + 1, w, h, d, 0, priorities[i]))
        return boxes

    @staticmethod
    def create_individual(boxes):
        np.random.shuffle(boxes)
        ids = [b.ID for b in boxes]
        orientations = [np.random.choice([0, 1, 2]) for b in boxes]
        ids.extend(orientations)
        return ids

    def pack_solution(self, individual, remaining_boxes):
        containers = []
        orientation_chromosome = individual[len(remaining_boxes):]

        # this for the purpose of saving computational cost when applying remove_invalid_EMSs
        remaining_order = copy.deepcopy(individual[:len(remaining_boxes)])

        for i in range(len(remaining_order)):
            box = next(x for x in remaining_boxes if x.ID == remaining_order[i])
            box.orientation = orientation_chromosome[i]
            rotate(box)

        while len(remaining_boxes) > 0:
            indices_to_discard = []
            # basically each round in the while loop is a new container
            container = Container(self.container_width, self.container_height, self.container_depth)

            # initial EMS is same dimensions as the container
            coordinates = container.get_coordinates()
            EMSs = [EMS(coordinates[0], coordinates[1])]

            # if I use remaining_order for looping, it will result in error since im removing elements from it
            reference_remaining_order = copy.deepcopy(remaining_order)

            for i, boxID in enumerate(reference_remaining_order):
                box = next(x for x in remaining_boxes if x.ID == boxID)
                result = placement_heuristic(box, EMSs)
                if result == -1:
                    # this box doesn't fit in an ems, skip to next box
                    continue
                container.add_box(box)
                remaining_boxes.remove(box)
                remaining_order.remove(box.ID)
                indices_to_discard.append(i)

                updated_EMSs = update_EMSs(EMSs, box)
                # remove infinitely thin EMSs ( one of it's dimensions is 0 now )
                # and remove EMSs totally inscribed within other EMSs ( duplicated )
                EMSs = remove_invalid_EMSs(updated_EMSs, remaining_boxes)

            # orientations are not unique, so I have to pop them by index rather than ID
            for i in sorted(indices_to_discard, reverse=True):
                del orientation_chromosome[i]

            containers.append(container)
        return containers
