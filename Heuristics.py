import copy
from EMS import *


def placement_heuristic(box, EMSs):
    feasibleEMSs = []  # an EMS is feasible if the box fits inside it
    for ems in EMSs:
        # for every EMS rotate the box again? Box is oriented len(EMSs) times with 1 or 2 ..
        fits = try_fit(ems, box)
        if fits:
            feasibleEMSs.append(ems)

    # if non of the EMSs fit the box, this means open a new container
    if not feasibleEMSs:
        return -1
    selectedEMS = select_ems(feasibleEMSs)
    # placement heuristic is back bottom left coordinate, can be changed
    box.pack_box(selectedEMS.bottom_left_coordinates)
    # successfully packed
    return 0


def update_EMSs(EMSs, box):
    updated_EMSs = []
    box_x_period = (box.bottom_left_coordinates[0], box.upper_right_coordinates[0])
    box_y_period = (box.bottom_left_coordinates[1], box.upper_right_coordinates[1])
    box_z_period = (box.bottom_left_coordinates[2], box.upper_right_coordinates[2])

    for ems in EMSs:
        ems_x_period = (ems.bottom_left_coordinates[0], ems.upper_right_coordinates[0])
        ems_y_period = (ems.bottom_left_coordinates[1], ems.upper_right_coordinates[1])
        ems_z_period = (ems.bottom_left_coordinates[2], ems.upper_right_coordinates[2])

        x1_intersection, x2_intersection = check_intersection(ems_x_period, box_x_period)
        if x1_intersection is None or x2_intersection is None:
            # no intersection with this ems, keep it without modification
            updated_EMSs.append(ems)
            continue

        y1_intersection, y2_intersection = check_intersection(ems_y_period, box_y_period)
        if y1_intersection is None or y2_intersection is None:
            # no intersection with this ems, keep it without modification
            updated_EMSs.append(ems)
            continue

        z1_intersection, z2_intersection = check_intersection(ems_z_period, box_z_period)
        if z1_intersection is None or z2_intersection is None:
            # no intersection with this ems, keep it without modification
            updated_EMSs.append(ems)
            continue

        new_EMSs = create_EMSs(ems.bottom_left_coordinates, ems.upper_right_coordinates,
                               (x1_intersection, y1_intersection, z1_intersection),
                               (x2_intersection, y2_intersection, z2_intersection))
        updated_EMSs.extend(new_EMSs)

    return updated_EMSs


def remove_invalid_EMSs(EMSs, remaining_boxes):
    indices_to_discard = []
    for i, ems in enumerate(EMSs):
        discard = True
        for j, box in enumerate(remaining_boxes):
            # If the volume of a newly created EMS is smaller than the volume of each of the boxes
            # remaining to be packed then discard it, it doesn't fit any remaining box
            # if the dimensions of the ems do not fit at least 1 remaining box then discard it
            if ems.volume >= box.volume:
                if try_fit(ems, box):
                    # move on to next ems as this ems shouldn't be discarded
                    discard = False
                    break
        if discard:
            indices_to_discard.append(i)
    # we need to delete in a reversed manner so that the indices of next items to delete doesn't change
    for i in sorted(indices_to_discard, reverse=True):
        del EMSs[i]
    indices_to_discard = []
    # remove every ems that is fully inscribed within another ems ( duplicated empty space )
    for i, target_ems in enumerate(EMSs):
        for ems in EMSs:
            # if (x1>x3) and (y1 >ty3) and (z1>z3) and (x2~<x4) and (y2~<y4) and
            # (z2 ~< z4). then ems (x1,y1,z1)(x2,y2,z2) is inscribed within ems
            # (x3,y3,z3)(x4,y4,z4) so remove it.
            if target_ems is ems:
                continue
            if target_ems.bottom_left_coordinates[0] >= ems.bottom_left_coordinates[0] and \
                    target_ems.bottom_left_coordinates[1] >= ems.bottom_left_coordinates[1] and \
                    target_ems.bottom_left_coordinates[2] >= ems.bottom_left_coordinates[2] and \
                    target_ems.upper_right_coordinates[0] <= ems.upper_right_coordinates[0] and \
                    target_ems.upper_right_coordinates[1] <= ems.upper_right_coordinates[1] and \
                    target_ems.upper_right_coordinates[2] <= ems.upper_right_coordinates[2]:
                indices_to_discard.append(i)
                break
    for i in sorted(indices_to_discard, reverse=True):
        del EMSs[i]

    return EMSs


