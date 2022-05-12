# -*- coding: utf-8 -*-
# @Time    : 20/3/22 6:35 μ.μ.
# @Author  : Kostas Risvas
# @Email   : krisvas@ece.upatras.gr
# @File    : utils.py
import copy
import csv
import numpy as np
import math
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def export(root, file_path):
    """Exports model as .feb file.

    Parameters
    ----------

    root: [ET.Element]

    file_path: [string] the file path (.feb can be omitted)

    """
    if '.feb' not in file_path:
        file_path += '.feb'

    # xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent='  ')
    indent(root)
    tree = ET.ElementTree(root)
    # with open(file_path, 'wb') as f:  # Python 3 : 'wb', not 'w'
    #     # f.write(xmlstr.encode("utf-8"))
    #     f.write(ET.tostring(root, xml_declaration='xml',
    #                         short_empty_elements=False))
    tree.write(file_path,
               encoding="utf-8", xml_declaration=True,
               short_empty_elements=False)


def indent(elem, level=0):
    """

    Parameters
    ----------
    elem
    level

    Returns
    -------

    """
    i = "\n" + level * "    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def to_xml_field(value):
    """Converts a python primitive to an xml string field."""

    if isinstance(value, list):
        return ','.join(map(str, value))
    elif isinstance(value, np.ndarray):
        return ','.join(map(str, value.tolist()))
    else:
        return str(value)


def transform(nodes, R, t, order):
    """Transform a set of nodes by a rotation R and a translation t.

    Parameters
    ----------

    nodes: [np.ndarray N x 3] vertices

    R: [np.ndarray 3x3] rotation matrix

    t: [list 3x1] translation vector

    order: order of transformation.
        If "normal", rotation is applied first, i.e. x' = R.x + t
            (same as a 4x4 tranformation matrix).
        If "reverse", translation is applied first, i.e. x' = R.(x + t)
            (is default because Rodriguez formula requires translation first).

    Returns
    -------

    nodes: transformed nodes
    """
    try:
        test = {
            'normal': lambda: np.array([R.dot(x) + np.array(t) for x in nodes]),
            'reverse': lambda: np.array(
                [R.dot(x + np.array(t)) for x in nodes]),
        }[order]()
        return test
    except KeyError:
        raise RuntimeError('Wrong order value. Select "normal" or "reverse".')


def translate(nodes, t):
    """Translates a set of nodes by t.

    Parameters
    ----------

    nodes: [np.ndarray N x 3] vertices

    t: [list 3x1] translation vector

    Returns
    -------

    nodes: the translated nodes

    """
    # return np.array(map(lambda x: x + np.array(t), nodes)) # Python 2.7
    return np.array([x + np.array(t) for x in nodes])  # Python 3.6.7


def scale(nodes, s):
    """Scales a set of nodes by s.

    Parameters
    ----------

    nodes: [np.ndarray N x 3] vertices

    s: [list 3x1] scaling vector

    Returns
    -------

    nodes: the translated nodes

    """
    # return np.array(map(lambda x: np.multiply(x, s), nodes))
    scaled_nodes = copy.copy(nodes)
    if s is not None:
        scaled_nodes = np.array([np.multiply(x, s) for x in nodes]) # Python 3
    # else:
    # scaled_nodes = copy.copy(nodes)
    # scaled_nodes[:, 0] *= s1
    # scaled_nodes[:, 1] *= s2
    # scaled_nodes[:, 2] *= s3

    return scaled_nodes


def rotation_matrix(axis, theta):
    """Return the rotation matrix associated with counterclockwise
    rotation about the given axis by theta radians.

    """
    axis = np.asarray(axis)
    axis = axis / math.sqrt(np.dot(axis, axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])


def anorm2(X):
    """ Compute euclidean norm along axis 1

    """
    return np.sqrt(np.sum(X ** 2, axis=1))


