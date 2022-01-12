from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from matplotlib.animation import FuncAnimation
import numpy as np
from Box import *

def visualize_solution(bin, boxes):
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection='3d')
    ax.set_xlim3d(0, bin.width)
    ax.set_ylim3d(0, bin.height)
    ax.set_zlim3d(0, bin.depth)
    # plot sides
    # the poly3dcollection takes faces of the shape to be plotted, not the vertices directly
    ax.add_collection3d(Poly3DCollection(bin.get_box_faces(),
                                         facecolors='white', linewidths=0.5, edgecolors='b', alpha=.0))
    for box in boxes:
        c = np.random.choice(colors)
        ax.add_collection3d(Poly3DCollection(box.get_box_faces(),
                                             facecolors=c, linewidths=0.3, edgecolors=c, alpha=.2))
    plt.show()


def visualize_individual(containers):
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', '#FF6000', '#43FF00', '#FCFF00', '#8400FF', '#0095FF', '#603702',
              '#8B8B8B']
    fig, axes = plt.subplots(len(containers), subplot_kw=dict(projection='3d'))
    fig.suptitle('packed boxes')
    for i, container in enumerate(containers):
        axes.set_xlim3d(0, container.width)
        axes.set_ylim3d(0, container.depth)
        axes.set_zlim3d(0, container.height)
        axes.add_collection3d(Poly3DCollection(container.get_container_faces(),
                                               facecolors='white', linewidths=0.5, edgecolors='b', alpha=.0))

        for box in container.boxes:
            print(box.bottom_left_coordinates)
            print("with width " + str(box.width) + " " + str(box.height) + " " + str(box.depth))
            print("id " + str(box.ID))
            c = np.random.choice(colors)
            axes.add_collection3d(Poly3DCollection(box.get_box_faces(),
                                                   facecolors=c, linewidths=0.27, edgecolors='k', alpha=.35))
    plt.show()


def animate(i, containers, axes):
    # you can add if statement here to check if its container 1 then use axis 1.
    container_id = None
    frame_ranges = []
    total_boxes = 0
    for container in containers:
        frame_ranges.append(total_boxes + len(container.boxes))
        total_boxes += len(container.boxes)
    for j, frame_range in enumerate(frame_ranges):
        if i < frame_range:
            container_id = j
            break

    try:
        axes = axes[container_id]
    except:
        pass
    axes.clear()
    axes.set_xlim3d(0, containers[container_id].width)
    axes.set_ylim3d(0, containers[container_id].depth)
    axes.set_zlim3d(0, containers[container_id].height)
    axes.add_collection3d(Poly3DCollection(containers[container_id].get_container_faces(),
                                                         facecolors='white', linewidths=0.5, edgecolors='b', alpha=.0))
    if container_id > 0:
        if i >= frame_ranges[container_id - 1]:
            i -= frame_ranges[container_id - 1]

    for box in containers[container_id].boxes[:i + 1]:
        axes.add_collection3d(Poly3DCollection(box.get_box_faces(),
                                                             facecolors=box.color, linewidths=0.27, edgecolors='k', alpha=.35))


def animate_containers(containers, description):
    fig, axes = plt.subplots(nrows=1, ncols=len(containers), subplot_kw=dict(projection='3d'))
    fig.set_size_inches(10, 6)
    fig.suptitle(description)
    frames = 0
    for container in containers:
        frames += len(container.boxes)
    ani = FuncAnimation(fig, animate, fargs=(containers, axes), frames=frames, interval=150,
                        repeat=False)
    # uncomment this if you want to save the gif
    #ani.save(description + ".GIF")
    plt.show()


# def visualize_EMSs(EMSs, box, container):
#     fig, axes = plt.subplots(1, subplot_kw=dict(projection='3d'))
#     fig.suptitle('Empty Maximal Spaces')
#     axes.set_xlim3d(0, container.width)
#     axes.set_ylim3d(0, container.depth)
#     axes.set_zlim3d(0, container.height)
#     axes.add_collection3d(Poly3DCollection(container.get_container_faces(),
#                                            facecolors='white', linewidths=0.5, edgecolors='b', alpha=.0))
#     axes.add_collection3d(Poly3DCollection(box.get_box_faces(),
#                                            facecolors='r', linewidths=0.3, edgecolors='k', alpha=.99))
#
#     colors = ['b', 'g', 'c', 'm', 'y', 'k', '#FF6000', '#43FF00', '#FCFF00', '#8400FF', '#0095FF', '#603702',
#               '#8B8B8B']
#     c = np.random.choice(colors)
#     box = Box(1, EMSs[4].width , EMSs[4].height, EMSs[4].depth - 20, 2, 2)
#     points = EMSs[2].bottom_left_coordinates
#     points = (points[0], points[1], points[2])
#     box.pack_box(EMSs[4].bottom_left_coordinates)
#     axes.add_collection3d(Poly3DCollection(box.get_box_faces(),
#                                          facecolors='#0095FF', linewidths=0.3, edgecolors='k', alpha=.2))
#     plt.show()