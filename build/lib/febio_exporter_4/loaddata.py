# -*- coding:utf-8 -*-
# @Time:        7/5/22 3:01 μ.μ.
# @Author:      kostas
# @Email:   krisvas@ece.upatras.gr
# @Filename:    loaddata.py

import xml.etree.ElementTree as ET
from febio_exporter_4.utils import to_xml_field

__doc__ = "LoadData submodule to define load controllers"
__all__ = ["Loaddata"]


class Loaddata:
    """
    Creates an instance of object Loaddata
    """

    def __init__(self, model):
        self.parent = model
        self.root = None

    def add_loadcurve(self, name, loadcurve_id, curve_type, extend_type,
                      abscissa, ordinate):
        """Adds a loadcurve that is associated with the corresponding id.

        Parameters
        ----------

        name: [string] load curve name

        loadcurve_id: [integer] the id of the load curve

        curve_type: [string] interpolation type (e.g., linear, smooth or step)

        extend_type: [string] extrapolation type (e.g., constant, extrapolate,
                     repeat or repeat offset)

        abscissa: [numpy.ndarray] x-coordinates

        ordinate: [numpy.ndarray] y-coordinates

        """
        if self.parent.loaddata is None:
            self.parent.loaddata = ET.SubElement(self.parent.root, 'LoadData')

        self.root = self.parent.loaddata

        assert (curve_type in ['linear', 'smooth', 'step', 'approximation',
                               'control points'])
        assert (extend_type in ['constant', 'extrapolate', 'repeat',
                                'repeat offset'])
        loadcurve = ET.SubElement(self.root, 'load_controller',
                                  attrib={'id': str(loadcurve_id),
                                          'name': name,
                                          'type': 'loadcurve'})
        # 'extend': extend_type})
        interpolate = ET.SubElement(loadcurve, 'interpolate')
        interpolate.text = curve_type.upper()
        points = ET.SubElement(loadcurve, 'points')
        for x, y in zip(abscissa, ordinate):
            point = ET.SubElement(points, 'point')
            point.text = to_xml_field([x, y])

#  TODO add implementation of math and PID controller

