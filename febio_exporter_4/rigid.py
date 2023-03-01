# -*- coding: utf-8 -*-
# @Time    : 20/3/22 9:12 μ.μ.
# @Author  : Kostas Risvas
# @Email   : krisvas@ece.upatras.gr
# @File    : rigid.py
import xml.etree.ElementTree as ET
import copy
from febio_exporter_4.utils import to_xml_field

__doc__ = "Rigid submodule that is used to create rigid body DoFs"
__all__ = ["Rigid"]


class Rigid:
	"""

	"""

	def __init__(self, model):
		self.parent = model
		self.root = None

	def add_rb_fixed_constraint(self, name, rigid_body_id, constraints,
	                            root=None):
		"""Constraint the degrees of freedom of a rigid body.

		Parameters
		----------

		name: [string] name of the element

		rigid_body_id: [integer] the associated rigid body

		constraints: [list] a list of constraints (e.g., x, y, z, Rx, Ry, Rz)

		root: [ET.SubElement] (default None -> self.boundaries) the root
		node in
		case that the boundary is attached to some other element (e.g. Step)

		"""
		for c in constraints:
			assert (c in ['Rx_dof', 'Ry_dof', 'Rz_dof',
			              'Ru_dof', 'Rv_dof', 'Rw_dof'])

		if root is None:
			self.root = self.parent.rigid
		else:
			self.root = root

		constraint_element = ET.SubElement(self.root, 'rigid_bc',
		                                   attrib={'name': name,
		                                           'type': 'rigid_fixed'})
		rb = ET.SubElement(constraint_element, 'rb')
		rb.text = str(rigid_body_id)
		for c in constraints:
			c_dof = ET.SubElement(constraint_element, c)
			c_dof.text = str(1)

	def add_rb_kinematic_constraint(
			self, name, parameters, root=None):

		assert parameters['dof'] in ['x', 'y', 'z', 'Ru', 'Rv', 'Rw'], \
			'Invalid dof!'
		assert parameters['c_type'] in \
		       ['rigid_displacement',
		        'rigid_rotation'], 'Invalid constraint type!'

		if root is None:
			self.root = self.parent.rigid
		else:
			self.root = root

		constraint_element = ET.SubElement(
			self.root, 'rigid_bc',
			attrib={'name': name, 'type': parameters['c_type']})
		rb = ET.SubElement(constraint_element, 'rb')
		rb.text = parameters['rb']
		dof = ET.SubElement(constraint_element, 'dof')
		dof.text = parameters['dof']
		value_el = ET.SubElement(
			constraint_element, 'value', attrib={
				"lc": str(self.parent.loadcurve_id + 1)})
		value_el.text = parameters['value']
		rel_el = ET.SubElement(
			constraint_element, 'relative'
		)
		rel_el.text = str(parameters['relative'])
		self.parent.loadcurve_id += 1

		return self.parent.loadcurve_id

	# def add_rb_force_load(
	# 		self, name, dof, rigid_body_id, c_type, l_type, value, relative=0,
	# 		root=None
	# ):

	def add_rb_force_load(
			self, name, dof, rigid_body_id, value, load_type, relative,
			root=None
	):
		"""

		Parameters
		----------
		name : [str] boundary condition name
		dof : [str] degree of freedom
		rigid_body_id : [int] rigid body material id
		value : [float] force value
		load_type : [int] 0: direct load, 1: follower load, 2: target load
		relative : [int] flag indicating if load is applied relative to
			previous step
		root : [ET.Element] parent element

		Returns
		-------

		"""

		assert (dof in ['Rx', 'Ry', 'Rz'])

		if root is None:
			self.root = self.parent.rigid
		else:
			self.root = root

		constraint_element = ET.SubElement(
			self.root, 'rigid_load',
			attrib={'name': name, 'type': 'rigid_force'})
		rb = ET.SubElement(constraint_element, 'rb')
		rb.text = str(rigid_body_id)
		dof_elem = ET.SubElement(constraint_element, 'dof')
		dof_elem.text = str(dof)
		load_type = ET.SubElement(constraint_element, 'load_type')
		load_type.text = str(load_type)
		relative_el = ET.SubElement(constraint_element, 'relative')
		relative_el.text = str(relative)
		value_el = ET.SubElement(
			constraint_element, 'value', attrib={
				"lc": str(self.parent.loadcurve_id + 1)})
		value_el.text = str(value)
		self.parent.loadcurve_id += 1

		return self.parent.loadcurve_id

	def add_rb_moment_load(
			self, name, dof, rigid_body_id, value, relative, load_type=None,
			root=None
	):
		"""

		Parameters
		----------
		name : [str] boundary condition name
		dof : [str] degree of freedom
		rigid_body_id : [int] rigid body material id
		value : [float] force value
		load_type : [int] 0: direct load, 1: follower load, 2: target load
		relative : [int] flag indicating if load is applied relative to
			previous step
		root : [ET.Element] parent element

		Returns
		-------

		"""

		assert (dof in ['Ru', 'Rv', 'Rw'])

		if root is None:
			self.root = self.parent.rigid
		else:
			self.root = root

		constraint_element = ET.SubElement(
			self.root, 'rigid_load',
			attrib={'name': name, 'type': 'rigid_moment'})
		rb = ET.SubElement(constraint_element, 'rb')
		rb.text = str(rigid_body_id)
		dof_elem = ET.SubElement(constraint_element, 'dof')
		dof_elem.text = str(dof)
		relative_el = ET.SubElement(constraint_element, 'relative')
		relative_el.text = str(relative)
		value_el = ET.SubElement(
			constraint_element, 'value', attrib={
				"lc": str(self.parent.loadcurve_id + 1)})
		value_el.text = str(value)
		if load_type is not None:
			# raise RuntimeError("Not Implemented Yet")
			load_elem = ET.SubElement(constraint_element, 'load_type')
			load_elem.text = str(load_type)
		self.parent.loadcurve_id += 1

		return self.parent.loadcurve_id

	def add_rigid_contractile_force(self, name, parameters, root=None):

		if root is None:
			self.root = self.parent.rigid
		else:
			self.root = root

		constraint = ET.SubElement(
			self.root, "rigid_connector", attrib={
				"type": "rigid contractile force"
			})

		for key, value in parameters.items():
			if "body" in key:
				subel = ET.SubElement(
					constraint, key)
				subel.text = str(value)
			elif "insertion" in key:
				subel = ET.SubElement(
					constraint, key)
				subel.text = to_xml_field(value)
			elif "f0" in key:
				subel = ET.SubElement(
					constraint, key,
					attrib={"lc": str(self.parent.loadcurve_id + 1)}
				)
				subel.text = str(value)
				self.parent.loadcurve_id += 1

		return self.parent.loadcurve_id

	#  TODO add description about paramters
	@staticmethod
	def get_rigid_body_prescribed_motion_default_parameters():
		"""

		"""
		return copy.copy({"rb": "",
		                  "dof": "",
		                  "scale": str(1),
		                  "constraint_type": "prescribe",
		                  "relative": str(0)
		                  })

	@staticmethod
	def get_rigid_body_prescribed_force_default_parameters():
		"""
		FEBio default
		-------------
		load_type: 0
		"""
		return copy.copy({"rb": str(0),
		                  "dof": "",
		                  "scale": str(1),
		                  "constraint_type": "force",
		                  "load_type": str(0)})

	@staticmethod
	def get_default_rcf_parameters():
		"""
		default rigid contractile force parameters

		Returns
		-------
		a copy of the parameters as dictionary
		"""
		return copy.copy({
			"body_a": 1,
			"body_b": 2,
			"insertion_a": [0, 0, 0],
			"insertion_b": [0, 0, 0],
			"f0": 1
		})
