# -*- coding:utf-8 -*-
# @Time:        24/10/22 8:22 μ.μ.
# @Author:      kostas
# @Email:   krisvas@ece.upatras.gr
# @Filename:    meshdata.py
import xml.etree.ElementTree as ET
from febio_exporter.utils import to_xml_field

__doc__ = "Mesh submodule to add mesh data variables such as ElementData. "
__all__ = ["MeshData"]


class MeshData:
    """
    Creates an instance of a "Mesh" object
    """

    def __init__(self, model):
        self.parent = model
        self.root = None

    def add_element_data(
            self, name, element_set,
            element_set_name,
            element_offset, value, val_type, root=None):
        """
        Function that adds ElementData for an element set

        Parameters
        ----------
        root
        name
        element_set
        element_set_name
        element_offset
        value
        val_type

        Returns
        -------

        """
        # assert (parameter in ['fiber'])
        if root is None:
            self.root = self.parent.mesh_data
        else:
            self.root = root

        data_el = ET.SubElement(
            self.root, "ElementData",
            attrib={
                "name": name,
                "datatype": val_type,
                "elem_set": element_set_name,
            })
        for idx, element in enumerate(element_set):
            el = ET.SubElement(
                data_el, "e",
                attrib={
                    "lid": str(idx + 1)
                    # "lid": str(int(element) + element_offset)
                }
            )
            el.text = to_xml_field(value[idx])
