# -*- coding: utf-8 -*-
# @Time    : 20/3/22 6:27 μ.μ.
# @Author  : Kostas Risvas
# @Email   : krisvas@ece.upatras.gr
# @File    : discrete.py

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
from utils import to_xml_field


__doc__ = "Discrete submodule to append discrete elements, such as linear or " \
          "nonlinear springs."
__all__ = ["Discrete"]


class Discrete:
    """
    Build an instance of object "Discrete"
    """

    def __init__(self, model):
        self.parent = model
        self.discrete_id = 1

    def add_discrete_element(self, group_name,
                             origin_geometry, origin_node_set,
                             origin_node_offset, insertion_geometry,
                             insertion_node_set, insertion_node_offset, ref_ax,
                             young_mod, cross_section, ref_strain,
                             mri_length, offset, linearity, plot_curve=True):
        """

        Parameters
        ----------
        group_name
        origin_geometry
        origin_node_set
        origin_node_offset
        insertion_geometry
        insertion_node_set
        insertion_node_offset
        ref_ax
        young_mod
        cross_section
        ref_strain
        mri_length
        offset
        linearity
        plot_curve

        Returns
        -------

        """

        origin_points = sort_sets(origin_geometry, origin_node_set, ref_ax)
        insertion_points = sort_sets(insertion_geometry, insertion_node_set,
                                     ref_ax)
        spring_num = min(origin_points.shape[0], insertion_points.shape[0])
        w = 0
        springs_length = []
        area = cross_section
        if linearity:
            if cross_section is None:
                stiffness = young_mod
                origin_points = sort_sets(origin_geometry, origin_node_set,
                                          ref_ax)
                insertion_points = sort_sets(insertion_geometry,
                                             insertion_node_set,
                                             ref_ax)
                # calculate the number of springs. Since 1 to 1 connection is
                # desired the maximum number of springs is equal to the total
                # number of nodes of the smallest node_set.
                spring_num = min(origin_points.shape[0],
                                 insertion_points.shape[0])
                # print(spring_num)
                total_length = []
                for i in range(0, spring_num):
                    length = np.linalg.norm(
                        origin_points[i, 1:4] - insertion_points[i, 1:4])
                    total_length.append(length)
                    # print(length)
                    # spring constant:
                    spring_constant = stiffness / spring_num
                    # print(spring_constant)
                    self.add_spring(group_name + str(i) + '_' + str(w),
                                    int(origin_points[
                                            i, 0]) + origin_node_offset,
                                    int(insertion_points[
                                            i, 0]) + insertion_node_offset,
                                    spring_constant,
                                    'tension-only linear spring')
                    w += 1

                average_length = np.average(np.asarray(total_length))
                print("The average spring length is {}".format(average_length))

            else:
                for i in range(1, spring_num + 1):
                    length = np.linalg.norm(
                        origin_points[i - 1, 1:4] -
                        insertion_points[i - 1, 1:4])
                    springs_length.append(length)
                    # spring constant:
                    spring_constant = (area * young_mod) / (spring_num * length)
                    # print(spring_constant)
                    spring_loadcurve_id = self.add_nonlinear_spring(
                        group_name + str(i - 1) + '_' + str(w),
                        int(origin_points[i - 1, 0]) + origin_node_offset,
                        int(insertion_points[i - 1, 0]) + insertion_node_offset,
                        1)
                    L = np.linspace(0, 200, 221)
                    force, displacement = stress_strain_relationship(
                        length,
                        spring_constant,
                        L,
                        offset,
                        mode='linear')
                    # print curve for validation
                    plt.figure(figsize=(14, 6))
                    plt.plot(displacement, force, marker='',
                             label=str(ref_strain))
                    plt.legend()
                    plt.show()
                    self.parent.add_loadcurve(spring_loadcurve_id, 'linear',
                                              'constant',
                                              displacement, force)
                    w += 1
        else:
            k = young_mod * area
            displacements = []
            forces = []
            strains = []
            for i in range(1, spring_num + 1):
                length = np.linalg.norm(
                    origin_points[i - 1, 1:4] - insertion_points[i - 1, 1:4])
                # pcl mesh length 41 use case
                # offset = np.abs(36.7 - length)
                # offset = np.abs(39 - length)
                if mri_length != 0:
                    offset = np.abs(mri_length - length)
                # print(offset)
                # print(length)
                springs_length.append(length)
                # print("The length of the {} is {}".format(group_name,length))
                spring_constant = k / spring_num
                # print(spring_constant)
                # print(spring_constant)
                spring_loadcurve_id = self.add_nonlinear_spring(
                    group_name + str(i - 1) + '_' + str(w),
                    int(origin_points[i - 1, 0]) + origin_node_offset,
                    int(insertion_points[i - 1, 0]) + insertion_node_offset,
                    1)
                # reference length
                Lr = length / (ref_strain + 1)
                L = np.round(np.linspace(0, 10, 101), 3)
                force, displacement = stress_strain_relationship(
                    Lr,
                    spring_constant,
                    L,
                    offset,
                    mode='non_linear')
                force[0] = 0
                force = np.round(force, 3)
                # print(strain,stress)
                self.parent.add_loadcurve(spring_loadcurve_id, 'linear',
                                          'constant',
                                          displacement, force)
                w += 1
                displacements.append(displacement)
                forces.append(force)
                strains.append(ref_strain)
            # print("spring_constant: {}".format(spring_constant))
            # print("spring_number: {}".format(spring_num))
            if plot_curve:
                plt.figure(figsize=(14, 6))
                for i in range(len(displacements)):
                    plt.plot(displacements[i], forces[i], marker='x',
                             label=str(strains[i]))
                plt.legend(loc='right', ncol=1,
                           bbox_to_anchor=(1, 0.5),
                           prop={'weight': 'bold', 'size': 8})
                plt.title(group_name)
                plt.show()
            average_length = np.average(np.asarray(springs_length))
            print("Stiffness parameter K (N): {}".format(k))
            print("The average spring length is {}".format(average_length))

    def add_nonlinear_spring(self, name, node_a, node_b, scale_factor=1):
        """

        Parameters
        ----------
        name : [string] name of the element

        node_a : [integer] node A id

        node_b : [integer] node B id

        scale_factor : spring force scale factor, default=1

        Returns
        -------
        loadcurve_id: [integer] (default None) the spring force-displacement
        must point loadcurve_id

        """
        if self.parent.discrete is None:
            self.parent.discrete = ET.SubElement(self.parent.root, 'Discrete')

        discrete_set = ET.SubElement(self.parent.geometries, 'DiscreteSet',
                                     attrib={'name': name})
        discrete_element = ET.SubElement(discrete_set, 'delem')
        discrete_element.text = to_xml_field([node_a, node_b])

        discrete_material = ET.SubElement(self.parent.discrete,
                                          'discrete_material',
                                          attrib={'id': str(self.discrete_id),
                                                  'name': name,
                                                  'type': 'nonlinear spring'})
        force_elem = ET.SubElement(discrete_material, 'force',
                                   attrib={'lc': str(self.parent.loadcurve_id)})
        force_elem.text = str(scale_factor)
        self.parent.loadcurve_id = self.parent.loadcurve_id + 1

        ET.SubElement(self.parent.discrete, 'discrete',
                      attrib={'dmat': str(self.discrete_id),
                              'discrete_set': name})
        self.discrete_id += 1
        return self.parent.loadcurve_id - 1

    def add_menisci_springs(self, group_name, origin_geometry,
                            origin_node_set,
                            origin_node_offset, insertion_geometry,
                            insertion_node_set, insertion_node_offset,
                            constant, mode, all=None):
        """

        Parameters
        ----------
        group_name
        origin_geometry
        origin_node_set
        origin_node_offset
        insertion_geometry
        insertion_node_set
        insertion_node_offset
        constant
        mode
        all

        Returns
        -------

        """
        spring_number = len(origin_node_set) * len(insertion_node_set)
        # print(spring_number)
        for i, origin_node in enumerate(origin_node_set):
            origin_position = origin_geometry.points[origin_node, :]
            for j, insertion_node in enumerate(insertion_node_set):
                insertion_position = insertion_geometry.points[
                                     insertion_node, :]

                # L = np.linalg.norm(origin_position - insertion_position)
                spring_constant = round(constant / spring_number, 2)
                self.add_spring(group_name + str(i) + '_' + str(j),
                                origin_node + origin_node_offset,
                                insertion_node + insertion_node_offset,
                                spring_constant, mode)

        print(spring_number, spring_constant)

    def add_spring(self, name, node_a, node_b, k, spring_type):
        """Adds a spring element.

        Parameters
        ----------

        name: [string] name of the element

        node_a: [integer] node A id

        node_b: [integer] node B id

        k: [float] stiffness

        spring_type: [string] 'linear spring' or 'tension-only linear spring'

        """
        if self.parent.discrete is None:
            self.parent.discrete = ET.SubElement(self.parent.root, 'Discrete')

        discrete_set = ET.SubElement(self.parent.geometries, 'DiscreteSet',
                                     attrib={'name': name})
        discrete_element = ET.SubElement(discrete_set, 'delem')
        discrete_element.text = to_xml_field([node_a, node_b])
        discrete_material = ET.SubElement(self.parent.discrete,
                                          'discrete_material',
                                          attrib={'id': str(self.discrete_id),
                                                  'name': name,
                                                  'type': spring_type})
        youngs_modulus = ET.SubElement(discrete_material, 'E')
        youngs_modulus.text = str(k)
        ET.SubElement(self.parent.discrete, 'discrete',
                      attrib={'dmat': str(self.discrete_id),
                              'discrete_set': name})
        self.discrete_id += 1


