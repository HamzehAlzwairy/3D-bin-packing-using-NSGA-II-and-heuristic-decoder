from Helpers import *
from Visualization import *
from deap import creator, algorithms, tools, base
from Evaluation import SpacePenality, PriorityPenality, WeightFitness
import random

# Could not find a way to stop the animation over write, but you can get the graph while the program is running


global boxNumber
global boxes
global helper


def main():
    # global variables
    global helper
    global boxes
    # helper = Helper(110, 110, 200)
    # boxes = helper.create_boxes(120)
    # must be divisible by 4, or nsga2 selection from deap will crash
    population_size = 32
    generations = 2
    CXPB = 0.65
    shufflePB = 0.25
    bitFlipPB = 0.25
    hallOfFame = []
    hallOfShame = []

    creator.create("Fitness", base.Fitness, weights=(-1.0, -1.0))
    creator.create("Individual", list, fitness=creator.Fitness)

    toolbox = base.Toolbox()
    toolbox.register("expression", Helper.create_individual, boxes)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expression)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("mutate_ids", tools.mutShuffleIndexes, indpb=shufflePB)
    toolbox.register("mate_ids", cxCutAndCrossFill)

    toolbox.register("mutate_orientations", mutate_orientations, indpb=bitFlipPB)
    toolbox.register("mate_orientations", tools.cxTwoPoint)

    toolbox.register("select", tools.selNSGA2)
    toolbox.register("evaluate", EvaluateIndividual)

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("minimum penality", np.min, axis=0)
    stats.register("maximum penality", np.max, axis=0)

    logbook = tools.Logbook()
    logbook.header = "gen", "evals", "minimum penality", "maximum penality"

    pop = toolbox.population(population_size)
    for individual in pop:
        containers = helper.pack_solution(individual, copy.deepcopy(boxes))
        toolbox.evaluate(individual, boxes, containers)

    # In DEAP, crowding distance is assigned within this function and it is not available out of the box. So, we call
    # this function while making sure it returns the same population but with crowding_dist attribute assigned
    pop = toolbox.select(pop, len(pop))

    # ---------------------------------------------------------------------------------
    hallOfShame.append(GetWorstIndividual(pop))
    hallOfFame.append(GetBestIndividual(pop))
    # -------------------------------------------------------------------------------

    record = stats.compile(pop)
    logbook.record(gen=0, evals=len(pop), **record)
    print(logbook.stream)

    for generation in range(generations):
        # create parent population by applying TS(R,CD)
        offspring = tools.selTournamentDCD(pop, len(pop))
        offspring = [toolbox.clone(ind) for ind in offspring]
        offspring = create_offspring_population(offspring, toolbox, CXPB)

        evaluations = 0
        # evaluate new individuals
        for individual in offspring:
            if not individual.fitness.valid:
                evaluations += 1
                containers = helper.pack_solution(individual, copy.deepcopy(boxes))
                toolbox.evaluate(individual, boxes, containers)

        # Apply NSGA-II selection, it should do non dominated sorting to pareto fronts then find crowding distance
        #  for each individual and finally select new population using rank and crowding distance TS
        pop.extend(offspring)
        pop = toolbox.select(pop, population_size)
        record = stats.compile(pop)
        logbook.record(gen=generation, evals=evaluations, **record)
        print(logbook.stream)

        # ------------------------------------------------------------------------------------
        # change this when try to run one single Fitness Using the function at below
        # between two ---------------- lines
        # if want to do two again using the original function
        hallOfShame.append(GetWorstIndividual(pop))
        hallOfFame.append(GetBestIndividual(pop))

        # -----------------------------------------------------------------------------------

    return pop, logbook, hallOfFame, hallOfShame


def EvaluateIndividual(individual, boxes, containers):
    spaceFitness = SpacePenality(containers)
    priorityFitness = PriorityPenality(individual, boxes)
    individual.fitness.values = spaceFitness, priorityFitness


# -------------------------------------------------------------------------------------------------------
def GetBestSpace(pop):
    best_individual = None
    for ind in pop:
        if best_individual is None:
            best_individual = ind
            continue
        if ind.fitness.values[0] < best_individual.fitness.values[0]:
            best_individual = ind
    return copy.deepcopy(best_individual)


