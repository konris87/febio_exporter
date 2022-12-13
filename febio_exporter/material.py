# -*- coding:utf-8 -*-
# @Time:        7/5/22 3:45 μ.μ.
# @Author:      kostas
# @Email:   krisvas@ece.upatras.gr
# @Filename:    material.py
import copy
import xml.etree.ElementTree as ET
from febio_exporter.utils import to_xml_field

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
        self.material = None

    def add_material(self, name, parameters):
        """Adds a material based on the type of the parameters.

        name: [string] the name of the material

        parameters: [dictionary] parameters

        Returns
        -------

        material_id: [integer] the material's id

        """
        mat = ET.SubElement(self.parent.materials, 'material',
                            attrib={'id': str(self.parent.material_id + 1),
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
                        for subel_key, subel_value in el_value.items():
                            item = ET.SubElement(el_item, el_key,
                                                 attrib={'type': subel_key})
                            item.text = to_xml_field(subel_value)
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
                        f0 = ET.SubElement(
                            pre_item, el_key, )
                        # attrib={'type': value['type']})
                        f0.text = to_xml_field(el_value)
                    elif el_key == 'stretch':
                        stretch_el = ET.SubElement(
                            pre_item, 'stretch', attrib={
                                'lc': str(self.parent.loadcurve_id)})
                        stretch_el.text = str(1)
                        self.parent.loadcurve_id = self.parent.loadcurve_id + 1
                        print(self.parent.loadcurve_id)
                    elif el_key == 'isochoric':
                        iso_el = ET.SubElement(
                            pre_item, 'isochoric'
                        )
                        iso_el.text = str(el_value)

            elif key == 'fiber':
                for el_key, el_value in value.items():
                    item = ET.SubElement(mat, key, attrib={'type': el_key})
                    item.text = to_xml_field(el_value)

            elif key == 'mat_axis':
                item = ET.SubElement(mat, key, attrib={'type': value['type']})
                for el_key, el_value in value.items():
                    if el_key == 'type':
                        pass
                    else:
                        subelm = ET.SubElement(item, el_key)
                        subelm.text = to_xml_field(el_value)
            else:
                item = ET.SubElement(mat, key)
                item.text = to_xml_field(value)

        self.parent.material_id = self.parent.material_id + 1

        if 'prestrain' in parameters.keys():
            return self.parent.material_id - 1, self.parent.loadcurve_id - 1
        else:
            return self.parent.material_id - 1

    def add_rigid_body_material(self, name, parameters):
        """
        Function that adds a rigid body material

        Parameters
        ----------
        name: [string] material name
        parameters: [dictionary] material parameters

        Returns
        -------

        """

        material_el = ET.SubElement(
            self.parent.materials, 'material',
            attrib={'id': str(self.parent.material_id + 1),
                    'name': name,
                    'type': parameters['type']})

        for key, value in parameters.items():
            if key == 'type':
                pass
            else:
                item = ET.SubElement(material_el, key)
                item.text = to_xml_field(value)

        self.parent.material_id += 1

        return self.parent.material_id

    def add_prestrain_material(self, name, parameters):
        """

        Parameters
        ----------
        name
        parameters

        Returns
        -------

        """
        assert parameters['prestrain']['type'] in [
            'prestrain gradient', 'in-situ stretch']

        mat = ET.SubElement(
            self.parent.materials, 'material',
            attrib={'id': str(self.parent.material_id + 1),
                    'name': name,
                    'type': parameters['type']})

        for key, value in parameters.items():
            if key == 'type':
                pass
            elif key == 'elastic':
                elem = ET.SubElement(
                    mat, key, attrib={'type': value['type']})
                for el_key, el_value in value.items():
                    if el_key == 'type':
                        pass
                    elif el_key == 'fiber':
                        fiber_item = ET.SubElement(
                            elem, el_key, attrib={'type': el_value['type']})
                        fiber_item.text = to_xml_field(el_value['value'])
                    elif el_key == 'active_contraction':
                        pass
                    else:
                        el_item = ET.SubElement(elem, el_key)
                        el_item.text = str(el_value)
            elif key == 'prestrain':
                elem = ET.SubElement(
                    mat, 'prestrain', attrib={'type': value['type']}
                )
                for el_key, el_value in value.items():
                    if el_key == 'type':
                        pass
                    elif el_key == 'F0':
                        if el_value["type"] is None:
                            f0 = ET.SubElement(elem, el_key)
                            f0.text = to_xml_field(el_value["value"])
                        elif el_value["type"] == "map":
                            f0 = ET.SubElement(
                                elem, el_key, attrib={"type": "map"})
                            f0.text = el_value["value"]
                    elif el_key == 'stretch':
                        if el_value["type"] is None:
                            stretch_el = ET.SubElement(
                                elem, 'stretch', attrib={
                                    'lc': str(self.parent.loadcurve_id + 1)})
                            stretch_el.text = str(1)
                            self.parent.loadcurve_id += 1
                            print(self.parent.loadcurve_id)

                        elif el_value["type"] == "map":
                            stretch_el = ET.SubElement(
                                elem, el_key, attrib={"type": "map"})
                            stretch_el.text = el_value["value"]

                    elif el_key == 'isochoric':
                        iso_el = ET.SubElement(
                            elem, 'isochoric'
                        )
                        iso_el.text = str(el_value)
            else:
                elem = ET.SubElement(mat, key)
                elem.text = to_xml_field(value)

        self.parent.material_id += 1

        return self.parent.material_id, self.parent.loadcurve_id

    def add_trans_iso_up_mooney_rivlin_model(self, name, parameters):
        """
        Function that adds the trans iso uncoupled mooney rivlin model
        Parameters
        ----------
        name
        parameters

        Returns
        -------

        """
        if parameters['prestrain']:
            parameters.pop('prestrain')

        elastic = parameters['elastic']
        for key, val in elastic.items():
            parameters[key] = val
        parameters.pop('elastic')

        mat = ET.SubElement(
            self.parent.materials, 'material',
            attrib={'id': str(self.parent.material_id + 1),
                    'name': name,
                    'type': parameters['type']})

        for key, value in parameters.items():

            if key == 'type':
                pass
            elif key == 'fiber':
                fiber_item = ET.SubElement(
                    mat, key, attrib={'type': value['type']})
                fiber_item.text = to_xml_field(value['value'])
            elif key == "active_contraction":
                if value["on"] == 0:
                    pass
                else:
                    active_item = ET.SubElement(
                        mat, key, attrib={"type": "active_contraction"}
                    )
                    value.pop("on")
                    for k, v in value.items():
                        el = ET.SubElement(active_item, k)
                        el.text = str(v)
            else:
                elem = ET.SubElement(mat, key)
                elem.text = to_xml_field(value)

        self.parent.material_id += 1

        return self.parent.material_id

    def add_material_test(self, name, parameters):
        """
        Generic function that adds a material

        Parameters
        ----------
        name
        parameters

        Returns
        -------

        """

        self.material = ET.SubElement(
            self.parent.materials, 'material',
            attrib={'id': str(self.parent.material_id + 1),
                    'name': name,
                    'type': parameters['type']})

        # add every value that is not a dictionary
        for key, value in parameters.items():
            if key == "type":
                pass
            elif not isinstance(value, dict):
                elem = ET.SubElement(self.material, key)
                elem.text = to_xml_field(value)

        self.parent.material_id += 1

        return self.parent.material_id

    def add_elastic_matrix(self, parameters, prestrain=False):
        """
        Function that adds an elastic matrix to the model

        Parameters
        ----------
        parent
        parameters

        Returns
        -------

        """
        parent = self.material
        if prestrain:
            elem = ET.SubElement(parent, "elastic", attrib={
                "type": parameters["type"]
            })
            parent = elem

        for key, value in parameters.items():
            if key == "type":
                pass
            elif not isinstance(value, dict):
                sub_elem = ET.SubElement(parent, key)
                sub_elem.text = to_xml_field(value)

    def add_fiber(self, parameters, type, prestrain=False):
        """
        Function that adds a fiber definition to the material model. If a
        prestrain material is defined then the fiber will be added under the
        elastic matrix element

        Parameters
        ----------
        parameters
        type
        prestrain

        Returns
        -------

        """
        assert type in ["map", "vector", "local"], "Wrong Fiber Type"

        # if prestrain is enabled find the elastic matrix element
        parent = self.material
        if prestrain:
            parent = self.material.find("elastic")

        fiber_elem = ET.SubElement(parent, "fiber", attrib={
            "type": type
        })
        if isinstance(parameters[type], str):
            fiber_elem.text = str(parameters[type])
        else:
            fiber_elem.text = to_xml_field(parameters[type])

    def add_active_contraction(self, parameters):
        """
        Function that adds an active contraction to the model

        Parameters
        ----------
        parameters

        Returns
        -------

        """
        active_elem = ET.SubElement(
            self.material, "active_contraction",
            attrib={
                "type": "active_contraction"
            })

        for key, value in parameters.items():
            if key in ("type", "on"):
                pass
            elif not isinstance(value, dict):
                sub_elem = ET.SubElement(active_elem, key)
                sub_elem.text = to_xml_field(value)

    def add_prestrain_stretch(self, parameters, type):
        """
        Function that adds a prestrain in - situ stretch
        Parameters
        ----------
        parameters
        type: map or loadcurve

        Returns
        -------

        """
        assert type in ("map", "loadcurve"), "Wrong Stretch Type!"

        prestrain_el = ET.SubElement(
            self.material, "prestrain", attrib={"type": "in-situ stretch"})

        if type == "map":
            stretch_el = ET.SubElement(
                prestrain_el, "stretch", attrib={"type": "map"})
            stretch_el.text = str(parameters[type])

            isochoric_el = ET.SubElement(prestrain_el, "isochoric")
            isochoric_el.text = str(parameters["isochoric"])

            return None

        else:
            stretch_el = ET.SubElement(
                prestrain_el, 'stretch', attrib={
                    'lc': str(self.parent.loadcurve_id + 1)})
            stretch_el.text = str(1)

            self.parent.loadcurve_id += 1

            isochoric_el = ET.SubElement(prestrain_el, "isochoric")
            isochoric_el.text = str(parameters["isochoric"])

            return self.parent.loadcurve_id

def recursive_dict_operator(self, d, parent):
    # iterate over all items of the dictionary
    for key, value in d.items():
        # check if the value is itself a dictionary
        if isinstance(value, dict):
            # if yes then create an element with attribute "type" = key
            if key in ["stretch"]:
                sub_elem = ET.SubElement(
                    parent, key, attrib={"type": key}
                )
                print("HERE")
                sub_elem.text = str(value)
            else:
                sub_elem = ET.SubElement(
                    parent, key, attrib={"type": value["type"]}
                )
                value.pop("type")
                for pair in self.recursive_dict_operator(value, sub_elem):
                    sub_sub_elem = ET.SubElement(sub_elem, *pair)
                    sub_sub_elem.text = to_xml_field(value)
                    yield key, *pair
        # if the value is not a dictionary then yield its value
        else:
            elem = ET.SubElement(parent, key)
            elem.text = to_xml_field(value)


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