def sort_sets(mesh, node_set, ax):
    """
    Sort the node_sets based on the specified coordinate

    Parameters
    ------------
    mesh: geometry

    node_set: a list of selected nodes

    ax: defines the sorting coordinate axis

    Returns
    ------------
    array1: a numpy array with the node ids sorted by the desired axis.

    """
    node_list = []
    for i in node_set:
        node_list.append(mesh.points[i])
    coords = np.array(node_list)
    array = np.insert(coords, 0, node_set, axis=1)
    array1 = array[np.argsort(array[:, ax])]
    return array1


def stress_strain_relationship(initial_length, k, L, offset, mode):
    """
    A function that calculates the stress - strain relationship of a non linear
        spring, based on the Blankevoort equation. It returns the force -
        displacement (FEBio requirement).

    Parameters
    ----------
    initial_length : spring resting length

    k : spring stiffness

    L : displacement

    offset: [float] offset to shift curve to allow different zero slack length

    mode: [string] linear or non_linear

    Returns
    -------
    stress : [numpy array]

    strain : [numpy array]
    """

    assert mode in ['linear', 'non_linear']
    displacement = L
    if mode == 'non_linear':
        constant, disp, L0 = sp.symbols('k disp L0')

        # f = sp.Piecewise(
        #     (0, e<0),
        #     (constant*(e-0.03), e>0.06),
        #     (0.25*constant*(e**2/0.03), True)
        # )

        f = sp.Piecewise(
            (0, disp < 0),
            (constant * ((disp / L0) - 0.03), disp > 0.06 * L0),
            (0.25 * constant * (disp ** 2) / (0.03 * (L0 ** 2)), True))
        # sp.pprint(f)
        force_func = sp.lambdify((constant, disp, L0), f, "numpy")
        force = force_func(k, displacement, initial_length)
        displacement += offset

    else:
        constant, disp = sp.symbols('k disp')

        f = sp.Piecewise(
            (0, disp <= offset),
            (constant * (disp - offset), True)
        )
        # sp.pprint(f)

        force_func = sp.lambdify((constant, disp), f, "numpy")
        force = force_func(k, displacement)
        greater_than_zero_indices = np.where(displacement > 0)

        displacement = displacement[greater_than_zero_indices]
        displacement = np.insert(displacement, 0, 0)
        force = force[greater_than_zero_indices]
        force = np.insert(force, 0, 0)

    return force, displacement
