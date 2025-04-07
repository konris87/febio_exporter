# -*- coding:utf-8 -*-
# @Time:        7/5/22 4:00 μ.μ.
# @Author:      kostas
# @Email:   krisvas@ece.upatras.gr
# @Filename:    febio_configure.py
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

__doc__ = "Submodule that is used to configure FEBio settings"
__all__ = ["FEBioConfigFile"]


class FEBioConfigFile:
    """
    This class creates a config file for the Febio model
    """

    def __init__(self):
        """Constructor"""
        self.root = ET.Element('febio_config',
                               attrib={'version': '3.0'})
        self.solver = ET.SubElement(self.root, 'default_linear_solver')
        # self.setname = ET.SubElement(self.root, 'set',
        #                              attrib={'name': 'PluginsDir'})
        # self.imp = ET.SubElement(self.root, 'import')

    def set_solver(self, solver='pardiso'):
        """
        Parameters
        ----------
        solver : ['string'] set the solver: 'paradiso' is default

        Returns
        -------
        None.

        """
        self.solver.attrib = {'type': solver}

    def setup_plugins_directory(self, pluginsdir):
        self.setname.text = pluginsdir

    def import_plugins(self, plugins):
        """

        Parameters
        ----------
        plugins : [List] A list of the plugins that are imported in the
        analysis.

        Returns
        -------
        None.

        """

        for i in plugins:
            self.imp.text = "$(PluginsDir)" + i

    def output_negative_jacobian_elements(self):
        self.neg = ET.SubElement(self.root, 'output_negative_jacobians')
        self.neg.text = str(1)

    def export_config_xml(self, dir_name, file_name):
        """Exports config file as .xml file.

        Parameters
        ----------

        dir_name: [string] directory to store the file

        file_name: [string] the file path (.feb can be omitted)

        """
        file_path = os.path.join(dir_name, file_name)
        xmlstr = minidom.parseString(ET.tostring(self.root)).toprettyxml(
            indent='  ')
        with open(file_path, 'wb') as f:  # Python 3 : 'wb', not 'w'
            f.write(xmlstr.encode('utf-8'))
