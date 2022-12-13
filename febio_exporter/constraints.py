# -*- coding:utf-8 -*-
# @Time:        7/5/22 3:19 μ.μ.
# @Author:      kostas
# @Email:   krisvas@ece.upatras.gr
# @Filename:    constraints.py
import copy
import xml.etree.ElementTree as ET
from febio_exporter.utils import to_xml_field

__doc__ = "Constraints submodule to create rigid joints," \
          " rigid connectors and prestrain rules"
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
                                             self.parent.loadcurve_id + 1)})
                    loadcurves.append(self.parent.loadcurve_id + 1)
                    self.parent.loadcurve_id = self.parent.loadcurve_id + 1

                item.text = str(value)
            else:
                item = ET.SubElement(joint, key)
                item.text = to_xml_field(value)

        return loadcurves

    def add_joint(self, name, parameters, root=None):
        """
        Adds a joint to the model

        Parameters
        ----------
        name
        parameters
        root

        Returns
        -------

        """

        if root is None:
            self.root = self.parent.rigid
        else:
            self.root = root
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
                                             self.parent.loadcurve_id + 1)})
                    loadcurves.append(self.parent.loadcurve_id + 1)
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

    def add_prestrain_constraint(self, name, parameters, root=None):
        """
        Adds prestrain constraint (prestrain update rules)

        Parameters
        ----------
        name
        parameters
        root

        Returns
        -------

        """
        if root is None:
            self.root = self.parent.constraints
        else:
            self.root = root

        constraint = ET.SubElement(
            self.root, 'constraint',
            attrib={'type': parameters['type'],
                    'name': name})

        for key, value in parameters.items():
            if key == 'type':
                pass
            else:
                item = ET.SubElement(constraint, key)
                item.text = to_xml_field(value)

    @staticmethod
    def get_default_cylindrical_joint_parameters():
        """Gets the default cylindrical joint parameters.

        Returns
        -------

        parameters: [dictionary]
        """
        return copy.copy({
            'body_a': 0,
            'body_b': 0,
            'tolerance': 0,
            'gaptol': 0.01,
            'angtol': 0.01,
            'force_penalty': 1e4,
            'moment_penalty': 1e5,
            'joint_origin': [0, 0, 0],
            'joint_axis': [1, 0, 0],
            'transverse_axis': [0, 0, 0],
            'minaug': 0,
            'maxaug': 10,
            'prescribed_translation': 0,
            'translation': 0,
            'force': 0,
            'prescribed_rotation': 0,
            'rotation': 0,
            'moment': 0
        })

    @staticmethod
    def get_default_revolute_joint_parameters():
        """Gets the default cylindrical joint parameters.

        Returns
        -------

        parameters: [dictionary]
        """
        return copy.copy({
            'body_a': 0,
            'body_b': 0,
            'tolerance': 0,
            'gaptol': 0.01,
            'angtol': 0.01,
            'force_penalty': 1e4,
            'moment_penalty': 1e5,
            'auto_penalty': 1,
            'joint_origin': [0, 0, 0],
            'rotation_axis': [1, 0, 0],
            'transverse_axis': [0, 0, 0],
            'minaug': 0,
            'maxaug': 10,
            'prescribed_rotation': 0,
            'rotation': 0,
            'moment': 0
        })

    @staticmethod
    def get_default_prismatic_joint_parameters():
        """Gets the default prismatic joint parameters.

        Returns
        -------

        parameters: [dictionary]
        """
        return copy.copy({
            'body_a': 0,
            'body_b': 0,
            'tolerance': 0,
            'gaptol': 0.01,
            'angtol': 0.01,
            'force_penalty': 1e4,
            'moment_penalty': 1e5,
            'auto_penalty': 1,
            'joint_origin': [0, 0, 0],
            'translation_axis': [1, 0, 0],
            'transverse_axis': [0, 0, 0],
            'minaug': 0,
            'maxaug': 10,
            'prescribed_translation': 0,
            'translation': 0,
            'force': 0
        })

    @staticmethod
    def get_default_lock_joint_parameters():
        """Gets the default cylindrical joint parameters.

        Returns
        -------

        parameters: [dictionary]
        """
        return copy.copy({
            'body_a': 0,
            'body_b': 0,
            'tolerance': 0,
            'gaptol': 0.01,
            'angtol': 0.01,
            'force_penalty': 1e7,
            'moment_penalty': 1e3,
            'auto_penalty': 1,
            'joint_origin': [0, 0, 0],
            'first_axis': [1, 0, 0],
            'second_axis': [0, 1, 0],
            'minaug': 0,
            'maxaug': 10,
        })

    @staticmethod
    def get_default_prestrain_constraint_parameters():
        """
        Gets default prestrain constraint parameters for an analysis using
        the prestrain plugin

        Returns
        -------

        """
        return copy.copy({
            'type': "prestrain",
            # 'update': 1,
            'tolerance': 0.03,
            'min_iters': 3,
            'max_iters': 0.0
        })

    @staticmethod
    def get_default_in_situ_stretch_constraint_parameters():
        """
        Gets default prestrain constraint parameters for an analysis using
        the prestrain plugin

        Returns
        -------

        """
        return copy.copy({
            'type': "in-situ stretch",
            'tolerance': 0.01,
            'min_iters': 3,
            'max_iters': 0.0
        })