def GetBestPriority(pop):
    best_individual = None
    for ind in pop:
        if best_individual is None:
            best_individual = ind
            continue
        if ind.fitness.values[1] < best_individual.fitness.values[1]:
            best_individual = ind
    return copy.deepcopy(best_individual)


def GetWorstSpace(pop):
    worst_individual = None
    for ind in pop:
        if worst_individual is None:
            worst_individual = ind
            continue
        if ind.fitness.values[0] > worst_individual.fitness.values[0]:
            worst_individual = ind
    return copy.deepcopy(worst_individual)


def GetWorstPriority(pop):
    worst_individual = None
    for ind in pop:
        if worst_individual is None:
            worst_individual = ind
            continue
        if ind.fitness.values[1] > worst_individual.fitness.values[1]:
            worst_individual = ind
    return copy.deepcopy(worst_individual)


# -------------------------------------------------------------------------------------------------------------------------------------------------------------

def create_offspring_population(offspring, toolbox, CXPB):
    # create offspring from parents, select parent 1,3 then 2,4 etc..
    new_offspring = []
    for parent1, parent2 in zip(offspring[::2], offspring[1::2]):

        # first half of the individual contains the order of the boxes ( their IDs ) which are ints
        # here when we extract first half its type becomes a list, therefore a new individual wrapper is needed
        idsChromosome1 = creator.Individual(parent1[:int(len(parent1) / 2)])
        idsChromosome2 = creator.Individual(parent2[:int(len(parent2) / 2)])
        # second half of the individual contains their orientations which are 0,1
        orientationsChromosome1 = creator.Individual(parent1[int(len(parent1) / 2):])
        orientationsChromosome2 = creator.Individual(parent2[int(len(parent2) / 2):])

        if np.random.random() <= CXPB:
            idsChromosome1, idsChromosome2 = toolbox.mate_ids(idsChromosome1, idsChromosome2)
            toolbox.mate_orientations(orientationsChromosome1, orientationsChromosome2)

        # P.C here we are always mutating the resulting children from the cx,
        # we can mutate in a separate prob or mutate parents. If we do that, mutation will not always occur hence
        # we need to make sure we return original parent with original fitness and crowding distance untouched
        toolbox.mutate_ids(idsChromosome1)
        toolbox.mutate_ids(idsChromosome2)

        toolbox.mutate_orientations(orientationsChromosome1)
        toolbox.mutate_orientations(orientationsChromosome2)

        idsChromosome1.extend(orientationsChromosome1[:])
        idsChromosome2.extend(orientationsChromosome2[:])
        new_offspring.append(idsChromosome1)
        new_offspring.append(idsChromosome2)
    return new_offspring


def GetWorstIndividual(pop):
    worst_individual = None
    for ind in pop:
        if worst_individual is None:
            worst_individual = ind
            continue
        if (ind.fitness.values[0] + ind.fitness.values[1]) > (
                worst_individual.fitness.values[0] + worst_individual.fitness.values[1]):
            worst_individual = ind
    return copy.deepcopy(worst_individual)


def GetBestIndividual(pop):
    best_individual = None
    for ind in pop:
        if best_individual is None:
            best_individual = ind
            continue
        if (ind.fitness.values[0] + ind.fitness.values[1]) < (
                best_individual.fitness.values[0] + best_individual.fitness.values[1]):
            best_individual = ind
    return copy.deepcopy(best_individual)


def cxCutAndCrossFill(individual1, individual2):
    child1 = creator.Individual([])
    child2 = creator.Individual([])
    crossOverPoint = np.random.randint(1, len(individual1) - 1)
    child1.extend(individual1[:crossOverPoint])
    child1.extend([x for x in individual2[crossOverPoint:] if x not in child1])
    child1.extend([x for x in individual2[:crossOverPoint] if x not in child1])

    child2.extend(individual2[:crossOverPoint])
    child2.extend([x for x in individual1[crossOverPoint:] if x not in child2])
    child2.extend([x for x in individual1[:crossOverPoint] if x not in child2])
    return child1, child2


def mutate_orientations(orientations, indpb):
    for i in range(len(orientations)):
        if np.random.random() < indpb:
            if orientations[i] == 0:
                orientations[i] = np.random.choice([1, 2])
            elif orientations[i] == 1:
                orientations[i] = np.random.choice([0, 2])
            elif orientations[i] == 2:
                orientations[i] = np.random.choice([0, 1])


