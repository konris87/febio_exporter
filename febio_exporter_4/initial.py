# -*- coding:utf-8 -*-
# @Time:        6/10/22 1:14 μ.μ.
# @Author:      kostas
# @Email:   krisvas@ece.upatras.gr
# @Filename:    initial.py

import xml.etree.ElementTree as ET

__doc__ = "Initial submodule to add initial conditions to a FEBio model"
__all__ = ["Initial"]


class Initial:
    """
    Build an instance of object "Initial"
    """

    def __init__(self, model):
        self.parent = model

    def add_prestrain_condition(self, name, init_val=1, reset_val=1):
        """
        Add prestrain initial condition

        Parameters
        ----------
        reset_val
        init_val
        name

        Returns
        -------

        """
        if self.parent.initial is None:
            self.parent.initial = ET.SubElement(
                self.parent.root, "Initial")

        prestrain_ic = ET.SubElement(
            self.parent.initial,
            'ic',
            attrib={
                "name": name,
                "type": "prestrain"
            }
        )
        init = ET.SubElement(
            prestrain_ic, "init")
        init.text = str(init_val)
        reset = ET.SubElement(
            prestrain_ic, "reset"
        )
        reset.text = str(reset_val)
