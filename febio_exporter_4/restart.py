#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 12/17/2022 7:55 PM
# @Author : Konstantinos Risvas
# E-mail: krisvas@ece.upatras.gr
import xml.etree.ElementTree as Et
import febio_exporter_4
from febio_exporter_4.utils import to_xml_field


class FEBioRestart(febio_exporter_4.FEBioExporter4):

	def __init__(self, dmp_file, model):
		super().__init__()
		self.root = Et.Element(
			"febio_restart", attrib={
				"version": "4.0"
			})

		self.archive = Et.SubElement(self.root, "Archive")
		self.archive.text = dmp_file
		self.loadcurve_id = model.loadcurve_id
		self.step = Et.SubElement(self.root, 'Step')
		self.loaddata = Et.SubElement(self.root, 'LoadData')

	def add_restart_step(self, name, parameters, use_must_point=0):
		step_el = Et.SubElement(
			self.root, "Step", attrib={
				"name": name, "type": "solid"})

		control = Et.SubElement(step_el, 'Control')

		for key, value in parameters.items():
			# if key == 'time_stepper':
			# 	time_stepper = Et.SubElement(control, key)
			# 	for sub_key, sub_value in value.items():
			# 		if use_must_point and sub_key == 'dtmax':
			# 			item = Et.SubElement(
			# 				time_stepper, sub_key,
			# 				attrib={'lc': str(self.loadcurve_id + 1)})
			# 			self.loadcurve_id += 1
			# 		else:
			# 			item = Et.SubElement(time_stepper, sub_key)
			# 			item.text = str(sub_value)
			# elif key == 'analysis':
			# 	item = Et.SubElement(control, key)
			# 	item.text = value.upper()
			# elif key == 'restart':
			# 	item = Et.SubElement(control, key)
			# 	item.text = str(1)
			# 	item.set('file', value)
			# elif key == 'solver':
			# 	solver = Et.SubElement(control, key)
			# 	for sub_key, sub_value in value.items():
			# 		subitem = Et.SubElement(solver, sub_key)
			# 		subitem.text = str(sub_value)
			# else:
			item = Et.SubElement(control, key)
			item.text = str(value)

		return step_el, self.loadcurve_id

	def add_loadcurve(self, loadcurve_id, curve_type, extend_type,
					   abscissa, ordinate):
		"""Adds a loadcurve that is associated with the corresponding id.

		Parameters
		----------

		loadcurve_id: [integer] the id of the load curve

		curve_type: [string] interpolation type (e.g., linear, smooth or step)

		extend_type: [string] extrapolation type (e.g., constant, extrapolate,
					 repeat or repeat offset)

		abscissa: [numpy.ndarray] x-coordinates

		ordinate: [numpy.ndarray] y-coordinates

		"""

		if self.loaddata is None:
			self.loaddata = Et.SubElement(self.root, 'LoadData')

		assert (curve_type in ['linear', 'smooth', 'step', 'approximation',
							   'control points'])
		assert (extend_type in ['constant', 'extrapolate', 'repeat',
								'repeat offset'])
		loadcurve = Et.SubElement(
			self.loaddata, 'loadcurve',
			attrib={
				'id': str(loadcurve_id),
				'type': curve_type,
				'extend': extend_type
			})
		# 'extend': extend_type})
		# interpolate = Et.SubElement(loadcurve, 'interpolate')
		# interpolate.text = curve_type.upper()
		# points = Et.SubElement(loadcurve, 'points')
		for x, y in zip(abscissa, ordinate):
			point = Et.SubElement(loadcurve, 'loadpoint')
			point.text = to_xml_field([x, y])
