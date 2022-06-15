# -*- coding: utf-8 -*-
# @Time    : 20/3/22 9:12 μ.μ.
# @Author  : Kostas Risvas
# @Email   : krisvas@ece.upatras.gr
# @File    : rigid.py
import xml.etree.ElementTree as ET
import copy
from febio_exporter.utils import to_xml_field

__doc__ = "Rigid submodule that is used to create rigid body DoFs"
__all__ = ["Rigid"]


class Rigid:
    """

    """

    def __init__(self, model):
        # self.add_loadcurve = febio_exporter.FEBioExporter.add_loadcurve
        self.parent = model
        self.root = None

    def add_rigid_body_fixed_constraint(self, name, rigid_body_id, constraints,
                                        root=None):
        """Constraint the degrees of freedom of a rigid body.

        Parameters
        ----------

        name: [string] name of the element

        rigid_body_id: [integer] the associated rigid body

        constraints: [list] a list of constraints (e.g., x, y, z, Rx, Ry, Rz)

        root: [ET.SubElement] (default None -> self.boundaries) the root node in
        case that the boundary is attached to some other element (e.g. Step)

        """
        for c in constraints:
            # assert (c in ['x', 'y', 'z', 'Rx', 'Ry', 'Rz'])
            # new in FEBio3
            assert (c in ['Rx', 'Ry', 'Rz', 'Ru', 'Rv', 'Rw'])

        if root is None:
            self.root = self.parent.rigid
        else:
            self.root = root

        constraint_element = ET.SubElement(self.root, 'rigid_constraint',
                                           attrib={'name': name,
                                                   'type': 'fix'})
        rb = ET.SubElement(constraint_element, 'rb')
        rb.text = str(rigid_body_id)
        dofs = ET.SubElement(constraint_element, 'dofs')
        dofs.text = to_xml_field(constraints)

    def add_rigid_body_prescribed_constraint(self, name, parameters,
                                             root=None, loadcurve=True):
        """Adds a prescribed constraint for a particular dof for a rigid body.

        Parameters
        ----------

        name: [string] name of the element
        parameters: [dict] constraint parameters
        root: [ET.SubElement] (default None -> self.boundaries) the root node in
        case that the boundary is attached to some other element (e.g. Step)
        loadcurve: [Boolean]

        Returns
        -------

        loadcurve_id: [integer] the id of the associated load curve, note that
                      the user is responsible for created the loadcurve using
                      add_loadcurve

        """
        constraint_type = parameters["constraint_type"]
        dof = parameters["dof"]
        assert (constraint_type == 'prescribe' or constraint_type == 'force')
        assert (dof in ['Rx', 'Ry', 'Rz', 'Ru', 'Rv', 'Rw'])
        if root is None:
            self.root = self.parent.rigid
        else:
            self.root = root

        prescribed_element = ET.SubElement(self.root, 'rigid_constraint',
                                           attrib={'name': name,
                                                   'type': constraint_type})
        for key, value in parameters.items():
            if key == 'scale':
                if loadcurve:
                    subel = ET.SubElement(prescribed_element, 'value',
                                          attrib={'lc': str(
                                              self.parent.loadcurve_id)})
                    subel.text = value
                    self.parent.loadcurve_id = self.parent.loadcurve_id + 1
                else:
                    subel = ET.SubElement(prescribed_element, 'value')
                    subel.text = value
            elif key == "constraint_type":
                pass
            else:
                subel = ET.SubElement(prescribed_element, key)
                subel.text = value

        return self.parent.loadcurve_id - 1

    #  TODO add description about paramters
    @staticmethod
    def get_rigid_body_prescribed_motion_default_parameters():
        """

        """
        return copy.copy({"rb": "",
                          "dof": "",
                          "scale": str(1),
                          "constraint_type": "prescribe",
                          "relative": str(0)
                          })

    @staticmethod
    def get_rigid_body_prescribed_force_default_parameters():
        """
        FEBio default
        -------------
        load_type: 0
        """
        return copy.copy({"rb": str(0),
                          "dof": "",
                          "scale": str(1),
                          "constraint_type": "force",
                          "load_type": str(0)})
