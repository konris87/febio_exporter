# -*- coding:utf-8 -*-
# @Time:        7/5/22 3:45 μ.μ.
# @Author:      kostas
# @Email:   krisvas@ece.upatras.gr
# @Filename:    material.py
import copy
import xml.etree.ElementTree as ET
from utils import to_xml_field

__doc__ = "Material submodule to create a new material connectivity. " \
          "FEBio default Material parameters are provided as static functions"
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

    @staticmethod
    def get_default_fung_orthotropic_parameters():
        """Gets the Fung orthotroptic meniscus materials parameters.

        Returns
        -------

        parameters: [dictionary]

        """
        return copy.copy({
            'type': 'Fung orthotropic',
            'density': 0,
            'E1': 0,
            'E2': 0,
            'E3': 0,
            'G12': 0,
            'G23': 0,
            'G31': 0,
            'v12': 0,
            'v23': 0,
            'v31': 0,
            'c': 0,
            'k': 0
        })

    @staticmethod
    def get_default_mooney_rivlin_parameters():
        """Gets the default Mooney-Rivlin materials parameters.

        Returns
        -------

        parameters: [dictionary]

        """
        return copy.copy({
            'type': 'Mooney-Rivlin',
            'density': 0,
            'c1': 0,
            'c2': 0,
            'k': 0
        })

    @staticmethod
    def get_default_rigid_body_parameters():
        """Gets default rigid-body materials parameters.

        Returns
        -------

        parameters: [dictionary]

        """
        return copy.copy({
            'type': 'rigid body',
            'density': 0,
            'center_of_mass': [0, 0, 0]
        })
