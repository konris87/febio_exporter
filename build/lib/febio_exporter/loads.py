# -*- coding: utf-8 -*-
# @Time    : 20/3/22 9:25 μ.μ.
# @Author  : Kostas Risvas
# @Email   : krisvas@ece.upatras.gr
# @File    : loads.py
import xml.etree.ElementTree as ET
from febio_exporter.utils import to_xml_field


class Loads:
    """

    """

    def __init__(self, model):
        # self.add_loadcurve = febio_exporter.FEBioExporter.add_loadcurve
        self.parent = model

    def add_surface_load(self, name, parameters, surface_name, scale_factor,
                         root=None):
        """

        Parameters
        ----------
        root
        name : [string] the name of the element

        parameters : [dictionary] the parameters of the surface load

        surface_name : the name of the surface on which the load is applied

        scale_factor : a scale factor, when the load is applied through a

        Returns
        -------
        loadcurve_id: [integer] the associated load curve id

        """
        # assert(parameters['type'] in ['pressure', 'traction'])
        if root is None:
            root = self.parent.loads
        load_element = ET.SubElement(root, 'surface_load',
                                     attrib={'name': name,
                                             'type': parameters['type'],
                                             'surface': surface_name})

        if parameters['type'] == 'pressure':
            scale = ET.SubElement(
                load_element, 'pressure',
                attrib={'lc': str(self.parent.loadcurve_id + 1)})
            scale.text = str(scale_factor)
            linear = ET.SubElement(load_element, 'linear')
            linear.text = str(parameters['linear'])
            stiffness = ET.SubElement(load_element, 'symmetric_stiffness')
            stiffness.text = str(parameters['stiffness'])

        elif parameters['type'] == 'traction':
            scale = ET.SubElement(
                load_element, 'scale',
                attrib={'lc': str(self.parent.loadcurve_id + 1)})
            scale.text = str(scale_factor)
            traction = ET.SubElement(load_element, 'traction')
            traction.text = to_xml_field(parameters['traction'])

        self.parent.loadcurve_id += 1
        return self.parent.loadcurve_id

    def add_nodal_load(self, name, dof, node_set_name, scale_factor):
        """Adds a nodal load.

        Parameters
        ----------

        name: [string] the name of the elements

        dof: [string] the prescribed dof constraints (e.g., x, y, z)

        node_set_name: [string] the name of the node set

        scale_factor: [float] scaling factor of the load curve

        Returns
        -------

        loadcurve_id: [integer] the associated load curve id

        """
        assert (dof in ['x', 'y', 'z'])
        load_element = ET.SubElement(self.parent.loads, 'nodal_load',
                                     attrib={'name': name,
                                             'bc': dof,
                                             'node_set': node_set_name})
        scale = ET.SubElement(load_element, 'scale',
                              attrib={'lc': str(self.parent.loadcurve_id)})
        scale.text = str(scale_factor)
        self.parent.loadcurve_id = self.parent.loadcurve_id + 1
        return self.parent.loadcurve_id - 1