def adet(X, Y, Z):
    """ Compute 3x3 determinnant along axis 1

    """
    ret = np.multiply(np.multiply(X[:, 0], Y[:, 1]), Z[:, 2])
    ret += np.multiply(np.multiply(Y[:, 0], Z[:, 1]), X[:, 2])
    ret += np.multiply(np.multiply(Z[:, 0], X[:, 1]), Y[:, 2])
    ret -= np.multiply(np.multiply(Z[:, 0], Y[:, 1]), X[:, 2])
    ret -= np.multiply(np.multiply(Y[:, 0], X[:, 1]), Z[:, 2])
    ret -= np.multiply(np.multiply(X[:, 0], Z[:, 1]), Y[:, 2])
    return ret


def is_inside(triangles, X):
    """ Compute if a set of points in located inside a 3D mesh described by a list
    of triplets (ie. triangles) of 3d vertices.

    Parameters
    ----------
    triangles: list of triples (tuples) of vertex coordinates forming triangles

    X: set of query points given as np.array([num_points x 3])


    Returns
    -------
    Boolean np.array([num_points x 1]) where True in poisition i indicates that
    the vertex with id = 1  is located inside the mesh
    -------

    Acquired from: https://github.com/marmakoide/inside-3d-mesh For details see:
    Jacobson et al. "Robust Inside-Outside Segmentation using Generalized
    Winding Numbers"

    """

    # One generalized winding number per input vertex
    ret = np.zeros(X.shape[0])

    # Acuumulate generalized winding number for each triangle
    for U, V, W in triangles:
        A, B, C = U - X, V - X, W - X
        omega = adet(A, B, C)  # determinant matrix

        a, b, c = anorm2(A), anorm2(B), anorm2(C)
        k = a * b * c
        k += c * np.sum(np.multiply(A, B), axis=1)
        k += a * np.sum(np.multiply(B, C), axis=1)
        k += b * np.sum(np.multiply(C, A), axis=1)

        ret += np.arctan2(omega, k)

    # Job done
    return ret >= np.pi


def select_nodes_inside_boundary(mesh, boundary_triangle_mesh, axis=2,
                                 percentile=100):
    """ Select a set of nodes located inside a boundary (closed) surface

    Parameters:
    ----------

    mesh = mesh object read with meshio module
    boundary_triangle_mesh = triangular mesh (.stl) read with meshio
    axis: axis to constraint selected nodes
    percentile: percentile of selected nodes in the chosen axis

    Returns:
    -------
    np.array with the node ids of vertices contained inside the boundary mesh

    """
    x = boundary_triangle_mesh.points[:, 0]
    y = boundary_triangle_mesh.points[:, 1]
    z = boundary_triangle_mesh.points[:, 2]
    triangle_ids = boundary_triangle_mesh.cells_dict['triangle']

    tuple_list_vertices = [list(zip(x, y, z))][0]

    poly3d = [[tuple_list_vertices[triangle_ids[ix][iy]]
               for iy in range(len(triangle_ids[0]))]
              for ix in range(len(triangle_ids))]

    # Find vertices inside boundary mesh
    point_in_bool = is_inside(poly3d, mesh.points)
    node_ids = [e for e in range(len(point_in_bool))
                if point_in_bool[e] == True]

    assert (node_ids != [])
    # selected_nodes = mesh.points[node_ids]
    # threshold = np.percentile(selected_nodes[:, axis], percentile)

    # indexes = np.where(selected_nodes[:, axis] <= threshold)
    # return np.array(node_ids)[indexes]
    return np.array(node_ids)


def get_faces_inside_boundary(geometry, boundary, file):
    '''
    Function that extracts the facets of the graft that are inside the boundary
    stl.

    Parameters
    -----------
    geometry:
    boundary: the boundary mesh
    file: a file that contains the nodes of the geometry's facets

    Returns
    -----------
    np.array with the node ids of vertices contained inside the boundary mesh
    '''
    nodes = select_nodes_inside_boundary(geometry, boundary, axis=0,
                                         percentile=100)
    faces = get_hex_faces(file)

    faces = np.where(((faces >= min(nodes)) & (faces <= max(nodes))), faces, 0)
    faces = faces[np.all(faces != 0, axis=1)]

    return faces


