# -*- coding: utf-8 -*-
# @Time    : 20/3/22 6:27 μ.μ.
# @Author  : Kostas Risvas
# @Email   : krisvas@ece.upatras.gr
# @File    : discrete.py

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
from febio_exporter_4.utils import to_xml_field, sort_sets
from febio_exporter_4.loaddata import Loaddata

__doc__ = "Discrete submodule to append discrete elements, such as linear or " \
		  "nonlinear springs."
__all__ = ["Discrete"]


class Discrete:
	"""
	Build an instance of object "Discrete"
	"""

	def __init__(self, model):
		self.parent = model
		self.discrete_id = 1
		self.loaddata = Loaddata(model)

	def add_discrete_element(
			self, group_name,
			origin_geometry, origin_node_set,
			origin_node_offset, insertion_geometry,
			insertion_node_set, insertion_node_offset, ref_ax,
			young_mod, cross_section, ref_strain,
			mri_length, offset, linearity, plot_curve=True):
		"""

		Parameters
		----------
		group_name
		origin_geometry
		origin_node_set
		origin_node_offset
		insertion_geometry
		insertion_node_set
		insertion_node_offset
		ref_ax
		young_mod
		cross_section
		ref_strain
		mri_length
		offset
		linearity
		plot_curve

		Returns
		-------

		"""

		origin_points = sort_sets(origin_geometry, origin_node_set, ref_ax)
		insertion_points = sort_sets(insertion_geometry, insertion_node_set,
									 ref_ax)
		spring_num = min(origin_points.shape[0], insertion_points.shape[0])
		w = 0
		springs_length = []
		area = cross_section
		if linearity:
			if cross_section is None:
				stiffness = young_mod
				origin_points = sort_sets(origin_geometry, origin_node_set,
										  ref_ax)
				insertion_points = sort_sets(insertion_geometry,
											 insertion_node_set,
											 ref_ax)
				# calculate the number of springs. Since 1 to 1 connection is
				# desired the maximum number of springs is equal to the total
				# number of nodes of the smallest node_set.
				spring_num = min(origin_points.shape[0],
								 insertion_points.shape[0])
				# print(spring_num)
				total_length = []
				for i in range(0, spring_num):
					length = np.linalg.norm(
						origin_points[i, 1:4] - insertion_points[i, 1:4])
					total_length.append(length)
					# print(length)
					# spring constant:
					spring_constant = stiffness / spring_num
					# print(spring_constant)
					self.add_spring(
						group_name + str(i) + '_' + str(w),
						int(origin_points[
								i, 0]) + origin_node_offset,
						int(insertion_points[
								i, 0]) + insertion_node_offset,
						spring_constant,
						'tension-only linear spring')
					w += 1

				average_length = np.average(np.asarray(total_length))
				print("The average spring length is {}".format(average_length))

			else:
				for i in range(1, spring_num + 1):
					length = np.linalg.norm(
						origin_points[i - 1, 1:4] -
						insertion_points[i - 1, 1:4])
					springs_length.append(length)
					# spring constant:
					spring_constant = (area * young_mod) / (spring_num *
															length)
					# print(spring_constant)
					spring_loadcurve_id = self.add_nonlinear_spring(
						group_name + str(i - 1) + '_' + str(w),
						int(origin_points[i - 1, 0]) + origin_node_offset,
						int(insertion_points[i - 1, 0]) +
						insertion_node_offset,
						1)
					L = np.linspace(0, 200, 221)
					force, displacement = stress_strain_relationship(
						length,
						spring_constant,
						L,
						offset,
						mode='linear')
					# print curve for validation
					plt.figure(figsize=(14, 6))
					plt.plot(displacement, force, marker='',
							 label=str(ref_strain))
					plt.legend()
					plt.show()
					if self.parent.loaddata is None:
						self.parent.loaddata = ET.SubElement(
							self.parent.root, 'LoadData')
					self.loaddata.add_loadcurve(
						spring_loadcurve_id,
						'linear',
						'constant',
						displacement, force)
					w += 1
		else:
			k = young_mod * area
			displacements = []
			forces = []
			strains = []
			for i in range(1, spring_num + 1):
				length = np.linalg.norm(
					origin_points[i - 1, 1:4] - insertion_points[i - 1, 1:4])
				# pcl mesh length 41 use case
				# offset = np.abs(36.7 - length)
				# offset = np.abs(39 - length)
				if mri_length != 0:
					offset = np.abs(mri_length - length)
				# print(offset)
				# print(length)
				springs_length.append(length)
				# print("The length of the {} is {}".format(group_name,length))
				spring_constant = k / spring_num
				# print(spring_constant)
				# print(spring_constant)
				spring_loadcurve_id = self.add_nonlinear_spring(
					group_name + str(i - 1) + '_' + str(w),
					int(origin_points[i - 1, 0]) + origin_node_offset,
					int(insertion_points[i - 1, 0]) + insertion_node_offset,
					1)
				# reference length
				Lr = length / (ref_strain + 1)
				L = np.round(np.linspace(0, 10, 101), 3)
				force, displacement = stress_strain_relationship(
					Lr,
					spring_constant,
					L,
					offset,
					mode='non_linear')
				force[0] = 0
				force = np.round(force, 3)
				# print(strain,stress)
				self.loaddata.add_loadcurve(
					spring_loadcurve_id,
					'linear',
					'constant',
					displacement, force)
				w += 1
				displacements.append(displacement)
				forces.append(force)
				strains.append(ref_strain)
			# print("spring_constant: {}".format(spring_constant))
			# print("spring_number: {}".format(spring_num))
			if plot_curve:
				plt.figure(figsize=(14, 6))
				for i in range(len(displacements)):
					plt.plot(displacements[i], forces[i], marker='x',
							 label=str(strains[i]))
				plt.legend(loc='right', ncol=1,
						   bbox_to_anchor=(1, 0.5),
						   prop={'weight': 'bold', 'size': 8})
				plt.title(group_name)
				plt.show()
			average_length = np.average(np.asarray(springs_length))
			print("Stiffness parameter K (N): {}".format(k))
			print("The average spring length is {}".format(average_length))

	def add_nonlinear_spring(
			self, name, node_a, node_b,
			force_vec, displacement_vec,
			scale_factor=1, measure_type='elongation',
			interpolate_type='linear', extend_type='constant'
	):
		"""

		Parameters
		----------
		name : [string] name of the element

		node_a : [integer] node A id

		node_b : [integer] node B id

		force_vec: [numpy array] force vector values

		displacement_vec: [numpy array] displacement, stress, stretch vector
			values

		scale_factor : spring force scale factor, default=1

		measure_type: [string] measure type, default=elongation

		interpolate_type: [string] interpolation type for the force
			displacement curve

		extend_type: [string] extend type outside of the interval defined by
			the user

		Returns
		-------
		loadcurve_id: [integer] (default None) the spring force-displacement
		must point loadcurve_id

		"""
		assert measure_type in ['elongation', 'strain', 'stretch'], \
			'Wrong Measure Type, select one of the following: elongation, ' \
			'strain, stretch'

		if self.parent.discrete is None:
			self.parent.discrete = ET.SubElement(self.parent.root, 'Discrete')

		discrete_set = ET.SubElement(self.parent.geometries, 'DiscreteSet',
									 attrib={'name': name})
		discrete_set_element = ET.SubElement(discrete_set, 'delem')
		discrete_set_element.text = to_xml_field([node_a, node_b])

		discrete_mat_element = ET.SubElement(
			self.parent.discrete,
			'discrete_material',
			attrib={
				'id': str(self.discrete_id),
				'name': name,
				'type': 'nonlinear spring'})

		scale_elem = ET.SubElement(
			discrete_mat_element, 'scale',
			# attrib={'lc': str(self.parent.loadcurve_id + 1)}
		)
		scale_elem.text = str(scale_factor)

		measure_elem = ET.SubElement(discrete_mat_element, "measure")
		measure_elem.text = measure_type

		force_elem = ET.SubElement(
			discrete_mat_element, 'force',
			attrib={'type': 'point'}
		)

		# interpolate type
		interpolate_elem = ET.SubElement(
			force_elem, 'interpolate'
		)
		interpolate_elem.text = interpolate_type

		# extend type
		extend_elem = ET.SubElement(
			force_elem, 'extend'
		)
		extend_elem.text = extend_type

		# add points
		points_elem = ET.SubElement(
			force_elem, 'points'
		)

		for i in range(force_vec.shape[0]):
			pt_elem = ET.SubElement(
				points_elem, 'pt'
			)
			pt_elem.text = to_xml_field([displacement_vec[i], force_vec[i]])

		ET.SubElement(
			self.parent.discrete, 'discrete',
			attrib={
				'dmat': str(self.discrete_id),
				'discrete_set': name})
		self.discrete_id += 1
		return self.parent.loadcurve_id

	def add_menisci_springs(self, group_name, origin_geometry,
							origin_node_set,
							origin_node_offset, insertion_geometry,
							insertion_node_set, insertion_node_offset,
							constant, mode):
		"""

		Parameters
		----------
		group_name
		origin_geometry
		origin_node_set
		origin_node_offset
		insertion_geometry
		insertion_node_set
		insertion_node_offset
		constant
		mode


		Returns
		-------

		"""
		spring_number = len(origin_node_set) * len(insertion_node_set)
		# print(spring_number)
		for i, origin_node in enumerate(origin_node_set):
			for j, insertion_node in enumerate(insertion_node_set):
				# insertion_position = insertion_geometry.points[
				#                      insertion_node, :]

				# L = np.linalg.norm(origin_position - insertion_position)
				spring_constant = round(constant / spring_number, 2)
				self.add_spring(group_name + str(i) + '_' + str(j),
								origin_node + origin_node_offset,
								insertion_node + insertion_node_offset,
								spring_constant, mode)

		print(spring_number, spring_constant)

	def add_spring(self, name, node_a, node_b, k, spring_type):
		"""Adds a spring element.

		Parameters
		----------

		name: [string] name of the element

		node_a: [integer] node A id

		node_b: [integer] node B id

		k: [float] stiffness

		spring_type: [string] 'linear spring' or 'tension-only linear spring'

		"""
		if self.parent.discrete is None:
			self.parent.discrete = ET.SubElement(self.parent.root, 'Discrete')

		discrete_set = ET.SubElement(self.parent.geometries, 'DiscreteSet',
									 attrib={'name': name})
		discrete_element = ET.SubElement(discrete_set, 'delem')
		discrete_element.text = to_xml_field([node_a, node_b])
		discrete_material = ET.SubElement(self.parent.discrete,
										  'discrete_material',
										  attrib={'id': str(self.discrete_id),
												  'name': name,
												  'type': spring_type})
		youngs_modulus = ET.SubElement(discrete_material, 'E')
		youngs_modulus.text = str(k)
		ET.SubElement(self.parent.discrete, 'discrete',
					  attrib={'dmat': str(self.discrete_id),
							  'discrete_set': name})
		self.discrete_id += 1
