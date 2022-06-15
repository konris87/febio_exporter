# -*- coding:utf-8 -*-
# @Time:        7/5/22 3:30 μ.μ.
# @Author:      kostas
# @Email:   krisvas@ece.upatras.gr
# @Filename:    mesh.py
import xml.etree.ElementTree as ET
from febio_exporter.utils import to_xml_field

__doc__ = "Mesh submodule to create mesh data, nodal coordinates and " \
          "connectivity."
__all__ = ["Mesh"]


class Mesh:
    """
    Creates an instance of a "Mesh" object
    """

    def __init__(self, model):
        self.parent = model
        self.root = None

    def create_part(self, name, scale=(1, 1, 1), rotate=(0, 0, 0, 1),
                    translate=(0, 0, 0)):
        """Creates an xml geometry part.

        Parameters
        ----------

        name: [string] name of the element

        scale: [list 3D] geometry scaling

        rotate: [list 4D] geometry rotation (quaternion)

        translate: [list 3D] geometry translation

        Returns
        -------

        part: [xml SubElement]

        """
        part = ET.SubElement(self.parent.geometries, 'Part',
                             attrib={'name': name})
        # create instance of the part
        instance = ET.SubElement(self.parent.geometries, 'Instance',
                                 attrib={'part': name})
        scale_element = ET.SubElement(instance, 'scale')
        scale_element.text = to_xml_field(scale)
        rotate_element = ET.SubElement(instance, 'rotate')
        rotate_element.text = to_xml_field(rotate)
        translate_element = ET.SubElement(instance, 'translate')
        translate_element.text = to_xml_field(translate)
        return part

    def add_part(self, name, material_id, element_type, nodes, elements,
                 scale=(1, 1, 1), rotate=(0, 0, 0, 1), translate=(0, 0, 0),
                 construct_part=False, root=None):
        """Adds a part to the geometries of the model.

        Parameters
        ----------

        root
        name: [string] name of the element

        material_id: [integer] the associated material id

        element_type: [string] the name of the material (e.g., hex8, tet4)

        nodes: [np.ndarray, nodes x dim]

        elements: [2d array, elements x
               element_type]

        scale: [list 3D] geometry scaling

        rotate: [list 4D] geometry rotation (quaternion)

        translate: [list 3D] geometry translation

        construct_part: [Boolean, default=false] construct part or append to
                        geometry

        Returns
        -------

        tuple:

            part: [xml SubElement]

            node_offset: [integer] the id of the first node that belongs to
                         this element (since may contain many geometries)

        To do
        ----

        T1: fix bug with node sets when working with parts.

        T2: infer the element type from the input.

        T3: add support for nodes sets and other elements.

        """
        part = None
        if construct_part:
            part = self.create_part(name, scale, rotate, translate)
            raise NotImplementedError('Not working properly with node sets')
        else:
            part = self.parent.geometries

        node_offset = self.add_nodes(name + '_nodes', nodes, part)
        self.add_element(name + '_elements', material_id, element_type,
                         elements, node_offset, part)

        return part, node_offset

    def add_surface(self, name, element_type, elements, node_offset,
                    root=None):
        """Adds a surface set.

        Parameters
        ----------

        name: [string] name of the element set

        element_type: [string] the name of the material (e.g., quad4)

        elements: [2d array, elements x element_type] an array of elements

        node_offset: [integer] the id of the first node that belongs to this
                     element (since may contain many geometries)

        root: [xml SubElement, None] if none they are appended to Geometry

        To do
        -----

        T1: add support for other element types (needs testing)

        """
        assert (element_type in ['quad4', 'tri3'])
        if root is None:
            self.root = self.parent.geometries
        else:
            self.root = root

        elements = elements + node_offset
        surface_element = ET.SubElement(
            self.root, 'Surface', attrib={'name': name})
        for i, e in enumerate(elements):
            element = ET.SubElement(surface_element, element_type,
                                    attrib={'id': str(i + 1)})
            element.text = to_xml_field(e)

    def add_node_set(self, name, node_set, node_offset, root=None):
        """Adds a note set.

        Parameters
        ----------

        name: [string] name of the element

        node_set: [list] node id values

        node_offset: [integer] the id of the first node that belongs to this
                     element (since may contain many geometries)

        root: [xml SubElement, None] if none they are appended to Geometry

        """
        if root is None:
            self.root = self.parent.geometries
        else:
            self.root = root

        node_set_element = ET.SubElement(self.root, 'NodeSet',
                                         attrib={'name': name})
        for n in node_set.flatten():
            ET.SubElement(node_set_element, 'node',
                          attrib={'id': str(n + node_offset)})

    def add_domain(self, name, material_name, domain, root=None):
        """
        Adds a shell domain entry

        Parameters
        ----------
        name
        material_name
        domain
        root

        Returns
        -------

        """
        domain_el = ET.SubElement(
            self.parent.domains, "{}Domain".format(domain),
            attrib={'name': '{}_elements'.format(name),
                    'mat': material_name})
        if domain == 'Shell':
            shell_el = ET.SubElement(domain_el, 'shell_normal_nodal')
            shell_el.text = '1'

    def add_element(self, name, material_id, element_type, elements,
                    node_offset, root=None):
        """Adds an element to the model.

        Parameters
        ----------

        name: [string] name of the element

        material_id: [integer] the associated material id

        element_type: [string] the name of the material (e.g., hex8, tri3)

        elements: [np.ndarray, elements x element_type] use zero based indexing

        node_offset: [integer] the id of the first node that belongs to this
                     element (since may contain many geometries)

        root: [xml SubElement, None] if none they are appended to Geometry

        To do
        -----

        T1: add support for other element types (needs testing)

        """
        assert (element_type in ['hex8', 'tri3', 'tet4'])
        if root is None:
            self.root = self.parent.geometries
        else:
            self.root = root

        elements_element = ET.SubElement(self.root, 'Elements',
                                         attrib={'type': element_type,
                                                 'mat': str(material_id),
                                                 'name': name})

        elements = elements + node_offset
        element_offset = self.parent.element_id
        for e in elements:
            element = ET.SubElement(elements_element, 'elem',
                                    attrib={'id': str(self.parent.element_id)})
            element.text = to_xml_field(e)
            self.parent.element_id = self.parent.element_id + 1

        return element_offset

    def add_nodes(self, name, nodes, root=None):
        """Adds a set of nodes to the model.

        Parameters
        ----------

        name: [string] name of the node set

        nodes: [np.ndarray, nodes x dim]

        root: [xml SubElement, None] if none they are appended to Geometry

        """
        if root is None:
            self.root = self.parent.geometries
        else:
            self.root = root

        nodes_element = ET.SubElement(self.root, 'Nodes',
                                      attrib={'name': name})
        node_offset = self.parent.node_id
        for n in nodes:
            node_element = ET.SubElement(
                nodes_element, 'node',
                attrib={'id': str(self.parent.node_id)})
            node_element.text = to_xml_field(n)
            self.parent.node_id = self.parent.node_id + 1

        return node_offset
