# -*- coding:utf-8 -*-
# @Time:        7/5/22 3:10 μ.μ.
# @Author:      kostas
# @Email:   krisvas@ece.upatras.gr
# @Filename:    contact.py

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
        ----------

        name: [string] name of the element

        contact_type: [string] type of the contact model (e.g.,
                      sliding-facet-on-facet")

        surface_pair: [string] name of the master-slave surface pair

        parameters: [dictionary] dictionary containing the parameters of the
                    contact model

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

        surface_pair = ET.SubElement(root, 'SurfacePair',
                                     attrib={'name': name})
        # ET.SubElement(surface_pair, 'master',
        primary = ET.SubElement(surface_pair, 'primary')
        primary.text = master_surface
        secondary = ET.SubElement(surface_pair, 'secondary')
        secondary.text = slave_surface

#  TODO Implement other types of contacts, eg. Surface - Nodes
