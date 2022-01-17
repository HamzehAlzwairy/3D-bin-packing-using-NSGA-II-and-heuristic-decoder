# 3D-bin-packing-using-NSGA-II-and-heuristic-decoder


## Introduction
3D bin packing is a classic NP-hard problem, we need to pack the given boxes into the least possible number of bins or containers to save as much space as possible. In this project we are aiming to add one more objective to the space saving object; ordering the boxes according to packing priority ( which box is to be retrieved from the container first ). In this project, we will use Evolutionary **Computing algorithms** to solve this problem, namely **NSGA-II**. We will also use a so called **Heuristic Decoder** to handle feasibility issues for the produced solutions by the NSGA-II. In short, it will use the Empty Maximal Spaces process described in [2] to locate the empty space inside the container that is available for packing, it will also apply several other functions like box rotation, box placement, finding empty space and updating empty space after placement. The reason we decided to use the decoder mentioned above is to move the feasibility and complexity issues of this problem into the
objective evaluation. So, now we can use sequence operators like two point crossover and shuffle indices mutation without worrying about the feasibility of the produced solutions. If we use the GA to change the boxes' locations directly then it's difficult to produce feasible solutions as the initialization and operators need to account for boxes not to overlap with each other in the container space. This makes the problem really complex, and the search space will be difficult to explore properly.


## Methodology
We will use the NSGA-II to find the order and orientation of the
boxes we have, whereas the heuristic decoder is used to translate
this genome ( order and orientations ) into a phenome (packed
solution) in order to evaluate the individual during the NSGA-II..
We move feasibility issues of the problem to a heuristic decoder
that will handle the box placement process, this decoder should
take as input an individual and return a packed solution ( list of
containers along with the boxes packed inside of them ).
The decoder consists of the following :

1- Placement heuristic function: Try fitting the box in each EMS
to determine which EMSs are feasible for this box.

2- Chooses the EMS according to the Back-Bottom-Left (BBL)
heuristic rule ( choose the spot with the lowest Z, Y, X coordinates
in order ) and places packs the box in that location, check figure below.

<img width="250" alt="BBL" src="https://user-images.githubusercontent.com/95043560/149689365-1d65c86a-0ba4-4aa0-8dc1-df50b699a80f.png">

3- Empty Maximal Space creation function: After packing a box
into a location, this function checks which existing EMSs intersect
with the packed box in order to create the new EMSs.

4- Empty Maximal Space update function: Because some created
empty spaces will have infinite thinness or might be totally
inscribed within other EMSs, this function is meant to find such
EMSs and remove them as they are unusable and only add
overhead to the program in the next iterations. We also make sure
to remove EMSs that do not fit any of the remaining boxes, i.e
they have less volume than any of the remaining boxes or their
dimensions don’t fit any of the remaining boxes. We apply those
two checks in sequence as in [6], the removal of these EMSs
reduces computational complexity as these EMSs won’t be used
in any future box placement.


## Initialization
First, initialize a set of boxes with random dimensions, priorities, weights, and orientations, see figure below. Create an initial container to use for packing the boxes. The decoder handles opening additional containers when space is needed. Each individual consists of two parts, the first part is the order in which the boxes are packed, and the second part is the orientation of each box. For example: [3,9,8,10,7,4,6,5,1,2,1,1,1,0,0,0,0,1,2,2, 1] Here, the first 10 digits are the ID of each box, and the last 10 digits (0, 1, 2) are the arrangement of each box on the left side of the chromosome. The 0 direction means the original direction (no direction) in which the box was created, 1 means the front and back are up and down, and 2 means the sides are up and down.

<img width="302" alt="initialization" src="https://user-images.githubusercontent.com/95043560/149690326-e64b150e-a850-4b66-a025-34d4e8028bd0.png">


## Penality functions
Penalty Evaluation We have created the following merit functions, all of which need to be minimized: 

- Space Penalty: This function performs really well for the 3D bin
packing problem according to [6]. NB means the number of
containers, BV is the volume of the last container's box, CV is the
volume of the last container. This function represents how well
the solution is using the available space (individually). Check only
the last container because it contains enough information. This is
because if it is better to pack the boxes using the previous
container, the last container will receive less boxes. Use NB parts
to punish the solution with more containers. If you use only the
BV / CV of the last container, you cannot distinguish between a
solution with two containers and a solution with three containers,
see figure below.