def pareto_frontier(Xs, Ys, maxX=True, maxY=True):
    print("here")
    # Sort the list in either ascending or descending order of X
    myList = sorted([[Xs[i], Ys[i]] for i in range(len(Xs))], reverse=maxX)
    # Start the Pareto frontier with the first value in the sorted list
    p_front = [myList[0]]
    # Loop through the sorted list
    for pair in myList[1:]:
        if maxY:
            if pair[1] >= p_front[-1][1]:  # Look for higher values of Y…
                # print("adding pair " + str(pair))
                p_front.append(pair)  # … and add them to the Pareto frontier
        else:
            if pair[1] <= p_front[-1][1]:  # Look for lower values of Y…
                p_front.append(pair)  # … and add them to the Pareto frontier
    # Turn resulting pairs back into a list of Xs and Ys
    p_frontX = [pair[0] for pair in p_front]
    p_frontY = [pair[1] for pair in p_front]
    return p_frontX, p_frontY


def paretoGraph(pop, boxNumber):
    PFSpace = []
    PFPriority = []
    for ind in pop:
        PFSpace.append(ind.fitness.values[0])
        PFPriority.append(ind.fitness.values[1])
    # print(PFSpace)
    # Find lowest values for both space and priority
    p_front = pareto_frontier(PFSpace, PFPriority, maxX=False, maxY=False)
    size = len(PFSpace)
    # print(p_front)
    # Plot a scatter graph of all results
    plt.scatter(PFSpace, PFPriority, s=size)
    # Then plot the Pareto frontier on top

    plt.plot(p_front[0], p_front[1])
    plt.plot(p_front[0][0], p_front[1][0], marker="o", markersize=10, markeredgecolor="red", markerfacecolor="red")
    plt.plot(p_front[0][-1], p_front[1][-1], marker="o", markersize=10, markeredgecolor="green",
             markerfacecolor="green")
    plt.plot(p_front[0][len(p_front[0]) // 2], p_front[1][len(p_front[1]) // 2], marker="o", markersize=10,
             markeredgecolor="blue", markerfacecolor="blue")
    plt.xlabel("Space Fitness")
    plt.ylabel("Priority Fitness")
    plt.suptitle("Pareto frintier when boxes are:" + str(boxNumber))
    filename = "Pareto frintier when boxes are "
    plt.savefig('{}{:d}.png'.format(filename, boxNumber))
    plt.show()
    plt.close()
    for ind in pop:
        if (ind.fitness.values[0] == p_front[0][0] and ind.fitness.values[1] == p_front[1][0]):
            containers = helper.pack_solution(ind, copy.deepcopy(boxes))
            animate_containers(containers,
                               "the individual with best space (red) for pareto with boxes " + str(boxNumber))
            print("red space: " + str(p_front[0][0]) + " red priority: " + str(p_front[1][0]))
        if (ind.fitness.values[0] == p_front[0][-1] and ind.fitness.values[1] == p_front[1][-1]):
            containers = helper.pack_solution(ind, copy.deepcopy(boxes))
            animate_containers(containers,
                               "the individual with best priority and space (green) for pareto with boxes " + str(
                                   boxNumber))
            print("green space: " + str(p_front[0][-1]) + " green priority: " + str(p_front[1][-1]))
        if (ind.fitness.values[0] == p_front[0][len(p_front[0]) // 2] and ind.fitness.values[1] == p_front[1][
            len(p_front[1]) // 2]):
            containers = helper.pack_solution(ind, copy.deepcopy(boxes))
            animate_containers(containers,
                               "the individual with best priority (blue) for pareto with boxes " + str(boxNumber))
            print("blue space: " + str(p_front[0][-1]) + " blue priority: " + str(p_front[1][-1]))
    PFSpace = []
    PFPriority = []


def FillDataList(dataList):
    global x1, x2, x3
    global boxNumber
    if (boxNumber == 70):
        for ind in hallOfFame:
            dataList["bestFor60BoxesSpaceFitness"].append(ind.fitness.values[0])
            dataList["bestFor60BoxespriorityFitness"].append(ind.fitness.values[1])
            x1 = np.arange(0, len(hallOfFame))
        for ind in hallOfShame:
            dataList["worstFor60BoxesSpaceFitness"].append(ind.fitness.values[0])
            dataList["worstFor60BoxespriorityFitness"].append(ind.fitness.values[1])
    if (boxNumber == 140):
        for ind in hallOfFame:
            dataList["bestFor120BoxesSpaceFitness"].append(ind.fitness.values[0])
            dataList["bestFor120BoxespriorityFitness"].append(ind.fitness.values[1])
            x2 = np.arange(0, len(hallOfFame))
        for ind in hallOfShame:
            dataList["worstFor120BoxesSpaceFitness"].append(ind.fitness.values[0])
            dataList["worstFor120BoxespriorityFitness"].append(ind.fitness.values[1])
    if (boxNumber == 210):
        boxNumber == 200
        for ind in hallOfFame:
            dataList["bestFor180BoxesSpaceFitness"].append(ind.fitness.values[0])
            dataList["bestFor180BoxespriorityFitness"].append(ind.fitness.values[1])
            x3 = np.arange(0, len(hallOfFame))
        for ind in hallOfShame:
            dataList["worstFor180BoxesSpaceFitness"].append(ind.fitness.values[0])
            dataList["worstFor180BoxespriorityFitness"].append(ind.fitness.values[1])
    print(len(dataList["worstFor180BoxesSpaceFitness"]))


def PlotDataList(dataList):
    global x1, x2, x3
    # plot the 60 120 180 boxes with both fitness value
    plt.plot(x1, dataList["bestFor60BoxesSpaceFitness"], 'g-', label="70 boxes")
    plt.plot(x2, dataList["bestFor120BoxesSpaceFitness"], 'r-', label="140 boxes")
    plt.plot(x3, dataList["bestFor180BoxesSpaceFitness"], 'b-', label="200 boxes")
    plt.legend()
    plt.xlabel("Generations")
    plt.ylabel("Space Fitness")
    plt.suptitle("Best individual for space penality for 3 number of boxes and 2 fitness")
    plt.show()
    plt.savefig('Best individual for space penality for 3 number of boxes and 2 fitness.png')

    plt.close()

    plt.plot(x1, dataList["worstFor60BoxesSpaceFitness"], 'g-', label="70 boxes")
    plt.plot(x2, dataList["worstFor120BoxesSpaceFitness"], 'r-', label="140 boxes")
    plt.plot(x3, dataList["worstFor180BoxesSpaceFitness"], 'b-', label="200 boxes")
    plt.legend()
    plt.xlabel("Generations")
    plt.ylabel("Space Fitness")
    plt.suptitle("Worst individual for space penality for 3 number of boxes and 2 fitness")
    plt.show()
    plt.savefig('Worst individual for space penality for 3 number of boxes and 2 fitness.png')

    plt.close()

    plt.plot(x1, dataList["bestFor60BoxespriorityFitness"], 'g-', label="70 boxes")
    plt.plot(x2, dataList["bestFor120BoxespriorityFitness"], 'r-', label="140 boxes")
    plt.plot(x3, dataList["bestFor180BoxespriorityFitness"], 'b-', label="200 boxes")
    plt.legend()
    plt.xlabel("Generations")
    plt.ylabel("Priority Fitness")
    plt.suptitle("Best individual for priority penality for 3 number of boxes and 2 fitness")
    plt.show()
    plt.savefig('Best individual for priority penality for 3 number of boxes and 2 fitness.png')

    plt.close()

    plt.plot(x1, dataList["worstFor60BoxespriorityFitness"], 'g-', label="70 boxes")
    plt.plot(x2, dataList["worstFor120BoxespriorityFitness"], 'r-', label="140 boxes")
    plt.plot(x3, dataList["worstFor180BoxespriorityFitness"], 'b-', label="200 boxes")
    plt.legend()
    plt.xlabel("Generations")
    plt.ylabel("Priority Fitness")
    plt.suptitle("Worst individual for priority penality for 3 number of boxes and 2 fitness")
    plt.show()
    plt.savefig('Worst individual for priority penality for 3 number of boxes and 2 fitness.png')

    plt.close()


if __name__ == "__main__":
    np.random.seed(22)
    random.seed(22)
    # test it with only space of priority fitness, but have to change the evaluation manually and using same thing below
    # and need to take the graph out of the folder or it will be overwrite
    global boxes
    global x1, x2, x3
    # for three different boxes number

    dataList = {
        "bestFor60BoxesSpaceFitness": [],
        "worstFor60BoxesSpaceFitness": [],
        "bestFor60BoxespriorityFitness": [],
        "worstFor60BoxespriorityFitness": [],
        "bestFor120BoxesSpaceFitness": [],
        "worstFor120BoxesSpaceFitness": [],
        "bestFor120BoxespriorityFitness": [],
        "worstFor120BoxespriorityFitness": [],
        "bestFor180BoxesSpaceFitness": [],
        "worstFor180BoxesSpaceFitness": [],
        "bestFor180BoxespriorityFitness": [],
        "worstFor180BoxespriorityFitness": []}

    # this is when the Space and prority are both in the evaluation funtion
    # this will be only using in the situation. one by one will provide at end
    boxesNumbers = [70, 140, 200]
    for boxNumber in boxesNumbers:
        helper = Helper(120, 120, 220)
        boxes = helper.create_boxes(boxNumber)
        pop, stats, hallOfFame, hallOfShame = main()
        pop.sort(key=lambda x: x.fitness, reverse=True)
        # best individual
        best_ind = hallOfFame[-1]
        worst_ind = hallOfShame[0]
        print("best individual penalities: " + str(best_ind.fitness.values))
        print("worst individual penalities: " + str(worst_ind.fitness.values))
        if (boxNumber == 70):
            containers = helper.pack_solution(worst_ind, copy.deepcopy(boxes))
            animate_containers(containers, "Worst individual across all generations with boxes " + str(boxNumber))
            # worst individual
            containers = helper.pack_solution(best_ind, copy.deepcopy(boxes))
            animate_containers(containers, "Best individual across all generations with boxes " + str(boxNumber))
        if (boxNumber == 140):
            containers = helper.pack_solution(worst_ind, copy.deepcopy(boxes))
            animate_containers(containers, "Worst individual across all generations with boxes " + str(boxNumber))
            # worst individual
            containers = helper.pack_solution(best_ind, copy.deepcopy(boxes))
            animate_containers(containers, "Best individual across all generations with boxes " + str(boxNumber))
        if (boxNumber == 200):
            containers = helper.pack_solution(worst_ind, copy.deepcopy(boxes))
            animate_containers(containers, "Worst individual across all generations with boxes " + str(boxNumber))
            # worst individual
            containers = helper.pack_solution(best_ind, copy.deepcopy(boxes))
            animate_containers(containers, "Best individual across all generations with boxes " + str(boxNumber))
        FillDataList(dataList)
        paretoGraph(pop, boxNumber)

    # PlotDataList(dataList)

    # 70
    # red space: 1.856 red priority: 0.308
    # blue space: 2.12 blue priority: 0.21
    # green space: 2.12 green priority: 0.21

    # best individual penalities: (1.856, 0.308)
    # worst individual penalities: (2.143, 0.37)

    # helper = Helper(110, 110, 200)
    # boxes = helper.create_boxes(boxNumber)   
    # pop, stats, hallOfFame, hallOfShame = main()
    # pop.sort(key=lambda x: x.fitness, reverse=True)

    # # test it with only space of priority fitness, but have to change the evaluation manually
    # # for individual in HallOfFame containers = helper.pack_solution(worst_ind, copy.deepcopy(boxes))
    # bestSpaceFitness = []
    # for individual in hallOfFame:
    #     containers = helper.pack_solution(individual, copy.deepcopy(boxes))
    #     SpaceFitness = SpacePenality(containers)
    #     bestSpaceFitness.append(SpaceFitness)
    #     # individual.fitness.values = (SpaceFitness,individual.fitness.values[0])
    #     # print(individual.fitness.values)
    #     # label: Best individual in terms of space in each generation while training for priority
    #     # draw priority as well
    # S = np.arange(0, len(hallOfFame))
    # plt.plot(S, bestSpaceFitness, 'c-', label = "60 boxes")
    # plt.legend()
    # plt.xlabel("Generations")
    # plt.ylabel("Space Fitness")
    # plt.suptitle("Best individual in terms of space in each generation while training for priority")
    # plt.savefig('DataPic/Best individual in terms of space in each generation while training for priority.png')
    # # plt.show()
    # # print(bestSpaceFitness)
    # plt.close()

    # worstSpaceFitness = []
    # for individual in hallOfShame:
    #     containers = helper.pack_solution(individual, copy.deepcopy(boxes))
    #     SpaceFitness = SpacePenality(containers)
    #     worstSpaceFitness.append(SpaceFitness)
    #     # individual.fitness.values = (SpaceFitness,individual.fitness.values[0])
    #     # print(individual.fitness.values)
    #     # label: Best individual in terms of space in each generation while training for priority
    #     # draw priority as well
    # S = np.arange(0, len(hallOfFame))
    # plt.plot(S, worstSpaceFitness, 'c-', label = "60 boxes")
    # plt.legend()
    # plt.xlabel("Generations")
    # plt.ylabel("Space Fitness")
    # plt.suptitle("Worst individual in terms of space in each generation while training for priority")
    # plt.savefig('DataPic/Worst individual in terms of space in each generation while training for priority.png')
    # # plt.show()
    # # print(bestSpaceFitness)
    # plt.close()
    # #------------------------------------------------------------
    # bestProrityFitness = []
    # for individual in hallOfFame:
    #     PriorityFitness = PriorityPenality(individual, boxes)
    #     bestProrityFitness.append(PriorityFitness)
    #     # individual.fitness.values = (individual.fitness.values[1],PriorityFitness)
    # # plot best and worst fitness over generations
    # S = np.arange(0, len(hallOfFame))
    # plt.plot(S, bestProrityFitness, 'c-', label = "60 boxes")
    # plt.legend()
    # plt.xlabel("Generations")
    # plt.ylabel("ProrityFitness")
    # plt.suptitle("Best individual in terms of priority in each generation while training for space")
    # plt.savefig('DataPic/Best individual in terms of priority in each generation while training for space.png')
    # # plt.show()
    # # print(bestProrityFitness)
    # plt.close()

    # worstProrityFitness = []
    # for individual in hallOfShame:
    #     PriorityFitness = PriorityPenality(individual, boxes)
    #     worstProrityFitness.append(PriorityFitness)
    #     # individual.fitness.values = (individual.fitness.values[1],PriorityFitness)
    # # plot best and worst fitness over generations
    # S = np.arange(0, len(hallOfFame))
    # plt.plot(S, worstProrityFitness, 'c-', label = "60 boxes")
    # plt.legend()
    # plt.xlabel("Generations")
    # plt.ylabel("ProrityFitness")
    # plt.suptitle("Worst individual in terms of priority in each generation while training for space")
    # plt.savefig('DataPic/Worst individual in terms of priority in each generation while training for space.png')
    # # plt.show()
    # # print(bestProrityFitness)
    # plt.close()
    # -------------------------------------------------------
    # spaceHallOfFameFitnesses = []
    # priorityHallOfFameFitnesses = []

    # for ind in hallOfFame:
    #     spaceHallOfFameFitnesses.append(ind.fitness.values[0])
    #     priorityHallOfFameFitnesses.append(ind.fitness.values[1])

    # spaceHallOfShameFitnesses = []
    # priorityHallOfShameFitnesses = []
    # for ind in hallOfShame:
    #     spaceHallOfShameFitnesses.append(ind.fitness.values[0])
    #     priorityHallOfShameFitnesses.append(ind.fitness.values[1])

    # x = np.arange(0, len(hallOfFame))
    # plt.plot(x, spaceHallOfFameFitnesses, 'g-', label = "Best individuals")
    # plt.plot(x, spaceHallOfShameFitnesses, 'r-', label = "Worst individuals")
    # plt.suptitle("Best and worst individual for space penality for 120 boxes and 2 fitness")
    # plt.legend()

    # plt.show()

    # plt.plot(x, priorityHallOfFameFitnesses, 'g-', label = "Best individuals")
    # plt.plot(x, priorityHallOfShameFitnesses, 'r-', label = "Worst individuals")
    # plt.suptitle("Best and worst individual for priority penality for 120 boxes and 2 fitness")
    # plt.show()
