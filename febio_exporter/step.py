# -*- coding:utf-8 -*-
# @Time:        7/5/22 2:14 μ.μ.
# @Author:      kostas
# @Email:   krisvas@ece.upatras.gr
# @Filename:    step.py

import xml.etree.ElementTree as ET

__doc__ = "Step submodule to add control steps."
__all__ = ["Step"]


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
        self.step = None
        self.root = None
        self.control = None
        self.loadcurve_id = None

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
                    attrib={'id': str(self.parent.loadcurve_id),
                            'name': name})
            else:
                #  TODO implement restart step
                raise RuntimeError("Not implemented yet! ")
                # self.root = ET.SubElement(self.root, 'Step',
                #                      attrib={'Type': 'solid'.upper()})
            self.control = ET.SubElement(self.root, 'Control')
        else:
            if self.parent.control is None:
                self.parent.control = ET.SubElement(self.parent.root, 'Control')
            self.control = self.parent.control

        if add_init_prestrain:
            initial = ET.SubElement(self.root, 'Initial')
        for key, value in parameters.items():
            if key == 'time_stepper':
                time_stepper = ET.SubElement(self.control, key)
                for sub_key, sub_value in value.items():
                    if use_must_point and sub_key == 'dtmax':
                        item = ET.SubElement(
                            time_stepper, sub_key,
                            attrib={'lc': str(self.parent.loadcurve_id)})
                        # item.text = ''
                        self.loadcurve_id = self.parent.loadcurve_id
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
                item = ET.SubElement(initial, 'ic',
                                     attrib={'type': 'prestrain'})
                item1 = ET.SubElement(item, 'init')
                item1.text = str(value['init'])
                item2 = ET.SubElement(item, 'reset')
                item2.text = str(value['reset'])
            elif key == 'solver':
                solver = ET.SubElement(self.control, key)
                for sub_key, sub_value in value.items():
                    subitem = ET.SubElement(solver, sub_key)
                    subitem.text = str(sub_value)
            else:
                item = ET.SubElement(self.control, key)
                item.text = str(value)

        return self.root, self.loadcurve_id

