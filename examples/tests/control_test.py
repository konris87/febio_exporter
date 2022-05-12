# -*- coding:utf-8 -*-
# @Time:        7/5/22 2:39 μ.μ.
# @Author:      kostas
# @Email:   krisvas@ece.upatras.gr
# @Filename:    control_test.py

import copy
from model import FEBioExporter
from step import Step
from loaddata import Loaddata
from examples.knee_data import FEBio_step

model = FEBioExporter()

# add a step
step_parameters = copy.copy(FEBio_step)
step = Step(model)
step.step_counter = 2
step1, step1_lc = step.add_step("step_1", step_parameters, True)
step2, step2_lc = step.add_step("step_2", step_parameters, True)

# add a loaddcurve to control must points
load_data = Loaddata(model)
load_data.add_loadcurve(step2_lc, 'step', 'constant',
                        [0.0, 1.0], [0.0, 1.0])

model.export('', 'febio_test_control_multiple_steps.feb')
