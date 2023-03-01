# -*- coding:utf-8 -*-
# @Time:        7/5/22 2:14 μ.μ.
# @Author:      kostas
# @Email:   krisvas@ece.upatras.gr
# @Filename:    step.py
import copy
import xml.etree.ElementTree as ET
from febio_exporter_4.utils import to_xml_field

__doc__ = "Step submodule to add control steps."
__all__ = ["Step", 'default_step_parameters']


class Step:
	"""
	 "Build an instance of object Control
	"""

	def __init__(self, model):
		"""
		Constructor

		Parameters
		----------
		model: an initialized febio_exporter model
		"""
		self.parent = model
		self.step_counter = 1
		self.step_id = 1
		self.step = None
		self.root = None
		self.control = None
		self.loadcurve_id = None
		self.initial = None

	def add_step(self, name, parameters, use_must_point=False,
				 restart_step=False,
				 add_init_prestrain=False):
		"""Adds a step according to the dictionary format.

		Parameters
		----------

		parameters: [dictionary] parameters of the step

		use_must_point: [boolean] whether to use must points in the time
						stepper
		restart_step: [boolean] whether to use the restart capablity
		add_init_prestrain: [boolean] add initial prestraint sectrion in case
							the prestrain plugin is used

		Returns
		-------

		step: [ET.SubElement] the step xml root

		loadcurve_id: [integer] (default None) the must point loadcurve_id
		"""

		if self.step_counter > 1:
			if self.parent.step is None:
				self.step = ET.SubElement(self.parent.root, 'Step')
			if not restart_step:
				self.root = ET.SubElement(
					self.step, 'step',
					attrib={
						'id': str(self.step_id), 'name': name})
				self.step_id += 1
			else:
				#  TODO implement restart step
				# raise RuntimeError("Not implemented yet! ")
				self.root = ET.SubElement(self.parent.root, 'Step',
										  attrib={'type': 'solid'})
			self.control = ET.SubElement(self.root, 'Control')
		else:
			if self.parent.control is None:
				self.parent.control = ET.SubElement(
					self.parent.root, 'Control')
			self.control = self.parent.control
			self.root = self.control

		if add_init_prestrain:
			self.initial = ET.SubElement(self.root, 'Initial')
		for key, value in parameters.items():
			if key == 'time_stepper':
				time_stepper = ET.SubElement(
					self.control, key, attrib={'type': value["type"]})
				for sub_key, sub_value in value.items():
					if sub_key == 'type':
						pass
					elif use_must_point and sub_key == 'dtmax':
						item = ET.SubElement(
							time_stepper, sub_key,
							attrib={'lc': str(self.parent.loadcurve_id + 1)})
						# item.text = str(1)
						self.loadcurve_id = self.parent.loadcurve_id + 1
						self.parent.loadcurve_id += 1
					else:
						item = ET.SubElement(time_stepper, sub_key)
						item.text = str(sub_value)
			elif key == 'analysis':
				item = ET.SubElement(self.control, key)
				item.text = value.upper()
			elif key == 'restart':
				item = ET.SubElement(self.control, key)
				item.text = str(1)
				item.set('file', value)
			elif key == 'initial':
				item = ET.SubElement(self.initial, 'ic',
									 attrib={'type': 'prestrain'})
				item1 = ET.SubElement(item, 'init')
				item1.text = str(value['init'])
				item2 = ET.SubElement(item, 'reset')
				item2.text = str(value['reset'])
			elif key == 'solver':
				solver = ET.SubElement(
					self.control, key, attrib={'type': value['type']})
				for sub_key, sub_value in value.items():
					if sub_key == 'type':
						pass
					elif sub_key == 'qn_method':
						subitem = ET.SubElement(
							solver, sub_key, attrib={'type': sub_value[
								'type']})
						for ss_key, ss_value in sub_value.items():
							if ss_key == 'type':
								pass
							else:
								ss_elem = ET.SubElement(subitem, ss_key)
								ss_elem.text = str(ss_value)
					else:
						subitem = ET.SubElement(solver, sub_key)
						subitem.text = str(sub_value)
			elif isinstance(value, list):
				item = ET.SubElement(self.control, key)
				item.text = to_xml_field(value)
			else:
				item = ET.SubElement(self.control, key)
				item.text = str(value)

		return self.root, self.loadcurve_id

	def add_restart_step(self, name, parameters, use_must_point=False):
		"""
		Function that adds a step to the restart file
		Returns
		-------

		"""
		if self.step_counter > 1:
			if self.parent.step is None:
				self.step = ET.SubElement(self.parent.root, 'Step')

			else:
				self.step = self.parent.step

			self.root = ET.SubElement(self.step, 'step',
									  attrib={'id': str(
										  self.parent.loadcurve_id + 1),
										  'name': name,
										  'type': "solid"})
			self.control = ET.SubElement(self.root, 'Control')

		for key, value in parameters.items():
			if key == 'time_stepper':
				time_stepper = ET.SubElement(
					self.control, key, attrib={'type': value["type"]})
				for sub_key, sub_value in value.items():
					print(sub_key)
					if sub_key == 'type':
						pass
					if use_must_point and sub_key == 'dtmax':
						item = ET.SubElement(
							time_stepper, sub_key,
							attrib={'lc': str(self.parent.loadcurve_id + 1)})
						item.text = '1'
						self.loadcurve_id = self.parent.loadcurve_id + 1
						self.parent.loadcurve_id += 1
					else:
						item = ET.SubElement(time_stepper, sub_key)
						item.text = str(sub_value)
			elif key == 'analysis':
				item = ET.SubElement(self.control, key)
				item.text = value.upper()
			elif key == 'restart':
				item = ET.SubElement(self.control, key)
				item.text = str(1)
				item.set('file', value)
			elif key == 'initial':
				item = ET.SubElement(self.initial, 'ic',
									 attrib={'type': 'prestrain'})
				item1 = ET.SubElement(item, 'init')
				item1.text = str(value['init'])
				item2 = ET.SubElement(item, 'reset')
				item2.text = str(value['reset'])
			elif key == 'solver':
				solver = ET.SubElement(
					self.control, key, attrib={'type': value['type']})
				for sub_key, sub_value in value.items():
					if sub_key == 'type':
						pass
					if sub_key == 'qn_method':
						subitem = ET.SubElement(
							solver, sub_key, attrib={'type': sub_value[
								'type']})
						max_ups = ET.SubElement(subitem, 'max_ups')
						max_ups.text = sub_value['max_ups']
					else:
						subitem = ET.SubElement(solver, sub_key)
						subitem.text = str(sub_value)
			else:
				item = ET.SubElement(self.control, key)
				item.text = str(value)

		return self.root, self.loadcurve_id

	def get_default_step_parameters(self):
		parameters = {
			'analysis': 'static',
			'time_steps': 20,
			'step_size': 0.05,
			'plot_range': [0, -1],
			'plot_level': 'PLOT_MAJOR_ITRS',
			'output_level': 'OUTPUT_MAJOR_ITRS',
			'adaptor_re_solve': 1,
			'time_stepper': {
				'type': 'default',
				'dtmin': 0.00000001,
				'dtmax': 1,
				'max_retries': 30,
				'opt_iter': 10,
				'aggressiveness': 0,
				'cutback': 0.8
			},
			'solver': {
				'type': 'solid',
				'symmetric_stiffness': 0,
				'equation_scheme': 'staggered',
				'equation_order': 'default',
				'optimize_bw': 0,
				'lstol': 0.9,
				'lsmin': 0.01,
				'lsiter': 5,
				'max_refs': 15,
				'check_zero_diagonal': 0,
				'zero_diagonal_tol': 0,
				'force_partition': 0,
				'reform_each_time_step': 1,
				'reform_augment': 0,
				'diverge_reform': 1,
				'min_residual': 0.001,
				'max_residual': 0,
				'dtol': 0.01,
				'etol': 0.1,
				'rtol': 0,
				'rhoi': -2,
				'alpha': 1,
				'beta': 0.25,
				'gamma': 0.5,
				'logSolve': 0,
				'arc_length': 0,
				'arc_length_scale': 0,
				'qn_method':
					{'type': 'Broyden',
					 'max_ups': str(0),
					 'max_buffer_size': 0,
					 'cycle_buffer': 1,
					 'cmax': 10000,
					 },
			},
		}

		return parameters.copy()


