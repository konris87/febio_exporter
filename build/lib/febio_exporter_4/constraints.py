# -*- coding:utf-8 -*-
# @Time:        7/5/22 3:19 μ.μ.
# @Author:      kostas
# @Email:   krisvas@ece.upatras.gr
# @Filename:    constraints.py
import copy
import xml.etree.ElementTree as ET
from febio_exporter_4.utils import to_xml_field

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
	def get_default_stretch_constraints():
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
			'max_iters': 0.0,
			'isochoric': 1.0
		})

