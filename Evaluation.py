def SpacePenality(containers):
    penality = len(containers) + containers[-1].get_packed_volume() / containers[-1].volume
    return round(penality, 3)

def PriorityPenality(individual, boxes):
    totalPriorityPenality = 0
    for i in range(len(boxes)):
        box = next(x for x in boxes if x.ID == individual[i])
        totalPriorityPenality += abs(box.priority-i)/len(boxes)
    return round(totalPriorityPenality / len(boxes), 3)


def WeightFitness(containers):
    global totalWeightFitness

    totalWeightFitness = 0

    ifBoxtop = False

    topTotalWeight = 0

    retrio = 0

    numberoftotalboxes = 0

    # this part is checking all the boxes bove for each boxes and divide the bottom one

    # and then I will get a retrio of each boxes and add them all together

    # the final weight fintness will be the average retrio of weight in this selutions

    # and this is already being test out and we are trying to find the minimum average retrio

    for i in range(len(containers)):

        # print("container " + str(i))

        for k in range(len(containers[i].boxes)):

            topTotalWeight = 0

            numberoftotalboxes += 1

            for j in range(len(containers[i].boxes)):

                # print("fdafa " +str(containers[i].boxes[j].bottom_left_coordinates[1]))

                if (int(containers[i].boxes[j].bottom_left_coordinates[1]) in range(
                        int(containers[i].boxes[k].upper_right_coordinates[1]), int(containers[i].height))

                        and int(containers[i].boxes[j].bottom_left_coordinates[2]) in range(
                            int(containers[i].boxes[k].bottom_left_coordinates[2]),
                            int(containers[i].boxes[k].upper_right_coordinates[2]))

                        and int(containers[i].boxes[j].bottom_left_coordinates[0]) in range(
                            int(containers[i].boxes[k].bottom_left_coordinates[0]),
                            int(containers[i].boxes[k].upper_right_coordinates[0]))):

                    if (j == k):

                        pass

                    else:

                        ifBoxtop = True

                else:

                    ifBoxtop = False

                if (ifBoxtop == True):
                    topTotalWeight += containers[i].boxes[j].weight

            retrio = topTotalWeight / containers[i].boxes[k].weight

            totalWeightFitness += retrio

            # print(ifBoxtop)

            # print (totalWeightFitness)

    totalWeightFitness = totalWeightFitness / numberoftotalboxes

    return totalWeightFitness