# dictionary containing default step parameters
default_step_parameters = copy.copy({
	'analysis': 'static',
	'time_steps': 20,
	'step_size': 0.05,
	'plot_range': [0, -1],
	'plot_level': 'PLOT_MAJOR_ITRS',
	'output_level': 'OUTPUT_MAJOR_ITRS',
	'adaptor_re_solve': 1,
	'time_stepper': {
		'type': 'default',
		'dtmin': 0.00000001,
		'dtmax': 1,
		'max_retries': 30,
		'opt_iter': 10,
		'aggressiveness': 0,
		'cutback': 0.5
	},
	'solver': {
		'type': 'solid',
		'symmetric_stiffness': 0,
		'equation_scheme': 'staggered',
		'equation_order': 'default',
		'optimize_bw': 0,
		'lstol': 0.9,
		'lsmin': 0.01,
		'lsiter': 5,
		'max_refs': 15,
		'check_zero_diagonal': 0,
		'zero_diagonal_tol': 0,
		'force_partition': 0,
		'reform_each_time_step': 1,
		'reform_augment': 0,
		'diverge_reform': 1,
		'min_residual': 0.001,
		'max_residual': 0,
		'dtol': 0.01,
		'etol': 0.1,
		'rtol': 0,
		'rhoi': -2,
		'alpha': 1,
		'beta': 0.25,
		'gamma': 0.5,
		'logSolve': 0,
		'arc_length': 0,
		'arc_length_scale': 0,
		'qn_method':
			{'type': 'Broyden',
			 'max_ups': str(10),
			 'max_buffer_size': 0,
			 'cycle_buffer': 1,
			 'cmax': 10000,
			 },
	},
})
