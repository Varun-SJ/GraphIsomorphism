from graph import *
from graph_io import *
import time


GRAPH_SAMPLES = [
    'Color_Refinement_Graphs/colorref_smallexample_4_7.grl',
    'Color_Refinement_Graphs/colorref_smallexample_6_15.grl',
    'Color_Refinement_Graphs/colorref_smallexample_4_16.grl',
    'Color_Refinement_Graphs/colorref_smallexample_2_49.grl',
    'Color_Refinement_Graphs/colorref_largeexample_6_960.grl',
    'Color_Refinement_Graphs/colorref_largeexample_4_1026.grl',

    'Archive2/trees36.grl',
    'Archive2/products72.grl',
    'Archive2/modulesC.grl',
    'Archive2/torus144.grl'
]


def get_next_color(colors):
    return colors.index([])


def color_graph(vertices, colors=None):

    def build_neighbourhood(vertex):

        cn = {}     # colored neighbourhood
        for v in vertex.neighbours:
            cn[v.colornum] = cn.get(v.colornum, 0) + 1

        return cn

    # initilization of colors according to their degree
    if colors is None:
        colors = [[] for _ in range(len(vertices) + 1)]
        for v in vertices:
            colors[v.degree - 1].append(v)
            v.colornum = v.degree - 1
            v.next_colornum = v.colornum

    # init invariants, loop while some nodes got new colors
    needs_more_work = True
    next_color = get_next_color(colors)
    while needs_more_work:

        # expect to be done
        needs_more_work = False

        # for all colors
        for c in colors:

            # no more splitting necessary
            if len(c) <= 1:
                continue

            # analyze the neighbourhood of the first vertex
            vn = build_neighbourhood(c[0])

            # for all other vertices
            i = 1

            while i < len(c):

                # get the vertex and analyze its neighbourhood
                u = c[i]
                un = build_neighbourhood(u)
                i += 1

                # if the neighbourhoods of u and v are the same, all is fine, handle next vertex
                if vn == un:
                    continue

                # override the color, remove it from the previous one, add it to the new one
                u.next_colornum = next_color

            i = 0
            while i < len(c):
                v = c[i]
                if v.colornum != v.next_colornum:
                    v.colornum = v.next_colornum
                    c.remove(v)
                    colors[next_color].append(v)
                else:
                    i += 1

            # if a vertex's color was moved, more work is necessary
            if len(colors[next_color]) > 0:
                next_color = get_next_color(colors)
                needs_more_work = True

    # DONE
    return colors


