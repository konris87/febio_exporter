#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 12/17/2022 7:55 PM
# @Author : Konstantinos Risvas
# E-mail: krisvas@ece.upatras.gr
import os.path
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
        self.archive.text = os.path.basename(dmp_file)
        self.loadcurve_id = model.loadcurve_id
        self.step = Et.SubElement(
            self.root, 'Step',
            attrib={'type': "solid"}
        )
        self.loaddata = Et.SubElement(self.root, 'LoadData')
        self.step_id = 1
        self.parent = model

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

        # if self.step_counter > 1:
        #     if self.parent.step is None:
        #         self.step = Et.SubElement(self.parent.root, 'Step')
        #     if not restart_step:
        #         self.root = Et.SubElement(
        #             self.step, 'step',
        #             attrib={
        #                 'id': str(self.step_id), 'name': name})
        #         self.step_id += 1
        #     else:
        #         #  TODO implement restart step
        #         # raise RuntimeError("Not implemented yEt! ")
        #         self.root = Et.SubElement(self.parent.root, 'Step',
        #                                   attrib={'type': 'solid'})
        #     self.control = Et.SubElement(self.root, 'Control')
        # else:
        #     if self.parent.control is None:
        #         self.parent.control = Et.SubElement(
        #             self.parent.root, 'Control')
        #     self.control = self.parent.control
        #     self.root = self.control
        root = Et.SubElement(
            self.step, 'step',
            attrib={'id': str(self.step_id), 'name': name, "type": "solid"})
        self.control = Et.SubElement(root, 'Control')

        self.step_id += 1

        for key, value in parameters.items():
            if key == 'time_stepper':
                time_stepper = Et.SubElement(
                    self.control, key, attrib={'type': value["type"]})
                for sub_key, sub_value in value.items():
                    if sub_key == 'type':
                        pass
                    elif use_must_point and sub_key == 'dtmax':
                        item = Et.SubElement(
                            time_stepper, sub_key,
                            attrib={'lc': str(self.parent.loadcurve_id + 1)})
                        # item.text = str(1)
                        self.loadcurve_id = self.parent.loadcurve_id + 1
                        self.parent.loadcurve_id += 1
                    else:
                        item = Et.SubElement(time_stepper, sub_key)
                        item.text = str(sub_value)
            elif key == 'analysis':
                item = Et.SubElement(self.control, key)
                item.text = value.upper()
            elif key == 'restart':
                item = Et.SubElement(self.control, key)
                item.text = str(1)
                item.set('file', value)
            elif key == 'initial':
                item = Et.SubElement(self.initial, 'ic',
                                     attrib={'type': 'prestrain'})
                item1 = Et.SubElement(item, 'init')
                item1.text = str(value['init'])
                item2 = Et.SubElement(item, 'reset')
                item2.text = str(value['reset'])
            elif key == 'solver':
                solver = Et.SubElement(
                    self.control, key)
                for sub_key, sub_value in value.items():
                    if sub_key == 'type':
                        pass
                    elif sub_key == 'qn_method':
                        subitem = Et.SubElement(
                            solver, sub_key, attrib={'type': sub_value[
                                'type']})
                        for ss_key, ss_value in sub_value.items():
                            if ss_key == 'type':
                                pass
                            else:
                                ss_elem = Et.SubElement(subitem, ss_key)
                                ss_elem.text = str(ss_value)
                    else:
                        subitem = Et.SubElement(solver, sub_key)
                        subitem.text = str(sub_value)
            elif isinstance(value, list):
                item = Et.SubElement(self.control, key)
                item.text = to_xml_field(value)
            else:
                item = Et.SubElement(self.control, key)
                item.text = str(value)

        return root, self.loadcurve_id

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
