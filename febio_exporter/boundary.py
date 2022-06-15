# -*- coding: utf-8 -*-
# @Time    : 20/3/22 9:36 μ.μ.
# @Author  : Kostas Risvas
# @Email   : krisvas@ece.upatras.gr
# @File    : boundary.py
import xml.etree.ElementTree as ET
from febio_exporter.utils import to_xml_field


class Boundary:
    """

    """

    def __init__(self, model):
        # self.add_loadcurve = febio_exporter.FEBioExporter.add_loadcurve
        self.parent = model
        self.root = None

    def add_deformable_boundary_conditions(self, name, dofs, node_set_name,
                                           scale_factor,
                                           relative_mode=False,
                                           root=None):

        """Adds a fixed or prescribed constraint to the dofs of
            a nodeset or surface

        Parameters
        ----------

        name: [string] name of the element

        dofs: [dictionary] the degrees of freedom of the constraints (e.g, x, y,
              z, Rx, Ry, Rz)

        node_set_name: [string] the name of the nodeset

        scale_factor: [integer] the curve scaling factor

        relative_mode: [boolean] flag for relative to previous analysis
            step constraints

        root: [ET.SubElement] (default None -> self.boundaries) the root node in
        case that the boundary is attached to some other element (e.g. Step)

        Returns
        -------

        loadcurve_id: [list] the ids of the associated load curves, note that
                      the user is responsible for creating the loadcurves using
                      add_loadcurve

        """
        keys = list(dofs.keys())
        values = list(dofs.values())

        for dof in dofs:
            assert (dof in ['x', 'y', 'z'])
        if root is None:
            self.root = self.parent.boundaries
        else:
            self.root = root

        curve_ids = []
        for i in keys:
            if dofs[i] == 'fixed':
                ET.SubElement(self.root, 'fix',
                              attrib={'bc': i,
                                      'name': name,
                                      'node_set': node_set_name})
            elif dofs[i] == 'prescribed':
                constraint = ET.SubElement(self.root, 'bc',
                                           attrib={'name': name,
                                                   'type': "prescribe",
                                                   'node_set': node_set_name})
                dof = ET.SubElement(constraint, 'dof')
                dof.text = i
                scale_el = ET.SubElement(constraint, 'scale', attrib={
                    'lc': str(self.parent.loadcurve_id)})
                scale_el.text = str(scale_factor)
                curve_ids.append(self.parent.loadcurve_id)
                self.parent.loadcurve_id = self.parent.loadcurve_id + 1
                relative = ET.SubElement(constraint, 'relative')
                relative.text = str(int(relative_mode))

        return curve_ids

    def add_deformable_prescribed_displacement(self, name, dof,
                                               node_set_name,
                                               scale_factor, root=None):
        """Adds prescribed displacement constraint.

        Parameters
        ----------

        name: [string] the name of the elements

        dof: [string] the prescribed dof constraints (e.g., x, y, z)

        node_set_name: [string] the name of the node set

        scale_factor: [float] scaling factor of the load curve

        root: [ET.SubElement] (default None -> self.boundaries) the root node in
        case that the boundary is attached to some other element (e.g. Step)

        Returns
        -------

        loadcurve_id: [integer] the associated load curve id

        """
        assert (dof in ['x', 'y', 'z'])
        if root is None:
            self.root = self.parent.boundaries
        else:
            self.root = root

        constraint_element = ET.SubElement(self.root, 'prescribe',
                                           attrib={'name': name,
                                                   'bc': dof,
                                                   'node_set': node_set_name})
        scale = ET.SubElement(constraint_element, 'scale',
                              attrib={'lc': str(self.parent.loadcurve_id)})
        scale.text = str(scale_factor)
        relative = ET.SubElement(constraint_element, 'relative')
        relative.text = str(0)
        self.parent.loadcurve_id += 1
        return self.parent.loadcurve_id - 1

    def add_rigid_connector(self, name, rigid_body_id, node_set_name,
                            root=None):
        """Connect the node set of a deformable to a rigid body.

        Parameters
        ----------

        name: [string] name of the element

        rigid_body_id: [integer] the associated rigid body

        node_set_name: [string] the name of the note set that belongs to the
                       deformable body

        root: [ET.SubElement] (default None -> self.boundaries) the root node
        in case that the boundary is attached to some other element (e.g.
        Step)

        """
        if root is None:
            self.root = self.parent.boundaries
        else:
            self.root = root

        bc = ET.SubElement(self.root, 'bc',
                           attrib={'name': name,
                                   'type': 'rigid',
                                   'node_set': node_set_name})
        rb = ET.SubElement(bc, 'rb')
        rb.text = str(rigid_body_id)

    def add_deformable_fixed_displacement(self, name, constraints,
                                          node_set_name, root=None):
        """Adds fixed displacement constraint.

        Parameters
        ----------

        name: [string] the name of the elements

        constraints: [list] a list of constraints (e.g., x, y, z)

        node_set_name: [string] the name of the node set

        root: [ET.SubElement] (default None -> self.boundaries) the root node in
        case that the boundary is attached to some other element (e.g. Step)

        """
        # for c in constraints:
        #     assert(c in ['x', 'y', 'z'])

        if root is None:
            self.root = self.parent.boundaries
        else:
            self.root = root

        ET.SubElement(self.root, 'fix',
                      attrib={'name': name,
                              'bc': to_xml_field(constraints),
                              'node_set': node_set_name})

    # if relative_mode:
    #     constraint = ET.SubElement(prescribed_element, 'prescribed',
    #                                attrib={'type': 'relative',
    #                                        'bc': dof,
    #                                        'lc': str(self.loadcurve_id)
    #                                        })
    #     constraint.text = str(scale_factor)
    #     self.loadcurve_id = self.loadcurve_id + 1
    #
    # else:
    #     constraint = ET.SubElement(prescribed_element, constraint_type,
    #                                attrib={'bc': dof,
    #                                        'lc': str(self.loadcurve_id)})
    #     constraint.text = str(scale_factor)
    #     self.loadcurve_id = self.loadcurve_id + 1

    # return self.loadcurve_id - 1
