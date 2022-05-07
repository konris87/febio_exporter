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
import copy
import os
import xml.etree.ElementTree as ET
from utils import export, indent

__doc__ = "Submodule to create, export and edit a .feb model"
__all__ = ["FEBioExporter"]


###############################################################################
class FEBioExporter:
    """This class creates, edits and exports the defined model as .feb file
    format."""

    def __init__(self):
        """Constructor"""
        self.material_id = 1
        self.node_id = 1
        self.element_id = 1
        self.loadcurve_id = 1
        # self.discrete_id = 1
        self.root = ET.Element('febio_spec',
                               attrib={'version': '3.0'})
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
        # self.constraints = ET.SubElement(self.root, 'Constraints')
        self.loaddata = None
        self.output = None
        self.step_counter = 1

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
        # old_section = section.copy() # Python 2.7
        old_section = copy.copy(section)
        root = ET.Element('febio_spec',
                          attrib={'version': '3.0'})
        root.append(old_section)
        export(root, os.path.join(dir_name, file_name))
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

        if '.feb' not in file_name:
            file_name += '.feb'

        # xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent='  ')
        indent(self.root)
        tree = ET.ElementTree(self.root)
        # with open(file_path, 'wb') as f:  # Python 3 : 'wb', not 'w'
        #     # f.write(xmlstr.encode("utf-8"))
        #     f.write(ET.tostring(root, xml_declaration='xml',
        #                         short_empty_elements=False))
        tree.write(file_name,
                   encoding="utf-8", xml_declaration=True,
                   short_empty_elements=False)

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
                subelement = ET.SubElement(element, subelem.tag, subelem.attrib)
                subelement.text = subelem.text
                for sub in subelem:
                    subsubelement = ET.SubElement(subelement,
                                                  sub.tag, sub.attrib)
                    # print(subsubelement.attrib)
                    # if subsubelement.attrib['lc'] != '0':
                    #     self.loadcurve_id = int(subsubelement.attrib['lc'])+1
                    subsubelement.text = sub.text
            last_element_id = int(element.attrib['id'])

        # retrieve the last material id in order to append new materials
        self.material_id = last_element_id + 1

        # load geometries file
        self.geometries.set('from', geometry_file)

        # load the discrete elements file
        if self.discrete is None:
            self.discrete = ET.SubElement(self.root, 'Discrete')
            self.discrete.set('from', discrete_file)

        # read and copy meshdomains
        for elem in root[tags.index('MeshDomains')]:
            element = ET.SubElement(self.domains, elem.tag, elem.attrib)
            for subelem in elem:
                subelement = ET.SubElement(element, subelem.tag, subelem.attrib)
                subelement.text = subelem.text

        # read and copy meshdata
        for elem in root[tags.index('MeshData')]:
            element = ET.SubElement(self.mesh_data, elem.tag, elem.attrib)
            for subelem in elem:
                subelement = ET.SubElement(element, subelem.tag, subelem.attrib)
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
                subelement = ET.SubElement(element, subelem.tag, subelem.attrib)
                subelement.text = subelem.text

        # read and copy the contact elements
        for elem in root[tags.index('Contact')]:
            element = ET.SubElement(self.contact, elem.tag, elem.attrib)
            for subelem in elem:
                subelement = ET.SubElement(element, subelem.tag, subelem.attrib)
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
            self.loadcurve_id = last_curve_id + 1

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

    @staticmethod
    def get_default_rigid_parameters():
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
    def get_default_step_parameters():
        """Gets the default step parameters.

        Returns
        -------

        parameters: [dictionary]

        """
        return copy.copy({
            'time_steps': 10,
            'step_size': 0.1,
            'max_refs': 15,
            'max_ups': 10,
            'diverge_reform': 1,
            'reform_each_time_step': 1,
            'dtol': 0.001,
            'etol': 0.01,
            'rtol': 0,
            'lstol': 0.9,
            'min_residual': 1e-20,
            'qnmethod': 0,
            'time_stepper': {
                'dtmin': 0.01,
                'dtmax': 0.1,
                'max_retries': 5,
                'opt_iter': 10
            },
            'analysis': {
                'type': 'static'
            },
            'symmetric_stiffness': 1,
            'alpha': 1,
            'beta': 0.25,
            'gamma': 0.5
        })

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
            'penalty': 1,
            'two_pass': 0,
            'auto_penalty': 0,
            'fric_coeff': 0,
            # 'fric_penalty': 0,
            'search_tol': 0.01,
            'minaug': 0,
            'maxaug': 10,
            'gaptol': 0,
            'seg_up': 0,
            'fric_coeff': 0,
            'smooth_aug': 0,
            'node_reloc': 0,
            'flip_master': 0,
            'flip_slave': 0
        })

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
        })\

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
        })\

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
            'force_penalty': 1e4,
            'moment_penalty': 1e5,
            'auto_penalty': 1,
            'joint_origin': [0, 0, 0],
            'first_axis': [1, 0, 0],
            'second_axis': [1, 0, 0],
            'minaug': 0,
            'maxaug': 10,
        })

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
            'node_data': {
                'displacement': {
                    'data': 'x;y;z',
                    'delim': ',',
                    'file': None,
                    'ids': None
                }
            }
        })