def create_EMSs(ems_bottom_left_coordinates, ems_upper_right_coordinates, intersection_bottom_left_coordinates,
                intersection_upper_right_coordinates):
    new_EMSs = []
    # ems create to the left of the intersection = (x1, y1, z1)(x3, y2, z2) where 1,2 coordinates are for the ems
    # and the 3,4 coordinates are for the box
    ems_left = EMS(ems_bottom_left_coordinates, (intersection_bottom_left_coordinates[0],
                                                 ems_upper_right_coordinates[1], ems_upper_right_coordinates[2]))

    # ems to the right of the intersection = (x4, y1, z1)(x2, y2, z2)
    ems_right = EMS((intersection_upper_right_coordinates[0], ems_bottom_left_coordinates[1],
                     ems_bottom_left_coordinates[2]), ems_upper_right_coordinates)

    # ems created above the intersection = (x1, y4, z1)(x2, y2, z2)
    ems_above = EMS((ems_bottom_left_coordinates[0], intersection_upper_right_coordinates[1],
                     ems_bottom_left_coordinates[2]), ems_upper_right_coordinates)

    # ems created under the intersection = (x1, y1, z1)(x2, y3, z2)
    ems_under = EMS(ems_bottom_left_coordinates,
                    (ems_upper_right_coordinates[0], intersection_bottom_left_coordinates[1],
                     ems_upper_right_coordinates[2]))

    # ems created before the intersection = (x1, y1, z1)(x2, y2, z3)
    ems_before = EMS(ems_bottom_left_coordinates,
                     (ems_upper_right_coordinates[0], ems_upper_right_coordinates[1],
                      intersection_bottom_left_coordinates[2]))

    # ems created after the intersection = (x1, y1, z4)(x2, y2, z2)
    ems_after = EMS((ems_bottom_left_coordinates[0], ems_bottom_left_coordinates[1],
                     intersection_upper_right_coordinates[2]), ems_upper_right_coordinates)

    new_EMSs.append(ems_left)
    new_EMSs.append(ems_right)
    new_EMSs.append(ems_above)
    new_EMSs.append(ems_under)
    new_EMSs.append(ems_before)
    new_EMSs.append(ems_after)

    return new_EMSs


def select_ems(EMSs):
    selectedEMS = None
    for ems in EMSs:
        if selectedEMS is None:
            selectedEMS = ems
            continue
        # choose ems with the deepest z
        if ems.bottom_left_coordinates[2] < selectedEMS.bottom_left_coordinates[2]:
            selectedEMS = ems
            continue
        # when z coordinates are equal, choose deepest y
        if ems.bottom_left_coordinates[2] == selectedEMS.bottom_left_coordinates[2]:
            if ems.bottom_left_coordinates[1] < selectedEMS.bottom_left_coordinates[1]:
                selectedEMS = ems
                continue
            # if heights are also equal, choose deepest x
            # not possible to get all coordinates equal as this ems would
            # have been removed earlier ( considered inscribed within another ems )
            if ems.bottom_left_coordinates[1] == selectedEMS.bottom_left_coordinates[1]:
                if ems.bottom_left_coordinates[0] < selectedEMS.bottom_left_coordinates[0]:
                    selectedEMS = ems
                    continue

    return selectedEMS


def check_intersection(ems_axis_period, box_axis_period):
    axis1_intersection = None
    axis2_intersection = None
    # box axis (left and right, e.g x1, x2 ) period inscribed within ems axis period (e.g x3<= x1,x2 <=x4)
    if ems_axis_period[0] < box_axis_period[1] <= ems_axis_period[1] and ems_axis_period[0] <= box_axis_period[0] < \
            ems_axis_period[1]:
        axis1_intersection = box_axis_period[0]
        axis2_intersection = box_axis_period[1]
    # ems axis period is inscribed within the box axis period
    elif box_axis_period[0] < ems_axis_period[1] <= box_axis_period[1] and box_axis_period[0] <= ems_axis_period[0] < \
        box_axis_period[1]:
        axis1_intersection = ems_axis_period[0]
        axis2_intersection = ems_axis_period[1]
    # axis1 (left, e.g x1) of the box lies in the ems axis period (intersects with it)
    elif ems_axis_period[0] <= box_axis_period[0] < ems_axis_period[1]:
        axis1_intersection = box_axis_period[0]
        axis2_intersection = ems_axis_period[1] if ems_axis_period[1] < box_axis_period[1] else box_axis_period[1]
    # axis2 (right, e.g x2) of the box lies in the ems axis period (intersects with it)
    elif ems_axis_period[0] < box_axis_period[1] <= ems_axis_period[1]:
        axis1_intersection = ems_axis_period[0] if box_axis_period[0] < ems_axis_period[0] else box_axis_period[0]
        axis2_intersection = box_axis_period[1]

    return axis1_intersection, axis2_intersection


def try_fit(ems, box):
    # check if the box fits in the ems
    if ems.width >= box.width and \
            ems.height >= box.height \
            and ems.depth >= box.depth:
        return True
    else:
        return False


def rotate(box):
    # no rotation
    if box.orientation == 0:
        pass
    # rotation 1 ( front and back faces become bottom and top, so we swap dimensions accordingly )
    if box.orientation == 1:
        height = box.height
        box.height = box.depth
        box.depth = height

    # rotation 2 ( the side faces become top and bottom)
    if box.orientation == 2:
        height = box.height
        box.height = box.width
        box.width = height
