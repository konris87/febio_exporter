# -*- coding: utf-8 -*-
# @Time    : 20/3/22 9:36 μ.μ.
# @Author  : Kostas Risvas
# @Email   : krisvas@ece.upatras.gr
# @File    : boundary.py
import xml.etree.ElementTree as ET
from febio_exporter.utils import to_xml_field


class Boundary:
	"""

	"""

	def __init__(self, model):
		# self.add_loadcurve = febio_exporter.FEBioExporter.add_loadcurve
		self.parent = model
		self.root = None

	def add_deformable_prescribed_displacement(
			self, name, dof, node_set_name, scale_factor,
			relative=0, root=None):
		"""Adds prescribed displacement constraint.

		Parameters
		----------

		name: [string] the name of the elements

		dof: [string] the prescribed dof constraints (e.g., x, y, z)

		node_set_name: [string] the name of the node set

		scale_factor: [float] scaling factor of the load curve

		root: [ET.SubElement] (default None -> self.boundaries) the root
		node in
		case that the boundary is attached to some other element (e.g. Step)

		Returns
		-------

		loadcurve_id: [integer] the associated load curve id

		"""
		assert (dof in ['x', 'y', 'z'])
		if root is None:
			self.root = self.parent.boundaries
		else:
			self.root = root

		bc_element = ET.SubElement(
			self.root, 'bc', attrib={
				'type': "prescribe",
				'name': name,
				'node_set': node_set_name})
		dof_el = ET.SubElement(bc_element, "dof")
		dof_el.text = dof
		scale = ET.SubElement(
			bc_element, 'scale',
			attrib={'lc': str(self.parent.loadcurve_id + 1)})
		scale.text = str(scale_factor)
		relative_el = ET.SubElement(bc_element, 'relative')
		relative_el.text = str(relative)
		self.parent.loadcurve_id += 1
		return self.parent.loadcurve_id

	def add_rigid_connector(self, name, rigid_body_id, node_set_name,
							root=None):
		"""Connect the node set of a deformable to a rigid body.

		Parameters
		----------

		name: [string] name of the element

		rigid_body_id: [integer] the associated rigid body

		node_set_name: [string] the name of the note set that belongs to the
					   deformable body

		root: [ET.SubElement] (default None -> self.boundaries) the root node
		in case that the boundary is attached to some other element (e.g.
		Step)

		"""
		if root is None:
			self.root = self.parent.boundaries
		else:
			self.root = root

		bc = ET.SubElement(self.root, 'bc',
						   attrib={'name': name,
								   'type': 'rigid',
								   'node_set': node_set_name})
		rb = ET.SubElement(bc, 'rb')
		rb.text = str(rigid_body_id)

	def add_deformable_fixed_displacement(self, name, constraints,
										  node_set_name, root=None):
		"""Adds fixed displacement constraint.

		Parameters
		----------

		name: [string] the name of the elements

		constraints: [list] a list of constraints (e.g., x, y, z)

		node_set_name: [string] the name of the node set

		root: [ET.SubElement] (default None -> self.boundaries) the root
		node in
		case that the boundary is attached to some other element (e.g. Step)

		"""
		# for c in constraints:
		#     assert(c in ['x', 'y', 'z'])

		if root is None:
			self.root = self.parent.boundaries
		else:
			self.root = root

		ET.SubElement(self.root, 'fix',
					  attrib={'name': name,
							  'bc': to_xml_field(constraints),
							  'node_set': node_set_name})

# if relative_mode:
#     constraint = ET.SubElement(prescribed_element, 'prescribed',
#                                attrib={'type': 'relative',
#                                        'bc': dof,
#                                        'lc': str(self.loadcurve_id)
#                                        })
#     constraint.text = str(scale_factor)
#     self.loadcurve_id = self.loadcurve_id + 1
#
# else:
#     constraint = ET.SubElement(prescribed_element, constraint_type,
#                                attrib={'bc': dof,
#                                        'lc': str(self.loadcurve_id)})
#     constraint.text = str(scale_factor)
#     self.loadcurve_id = self.loadcurve_id + 1

# return self.loadcurve_id - 1
