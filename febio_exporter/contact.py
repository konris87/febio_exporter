# -*- coding:utf-8 -*-
# @Time:        7/5/22 3:10 μ.μ.
# @Author:      kostas
# @Email:   krisvas@ece.upatras.gr
# @Filename:    contact.py
import copy
import xml.etree.ElementTree as ET

__doc__ = "Contact submodule to create contact between surface pairs"
__all__ = ["Contact"]


class Contact:
    """
    Builds an instance of object "Contact"
    """

    def __init__(self, model):
        self.parent = model
        self.root = None

    def add_contact_model(self, name, contact_type, surface_pair, parameters,
                          root=None):
        """Adds a contact model.

        Parameters

        name: [string] name of the element

        contact_type: [string] type of the contact model (e.g.,
                      sliding-facet-on-facet")

        surface_pair: [string] name of the master-slave surface pair

        parameters: [dictionary] dictionary containing the parameters of the
                    contact model

        root: The parent xml element

        To do
        -----

        T1: provide support for other contact models (need testing)

        """
        if root is None:
            self.root = self.parent.contact
        else:
            self.root = root

        assert (contact_type in ['sliding-facet-on-facet', 'sliding-elastic',
                                 'tied-node-on-facet', 'tied-facet-on-facet',
                                 'tied-elastic'])
        contact = ET.SubElement(self.root, 'contact',
                                attrib={'name': name,
                                        'type': contact_type,
                                        'surface_pair': surface_pair})
        for key, value in parameters.items():
            item = ET.SubElement(contact, key)
            item.text = str(value)

    def add_surface_pair(self, name, master_surface, slave_surface, root=None):
        """Adds a surface pair that can be used for collision.

        Parameters
        ----------

        name: [string] name of the element

        master_surface: [string] name of the master surface

        slave_surface: [string] name of the slave surface

        root: [xml SubElement, None] if none they are appended to Geometry

        """
        if root is None:
            self.root = self.parent.geometries
        else:
            self.root = root

        surface_pair = ET.SubElement(self.root, 'SurfacePair',
                                     attrib={'name': name})
        # ET.SubElement(surface_pair, 'master',
        primary = ET.SubElement(surface_pair, 'primary')
        primary.text = master_surface
        secondary = ET.SubElement(surface_pair, 'secondary')
        secondary.text = slave_surface

    @staticmethod
    def get_default_sliding_elastic_contact_parameters():
        """Gets the contact sliding-elastic parameters.

        Returns
        -------

        parameters: [dictionary]

        FEBio Defaults
        --------------

            'laugon': 0,
            'tolerance': 0.2,
            'penalty': 1,
            'two_pass': 0,
            'auto_penalty': 0,
            'fric_coeff': 0,
            'fric_penalty': 0,
            'search_tol': 0.01,
            'minaug': 0,
            'maxaug': 10,
            'gaptol': 0,
            'seg_up': 0

        """
        return copy.copy({
            'laugon': 0,
            'tolerance': 0.2,
            'gaptol': 0,
            'penalty': 1,
            'auto_penalty': 0,
            'two_pass': 0,
            'symmetric_stiffness': 0,
            'search_tol': 0.01,
            'search_radius': 0,
            'minaug': 0,
            'maxaug': 10,
            'seg_up': 0,
            'fric_coeff': 0,
            'smooth_aug': 0,
            'node_reloc': 0,
            'flip_primary': 0,
            'flip_secondary': 0,
            'knmult': 0,
            'update_penalty': 0,
            'shell_bottom_primary': 0,
            'shell_bottom_secondary': 0
        })

    @staticmethod
    def get_default_tied_elastic_contact_parameters():
        """

        """
        return copy.copy({
            'laugon': 1,
            'tolerance': 0,
            'gaptol': 0,
            'penalty': 1e3,
            'auto_penalty': 0,
            'two_pass': 0,
            'knmult': 1,
            'search_tol': 0.01,
            'symmetric_stiffness': 0,
            'search_radius': 1,
            'minaug': 0,
            'maxaug': 10
        })

    @staticmethod
    def get_default_tied_facet_on_facet():
        """

        """
        return copy.copy({
            'laugon': 1,
            'tolerance': 0,
            'penalty': 1e3,
            'minaug': 0,
            'maxaug': 10})

#  TODO Implement other types of contacts, eg. Surface - Nodes
