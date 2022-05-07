# -*- coding:utf-8 -*-
# @Time:        7/5/22 3:45 μ.μ.
# @Author:      kostas
# @Email:   krisvas@ece.upatras.gr
# @Filename:    material.py

import xml.etree.ElementTree as ET
from utils import to_xml_field

__doc__ = "Material submodule to create a new material connectivity. " \
          "FEBio default Material parameters are inside the material library " \
          "directory"
__all__ = ["Material"]


class Material:
    """
    Creates an instance of a "Material" object
    """

    def __init__(self, model):
        self.parent = model
        self.root = None

    def add_material(self, name, parameters):
        """Adds a material based on the type of the parameters.

        name: [string] the name of the material

        parameters: [dictionary] parameters

        Returns
        -------

        material_id: [integer] the material's id

        """
        mat = ET.SubElement(self.parent.materials, 'material',
                            attrib={'id': str(self.parent.material_id),
                                    'name': name,
                                    'type': parameters['type']})
        for key, value in parameters.items():
            if key == 'type':
                pass
            elif key == 'elastic':
                el_item = ET.SubElement(
                    mat, key, attrib={'type': value['type']})
                for el_key, el_value in value.items():
                    if el_key == 'type':
                        pass
                    elif el_key == 'fiber':
                        elas_item = ET.SubElement(el_item, el_key,
                                                  attrib={'type': 'local'})
                        elas_item.text = to_xml_field(el_value)
                    else:
                        elas_item = ET.SubElement(el_item, el_key)
                        elas_item.text = to_xml_field(el_value)
            elif key == 'prestrain':
                pre_item = ET.SubElement(
                    mat, key, attrib={'type': value['type']})
                for el_key, el_value in value.items():
                    if el_key == 'type':
                        pass
                    elif el_key == 'F0':
                        f0 = ET.SubElement(pre_item, 'F0',
                                           attrib={'type': 'map'})
                        f0.text = to_xml_field(el_value['val'])
                    else:
                        pres_item = ET.SubElement(pre_item, el_key)
                        pres_item.text = to_xml_field(el_value)
            elif key == 'fiber':
                item = ET.SubElement(mat, key, attrib={'type': 'local'})
                item.text = to_xml_field(value)
            else:
                item = ET.SubElement(mat, key)
                item.text = to_xml_field(value)

        self.parent.material_id = self.parent.material_id + 1

        if 'active_contraction' in parameters.keys():
            return self.parent.material_id - 1, self.parent.loadcurve_id - 1
        else:
            return self.parent.material_id - 1