def are_graphs_isomorph(graph1, graph2):
    """
    Check whether one graph is an isomorphism of the other
    :param graph1: some graph
    :param graph2: other graph to check against
    :return: True if graph1 and graph2 are isomorphic otherwise False
    """

    def check_colors(colors):
        for c in colors:

            # empty color
            if len(c) == 0:
                continue
            # no bijection
            if len(c) % 2 == 1:
                return False

            if len(c) == 2:
                if (c[0] in graph1.vertices) == (c[1] in graph1.vertices):
                    return False
                continue

            # len(c) >= 4 and even
            x = c[0]
            colors[x.colornum].remove(x)
            x.colornum = get_next_color(colors)
            x.next_colornum = x.colornum
            colors[x.colornum] = [x]

            for i in range(len(c) // 2, len(c)):

                new_colors = [l[:] for l in colors]

                y = c[i]
                new_colors[y.colornum].remove(y)
                y.colornum = x.colornum
                y.next_colornum = x.colornum
                new_colors[x.colornum].append(y)

                new_colors = color_graph(c, colors=new_colors)
                if check_colors(new_colors):
                    return True

            return False

        return True

    # simple pre-checks
    if graph1 is None or graph2 is None:
        return False
    if graph1 is graph2:
        return True
    if len(graph1.vertices) != len(graph2.vertices):
        return False
    if len(graph1.edges) != len(graph2.edges):
        return False

    # color both graphs and compare them
    vertices = graph1.vertices + graph2.vertices
    colors = color_graph(vertices)

    # DONE
    return check_colors(colors)


def count_isomorphism(g1, g2):

    def count(colors=None):

        # color the graphs
        colors = color_graph(vertices, colors)

        # check if unbalanced
        if is_unbalanced(colors):
            return 0
        # check for bijection
        if is_bijection(colors):
            return 1

        # choose a color index where len(c) >= 4
        c_index = None
        i = 0
        while i < len(colors):
            if len(colors[i]) >= 4:
                c_index = i
                break
            i += 1

        # choose a vertex x where x is in g1 of this color
        x = None
        i = len(colors[c_index]) - 1
        while i >= 0:
            v = colors[c_index][i]
            if v in g1.vertices:
                x = v
                break
            i -= 1

        # choose all vertices y that are in g2 of this color
        num = 0
        for v in colors[c_index]:
            if v in g2.vertices:
                y = v
                colornum_equals_color_index(colors, c_index)
                new_colors = move_to_new_color(colors, c_index, x, y)
                num += count(new_colors)
        return num

    def colornum_equals_color_index(colors, c_index):
        i = 0
        while i < len(colors):
            for v in colors[i]:
                v.colornum = i
                v.next_colornum = i
            i += 1


    def move_to_new_color(colors_old, c_index, x, y):
        colors = [l[:] for l in colors_old]

        colors[c_index].remove(x)
        colors[c_index].remove(y)
        c_next_index = get_next_color(colors)
        colors[c_next_index].append(x)
        colors[c_next_index].append(y)

        x.colornum = c_next_index
        x.next_colornum = c_next_index
        y.colornum = c_next_index
        y.next_colornum = c_next_index
        return colors

    def is_unbalanced(colors):
        for c in colors:
            # uneven, definitely unbalanced
            if len(c) % 2 == 1:
                return True
            # even and >= 2, check if equal amount of vertices in one graph as the other
            if len(c) >= 2:
                #todo: create nicer data structure 'colors' to avoid this for-loop
                sum_g1 = 0
                sum_g2 = 0
                for v in c:
                    if v in g1.vertices:
                        sum_g1 += 1
                    else:
                        sum_g2 += 1
                if sum_g1 != sum_g2:
                    return True

    def is_bijection(colors):
        for c in colors:

            # empty color, could be bijection
            if len(c) == 0:
                continue
            # uneven amout of vertices, no bijection
            if len(c) == 1:
                return False

            # exactly two vertices, check if they are in different graphs
            if len(c) == 2:
                if (c[0] in g1.vertices) == (c[1] in g1.vertices):
                    return False
                continue

            if len(c) > 2:
                return False

            # => len(c) = 0, or 2 and are from different graphs.
        return True

    # simple pre-checks
    if g1 is None or g2 is None:
        return 0
    if len(g1.vertices) != len(g2.vertices):
        return 0
    if len(g1.edges) != len(g2.edges):
        return 0

    # list of all vertices of both graphs
    vertices = g1.vertices + g2.vertices

    # use recursive function to count isomorphisms
    return count()


if __name__ == '__main__':
    starttime = time.time()
    with open(GRAPH_SAMPLES[9]) as f:
        L = load_graph(f, read_list=True)

    for i in range(len(L[0])):
        g1 = L[0][i]

        for j in range(i + 1, len(L[0])):
            g2 = L[0][j]

            """
            is_isomorphism = are_graphs_isomorph(g1, g2)
            if is_isomorphism:
                print('Graph {}vs{}: is_isomorphism={}'.format(i, j, is_isomorphism))
            """
            count_iso = count_isomorphism(g1, g2)
            if count_iso > 0:
                print('Graph {}vs{}: count_iso={}'.format(i, j, count_iso))

            with open('colorful{}.dot'.format(i), 'w') as f:
                write_dot(g1, f)
    time_taken = ("This took {:.3f}s".format(time.time() - starttime))
    print(time_taken)