<img width="307" alt="Space penality" src="https://user-images.githubusercontent.com/95043560/149690538-6cf68e0e-5776-4c28-b431-541b692e564f.png">

- Priority Penality, PP is the priority penalty, P is the priority, N is the number of boxes, and I is the index (order) of the person's boxes. This function shows how wrong the priority is. Therefore, there are 50 boxes, with the 50th priority (highest priority) box first. Get 50-0/50 = 1.00. This is the maximum penalty, which is a percentage of how far the boxing order is from the correct position. We sum this penalty over every box in the chromosome and after that we divide them by N again, and this way, instead of getting some arbitrary number, we get a percentage that represents how off mark the individual is.


<img width="325" alt="priority penality" src="https://user-images.githubusercontent.com/95043560/149690777-b9231e71-6aa4-4676-bc0d-1e743b4e398d.png">


## Results
The following two GIFs show the visualization of the phenomes ( which are genomes that were passed to the decoder ) for a run of the program using 70 boxes with random dimensions sampled from a set of dimensions proportional to the container size, the larger the dimension the lower the probablity of using this dimension ( it produces fewer boxes with large width, depth or height ). The program was run for 50 generations:


Worst individual across the 50 generations ( used the space the most among all solutions ):


![Worst individual across all generations](https://user-images.githubusercontent.com/95043560/149696745-d42deb2e-9daa-45a6-ad73-2e0db3b543ee.GIF)


Best individual across the 50 generations ( as we can see the algorithm was able to reduce the number of containers used from 3 to 2 using this solution ):

![Best individual across all generations](https://user-images.githubusercontent.com/95043560/149697070-a0aa4621-094a-46e5-9472-62657ab2f380.GIF)


**The following plots show the results we got when running the program for 70, 140, and 200 boxes :


![Worst individuals across generations for priority penality](https://user-images.githubusercontent.com/95043560/149697978-718bb793-75b2-4889-8bda-6f9277092e32.png)



![DBest individuals across generations for priority penality](https://user-images.githubusercontent.com/95043560/149698345-45ffb81d-ee7f-43ad-845f-9cb31ccdc819.png)



![Worst individuals across generations for space penality](https://user-images.githubusercontent.com/95043560/149698419-4e3e81de-5e8f-4f0c-be16-1bf1b331d3ce.png)



![Best individuals across generations for space penality](https://user-images.githubusercontent.com/95043560/149698469-6e378bae-f466-4056-b400-b8c3982f9105.png)


**The following are the pareto fronts for each of the runs above:**

Pareto front for the 70 boxes run :

<img width="364" alt="pareto 70 boxes" src="https://user-images.githubusercontent.com/95043560/149699726-bb943381-ba20-4447-9b44-4ecc2f0468e4.png">


Pareto front for the 140 boxes run:

<img width="343" alt="pareto 140" src="https://user-images.githubusercontent.com/95043560/149699752-f95ad97d-2db7-48a5-9d73-6c73ba135df9.png">


Pareto front for the 200 boxes run:

<img width="385" alt="pareto 200" src="https://user-images.githubusercontent.com/95043560/149699780-6d3b6564-82f7-4b01-a744-e2fbdc2a5a9b.png">



## REFERENCES
[1] Bean, J., 1994. Genetic algorithms and random keys for sequencing and
optimization. ORSA Journal on Computing 6, 154–160. 

[2] Lai, K., Chan, J., 1997. Developing a simulated annealing algorithm for the
cutting stock problem. Computers and Industrial Engineering 32, 115–127.

[3] DEAP. (n.d.). Deap/nsga2.py at master · DEAP/deap. GitHub. Retrieved
December 7, 2021, from
https://github.com/DEAP/deap/blob/master/examples/ga/nsga2.py.

[4] David Kosiur. 2001. Understanding Policy-Based Networking (2nd. ed.). Wiley,
New York, NY.

[5] J, Gonçalves. M. Resende. 2013. A biased random key genetic algorithm for 2D
and 3D bin packing problems, Int. J. Production Economics 145 (2013)
500–510.