def get_hex_faces(filename):
    '''
    Reads the tetrads of node ids of the facets that belong to the surface

    Parameters
    ----------
    filename: The document file that contains the node ids

    Returns
    ----------
    A numpy array with the node ids
    '''
    with open(filename, 'r') as in_file:
        inp = csv.reader(in_file, delimiter=" ")

        facet_nodes = []
        for l in inp:
            facet_nodes.append([int(n) for n in l])

        assert (facet_nodes != [])

        # print(np.array(facet_nodes.shape)
        return np.array(facet_nodes)


def get_smesh_facets(filename):
    '''
    Reads the facet list in .smesh file starting after line "# part 2: facet
    list."

    Returns: np.array([# facets x elem_dim])
    '''
    with open(filename, 'r') as in_file:
        buf = in_file.readlines()

    idx = 0
    for line in buf:
        if line == '# part 2: facet list.\n':
            break
        else:
            idx += 1

    ret = []
    num_elements = buf[idx + 1].split()[0]
    for line in buf[idx + 2:idx + 2 + int(num_elements)]:
        ret.append([int(n) for n in line.split()[1:]])

    assert (ret != [])

    return np.array(ret) - 1


def visualize_mesh(nodes, elements, color=[0.5, 0.5, 0.5], ax=None):
    """Visualizes a mesh that is composed of nodes and elements of any kind.

    Parameters
    ----------

    nodes: [np.ndarray typically N x 3] an array of vertices

    elements: [np.ndarray E x element_type] and array of elements E of different
              types (e.g., triangles, hexahedron)

    """
    x = nodes[:, 0]
    print(x)
    y = nodes[:, 1]
    z = nodes[:, 2]
    N = x.shape[0]
    print(N / 10)
    tuple_list_vertices = list(zip(x, y, z))
    poly3d = [[tuple_list_vertices[elements[ix][iy]]
               for iy in range(len(elements[0]))]
              for ix in range(len(elements))]
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

    ax.scatter(x[::int(N / 10)], y[::int(N / 10)], z[::int(N / 10)])
    triangle_poly = Poly3DCollection(poly3d, linewidths=0.2, alpha=0.5)
    triangle_poly.set_edgecolor('k')
    triangle_poly.set_facecolor(color)
    ax.add_collection3d(triangle_poly)


# def select_surface_elements(mesh):
#   '''
#   Finds triangle elements in surface of tetrahedral mesh

#     Unused.... Time issues....
#     '''
#     comb = [] for L in mesh.cells['tetra']: comb.append([sorted(x) for x in
#     combinations(L, 3)])

#     surface_ids = [i for i, x in enumerate(mesh.cells['triangle']) if
#         sum(line.count(sorted(x)) for line in comb) == 1]

#     # # alternative way
#     # surface_ids = []
#     # for i, x in enumerate(mesh.cells['triangle']):
#     #   if sum(line.count(sorted(x)) for line in comb) == 1:
#     #       surface_ids.append(i)

#     return mesh.cells['tetra'][surface_ids]

def get_elements_within_boundary(mesh, boundary, element_type='triangle'):
    '''
    Function that selects elements inside a boundary closed surface

    Parameters
    ----------
    mesh = mesh object read with meshio module
    boundary_triangle_mesh = triangular mesh (.stl) read with meshio
    element_type : type. The default is 'triangle'.

    Returns
    -------
    element cells

    '''

    nodes = select_nodes_inside_boundary(mesh, boundary)

    element_labels = []
    for k in nodes:
        element_labels += np.where(mesh.cells[element_type] == k)[0].tolist()

    return mesh.cells[element_type][element_labels]


def get_element_set(mesh, physical_group_name, element_type):
    """Gets the elements' id that belong to the physical group.

    Parameters
    ----------

    mesh: [meshio.mesh.Mesh]

    physical_group_name: [string] name of the physical group

    element_type = [string] the type of the element e.g. 'vertex', 'quad',
                   'hexahedron'

    Returns
    -------

    node_id: [np.ndarray] elements id

    To do
    -----

    T1: automatic recognition of the element type

    """
    assert (element_type in ['vertex', 'quad', 'hexahedron'])
    physical_group = mesh.field_data[physical_group_name]
    physical_data = mesh.cell_data_dict['gmsh:physical'][element_type]
    element_indices = np.where(physical_data == physical_group[0])
    return mesh.cells_dict[element_type][element_indices]
