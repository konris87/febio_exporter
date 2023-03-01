# A convenient Python interface for exporting FEBio (finite element) .feb
# models.
#
# Author: Dimitar Stanev (jimstanev@gmail.com)
# Contributors: Konstantinos Risvas (krisvas@ece.upatras.gr)
#               Konstantinos Filip (filipconstantinos@gmail.com)
#
# ---
# Preview bug #2, deformable fix constraint ignores name
# Preview bug #3, deformable fix constraint requires , without space
# (e.g. 'x,y,z')

import os
import copy
import xml.etree.ElementTree as ET
from xml.dom import minidom
from febio_exporter_4.utils import export, indent, sort_children
import subprocess
import vedo
import numpy as np

__doc__ = "Submodule to create, export and edit a .feb model"
__all__ = ["FEBioExporter4"]


###############################################################################
class FEBioExporter4:
    """This class creates, edits and exports the defined model as .feb file
    format."""

    def __init__(self):
        """Constructor"""
        self.material_id = 0
        self.node_id = 1
        self.element_id = 1
        self.loadcurve_id = 0
        # self.discrete_id = 1
        self.root = ET.Element('febio_spec',
                               attrib={'version': '4.0'})
        self.solid = ET.SubElement(self.root, 'Module',
                                   attrib={'type': 'solid'})
        self.control = None
        self.globals = ET.SubElement(self.root, 'Globals')
        constants = ET.SubElement(self.globals, 'Constants')
        t = ET.SubElement(constants, 'T')
        t.text = '0'
        r = ET.SubElement(constants, 'R')
        r.text = '0'
        f = ET.SubElement(constants, 'Fc')
        f.text = '0'
        self.materials = ET.SubElement(self.root, 'Material')
        self.geometries = ET.SubElement(self.root, 'Mesh')
        self.domains = ET.SubElement(self.root, 'MeshDomains')
        self.mesh_data = ET.SubElement(self.root, 'MeshData')
        self.initial = ET.SubElement(self.root, 'Initial')
        self.boundaries = ET.SubElement(self.root, 'Boundary')
        self.rigid = ET.SubElement(self.root, 'Rigid')
        self.loads = ET.SubElement(self.root, 'Loads')
        self.contact = ET.SubElement(self.root, 'Contact')
        self.step = None
        # due to bug in FEBio discrete section cannot be empty
        # self.discrete = None
        self.discrete = None
        self.constraints = ET.SubElement(self.root, 'Constraints')
        self.loaddata = None
        self.output = None
        self.step_counter = 1
        self.name = ''

        self.model_rotation = np.eye(3)
        self.model_origin = np.zeros(3)

    # def enable_restart(self, file_name):
    #     """Enables the febio restart mechanism.
    #
    #     Parameters
    #     ----------
    #
    #     file_name: [string] name of the damp file (e.g. out.dmp)
    #     """
    #     raise NotImplementedError('Not accepted by febio')
    #     self.restart = ET.SubElement(self.root, 'febio_restart',
    #                                  attrib={'version': '1.0'})
    #     archive = ET.SubElement(self.restart, "Archive")
    #     archive.text = file_name

    def separate_section(self, section, dir_name, file_name):
        """Separates a section of the model into a different file.

        Parameters
        ----------

        section: [ET.SubElement] section to be separated

        dir_name: [string] directory to store the file

        file_name: [string] name of the file section (.feb can be omitted)

        """
        if '.feb' not in file_name:
            file_name += '.feb'

        # export section into separate file
        old_section = copy.copy(section)
        root = ET.Element('febio_spec',
                          attrib={'version': '4.0'})
        root.append(old_section)
        tree = ET.ElementTree(root)
        ET.indent(tree, space="\t", level=0)

        tree.write(os.path.join(dir_name, file_name),
                   encoding="utf-8", xml_declaration=True,
                   short_empty_elements=True)

        # clear current section
        section.clear()
        section.attrib = {'from': file_name}

    def export(self, dir_name, file_name):
        """Exports model as .feb file.

        Parameters
        ----------

        dir_name: [string] directory to store the file

        file_name: [string] the file path (.feb can be omitted)

        """
        #  TODO add implementation for both windows & ubuntu
        if '.feb' not in file_name:
            file_name += '.feb'

        file = os.path.abspath(os.path.join(dir_name, file_name))
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
            print("created folder : ", dir_name)
        else:
            print("output_dir exists")

        tree = ET.ElementTree(self.root)
        # ensure that the loaddata curves are sorted
        try:
            loaddata = tree.find("LoadData")
            sort_children(loaddata, 'id')
        except TypeError:
            pass

        # xmlstr = minidom.parseString(ET.tostring(self.root)).toprettyxml(
        #     indent='    ')
        # with open(file, "w") as f:
        #     f.write(xmlstr)
        ET.indent(tree, space="\t", level=0)
        tree.write(file,
                   encoding="utf-8", xml_declaration=True,
                   short_empty_elements=True)

    def edit_feb_file(self, feb_file, geometry_file, discrete_file):
        """
        Function that loads a feb file, and adjust the FEBioExporter class in
        order to continue processing of the feb file.

        Parameters
        ----------
        feb_file: the imported feb file
        geometry_file: the file that contains the geometries
        discrete_file: the file that contains the discrete element

        """

        tree = ET.parse(feb_file)
        root = tree.getroot()

        childs = []
        for child in root:
            childs.append(child)

        tags = []
        for child in root:
            tags.append(child.tag)

        # read and copy the material elements
        last_element_id = None
        for elem in root[tags.index('Material')]:
            element = ET.SubElement(self.materials, elem.tag, elem.attrib)
            for subelem in elem:
                subelement = ET.SubElement(element, subelem.tag,
                subelem.attrib)
                subelement.text = subelem.text
                for sub in subelem:
                    subsubelement = ET.SubElement(subelement,
                                                  sub.tag, sub.attrib)
                    subsubelement.text = sub.text
            last_element_id = int(element.attrib['id'])
            element = copy.deepcopy(elem)

        # retrieve the last material id in order to append new materials
        self.material_id = last_element_id

        # load geometries file
        self.geometries.set('from', geometry_file)

        # load the discrete elements file
        if discrete_file is None:
            pass
        elif self.discrete is None:
            self.discrete = ET.SubElement(self.root, 'Discrete')
            self.discrete.set('from', discrete_file)

        # read and copy meshdomains
        for elem in root[tags.index('MeshDomains')]:
            element = ET.SubElement(self.domains, elem.tag, elem.attrib)
            for subelem in elem:
                subelement = ET.SubElement(element, subelem.tag,
                                           subelem.attrib)
                subelement.text = subelem.text

        # read and copy meshdata
        for elem in root[tags.index('MeshData')]:
            element = ET.SubElement(self.mesh_data, elem.tag, elem.attrib)
            for subelem in elem:
                subelement = ET.SubElement(element, subelem.tag,
                                           subelem.attrib)
                subelement.text = subelem.text

        # read and copy the boundary elements
        for elem in root[tags.index('Boundary')]:
            element = ET.SubElement(self.boundaries, elem.tag, elem.attrib)
            for subelem in elem:
                subelement = ET.SubElement(element, subelem.tag)
                subelement.text = subelem.text

        # read and copy rigid
        for elem in root[tags.index('Rigid')]:
            element = ET.SubElement(self.rigid, elem.tag, elem.attrib)
            for subelem in elem:
                subelement = ET.SubElement(element, subelem.tag,
                                           subelem.attrib)
                subelement.text = subelem.text

        # read and copy the contact elements
        for elem in root[tags.index('Contact')]:
            element = ET.SubElement(self.contact, elem.tag, elem.attrib)
            for subelem in elem:
                subelement = ET.SubElement(element, subelem.tag,
                                           subelem.attrib)
                subelement.text = subelem.text

        # load the looadcurves and retrieve the last curve
        if self.loaddata is None:
            self.loaddata = ET.SubElement(self.root, 'LoadData')

        last_curve_id = None
        if 'LoadData' in tags:
            for elem in root[tags.index('LoadData')]:
                element = ET.SubElement(self.loaddata, elem.tag, elem.attrib)
                if element.attrib['id'] != '0':
                    self.loadcurve_id = int(
                        element.attrib['id']) + 1
                for subelem in elem:
                    subelement = ET.SubElement(element, subelem.tag,
                                               subelem.attrib)
                    subelement.text = subelem.text
                    for sub in subelem:
                        subsubelement = ET.SubElement(subelement,
                                                      sub.tag, sub.attrib)
                        # print(subsubelement.attrib)
                        subsubelement.text = sub.text
                last_curve_id = int(element.attrib['id'])

            # retrieve the last curve id in order to append new curves
            self.loadcurve_id = last_curve_id

    def add_output(self, plot_file_parameters, logfile_parameters):
        """Sets the output parameters of the analysis.

        Parameters
        ----------

        plot_file_parameters: [dictionary] output variables
        logfile_parameters: [dictionary] logfile parameters
        """
        self.output = ET.SubElement(self.root, 'Output')
        plotfile = ET.SubElement(self.output, 'plotfile',
                                 attrib={'type': 'febio'})
        for key, value in plot_file_parameters.items():
            if value == 1:
                var = ET.SubElement(plotfile, 'var', attrib={'type': key})

        if logfile_parameters is not None:
            logfile = ET.SubElement(self.output, 'logfile')
            for key, value in logfile_parameters.items():
                for sub_key, sub_value in value.items():
                    var = ET.SubElement(logfile, key)
                    var.set('name', sub_key)
                    var.set('data', sub_value['data'])
                    if sub_value['file']:
                        var.set('file', sub_value['file'])
                    if sub_value['ids']:
                        var.text = sub_value['ids']

    def FEBio_Restarter(self, restart_file):
        """
        Function that enables FEBio restart using a damp file

        Parameters
        -----------
        restart_file: the feb file that we want to restart

        """
        self.step_counter = 1
        self.loadcurve_id = 1
        self.root = ET.Element('febio_restart',
                               attrib={'version': '2.0'})
        archive = ET.SubElement(self.root, 'Archive')
        archive.text = restart_file
        self.loaddata = ET.SubElement(self.root, 'LoadData')

    def execute(self, model_filename, directory, mode='i', *args):
        """
        Function that executes FEBio version 3 through the command line.
        FEBio should be in the environment PATH

        Parameters
        ----------
        directory
        model_filename: the name of the created file
        mode: 'i' is the default, use 'r' to restart a run
        Returns
        -------

        """
        command = ["febio4", f"-{mode}", '{}'.format(model_filename)]
        command += args
        print(command)
        subprocess.run(command,	cwd=directory)

    def visualize(self, geometries):
        """
        Function to view model geometry using vedo

        Parameters
        ----------
        geometries

        Returns
        -------

        """
        meshes = []
        names = []
        # create vedo meshes from points and connectivity
        for idx in range(len(geometries)):
            points = geometries[idx][0]
            cells = geometries[idx][1]
            cell_type = geometries[idx][2]
            cells_nr = cells[cell_type].shape[0]
            names.append(geometries[idx][3])
            if cell_type == 'triangle':
                meshes.append(vedo.Mesh([points, cells[cell_type]]).legend(
                    geometries[idx][3]
                ))
            elif cell_type == 'hexahedron':
                meshes.append(vedo.UGrid([points, cells[cell_type],
                                          [12 for j in range(cells_nr)]]))
            else:
                #  TODO implement tetrahedral meshes
                raise RuntimeError('Mesh Type not implemented yet')

        # create a colormap for the provided meshes
        colors = vedo.buildPalette('g', 'r', N=len(meshes) + 1)

        # create a vedo plotter
        plt = vedo.Plotter(title="{}".format(self.name))
        for idx, mesh in enumerate(meshes):
            plt += mesh.c(colors[idx]).lw(5)
            # plt += vedo.LegendBox([mesh])

        plt.show()
        plt.close()

    @staticmethod
    def get_default_plot_file_parameters():
        """Gets the default plot file parameters.

        Returns
        -------

        parameters: [dictionary]
        """
        return copy.copy({
            'contact area': 1,
            'contact force': 1,
            'contact gap': 1,
            'contact pressure': 1,
            'displacement': 1,
            'element center of mass': 1,
            'Euler angle': 1,
            'reaction forces': 1,
            'rigid force': 1,
            'rigid torque': 1,
            'rigid position': 1,
            'rigid rotation vector': 1,
            'stress': 1
        })

    @staticmethod
    def get_default_logfile_parameters():

        return copy.copy({
            'rigid_body_data': {
                'center_of_mass': {'data': 'x;y;z',
                                   'file': None, 'ids': None},
                'quaternion_data': {'data': 'qx;qy;qz;qw',
                                    'file': None, 'ids': None},
                'reaction_forces': {
                    'data': 'Fx;Fy;Fz',
                    'file': None,
                    'ids': None
                },
                'reaction_moments': {
                    'data': 'Mx;My;Mz',
                    'file': None,
                    'ids': None
                }
            },
            'rigid_connector_data': {
                'connector_forces': {
                    'data': 'RCFx;RCFy;RCFz',
                    'file': None,
                    'ids': None
                },
                'connector_moments': {
                    'data': 'RCMx;RCMy;RCMz',
                    'file': None,
                    'ids': None}
            },
        })
