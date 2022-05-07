# -*- coding:utf-8 -*-
# @Time:        7/5/22 3:19 μ.μ.
# @Author:      kostas
# @Email:   krisvas@ece.upatras.gr
# @Filename:    constraints.py
import xml.etree.ElementTree as ET
from utils import to_xml_field

__doc__ = "Contact submodule to create contact between surface pairs"
__all__ = ["Constraints"]


class Constraints:
    """
    Builds an instance of object "Constraints"
    """

    def __init__(self, model):
        self.parent = model
        self.root = None

    def add_cylindrical_joint(self, name, parameters, root=None):
        """Adds a cylindrical joint constraint.

        Parameters
        ----------

        name: [string] name of the element

        parameters: [dictionary] the parameters of the cylindrical joint

        Returns
        -------

        loadcurves: [list] the load curve ids

        """
        if root is None:
            # root = self.constraints
            root = self.parent.rigid
        joint = ET.SubElement(root, 'rigid_connector',
                              attrib={'name': name,
                                      'type': 'rigid cylindrical joint'})
        loadcurves = []
        for key, value in parameters.items():
            if key in ['translation', 'force', 'rotation', 'moment']:
                if value == 0:
                    item = ET.SubElement(joint, key)
                else:
                    item = ET.SubElement(joint, key,
                                         attrib={'lc': str(
                                             self.parent.loadcurve_id)})
                    loadcurves.append(self.parent.loadcurve_id)
                    self.parent.loadcurve_id = self.parent.loadcurve_id + 1

                item.text = str(value)
            else:
                item = ET.SubElement(joint, key)
                item.text = to_xml_field(value)

        return loadcurves

    def add_joint(self, name, parameters, root=None):

        if root is None:
            self.root = self.parent.rigid
        joint = ET.SubElement(self.root, 'rigid_connector',
                              attrib={'name': name,
                                      'type': parameters['type']})
        loadcurves = []
        for key, value in parameters.items():
            if key in ['translation', 'force', 'rotation', 'moment']:
                if value == 0:
                    item = ET.SubElement(joint, key)
                else:
                    item = ET.SubElement(joint, key,
                                         attrib={'lc': str(
                                             self.parent.loadcurve_id)})
                    loadcurves.append(self.parent.loadcurve_id)
                    self.parent.loadcurve_id = self.parent.loadcurve_id + 1

                item.text = str(value)
            if key == 'type':
                pass
            else:
                item = ET.SubElement(joint, key)
                item.text = to_xml_field(value)

        return loadcurves

    def add_rigid_spring(self, name, parameters, root=None):
        """

        Parameters
        ----------
        name: [string] name of the element
        parameters: [dictionary] the parameters of the rigid spring
        root

        Returns
        -------

        """

        if root is None:
            self.root = self.parent.rigid

        spring = ET.SubElement(self.root, 'rigid_connector',
                               attrib={'name': name,
                                       'type': 'rigid spring'})

        for key, value in parameters.items():
            item = ET.SubElement(spring, key)
            item.text = to_xml_field(value)
