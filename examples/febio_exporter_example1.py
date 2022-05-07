# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 14:45:10 2020

Constructs a simple model containing two rigid bodies and one
    deformable.

@author: Dimitar Stanev (jimstanev@gmail.com)

@maintainer: Konstantinos Risvas (krisvas@ece.upatras.gr)

"""
import numpy as np
from model import FEBioExporter
from utils import translate, scale

construct_part = False

# FEBioExporter
model = FEBioExporter()

# geometries
cube_nodes = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
                       [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]])
cube_elements = np.array([[0, 1, 2, 3, 4, 5, 6, 7]])

# add meniscus
meniscus_id = model.add_material_mooney_rivlin('meniscus_material',
                                               1, 1, 0, 100)
meniscus_nodes = translate(cube_nodes, [-0.5, -0.5, 0])
meniscus_elements = cube_elements
meniscus_part, meniscus_node_offset = model.add_part('meniscus',
                                                     meniscus_id,
                                                     'hex8',
                                                     meniscus_nodes,
                                                     meniscus_elements,
                                                     construct_part=construct_part)

# add tibia
tibia_id = model.add_material_rigid_body('tibia_material', 1,
                                         [0, -1.5, 0.5])
tibia_nodes = translate(scale(translate(cube_nodes, [-0.5, -0.5, 0]),
                              [1, 2, 1]), [0, -1.5, 0])
tibia_elements = cube_elements
tibia_part, tibia_node_offset = model.add_part('tibia',
                                               tibia_id,
                                               'hex8',
                                               tibia_nodes,
                                               tibia_elements,
                                               construct_part=construct_part)

# add femur
femur_id = model.add_material_rigid_body('femur_material', 1,
                                         [0, 1.5, 0.5])
femur_nodes = translate(scale(translate(cube_nodes, [-0.5, -0.5, 0]),
                              [1, 2, 1]), [0, 1.5, 0])
femur_elements = cube_elements
tibia_part, tibia_node_offset = model.add_part('femur',
                                               femur_id,
                                               'hex8',
                                               femur_nodes,
                                               femur_elements,
                                               construct_part=construct_part)

# boundary conditions

# m2t connector
meniscus2tibia = np.array([0, 1, 5, 4])
model.add_node_set('m2t', meniscus2tibia, meniscus_node_offset,
                   meniscus_part)
model.add_rigid_connector('m2t_connector', tibia_id, 'm2t')

# m2f connector
meniscus2femur = np.array([3, 2, 6, 7])
model.add_node_set('m2f', meniscus2femur, meniscus_node_offset,
                   meniscus_part)
model.add_rigid_connector('m2f_connector', femur_id, 'm2f')

# tibia fixed
model.add_rigid_body_fixed_constraint('tibia_constraints', tibia_id,
                                      ['x', 'y', 'z', 'Rx', 'Ry', 'Rz'])

# femur fixed
model.add_rigid_body_fixed_constraint('femur_constraints', femur_id,
                                      ['x', 'z', 'Rx', 'Rz'])
femur_motion_y_id = model \
    .add_rigid_body_prescribed_constraint('femur_prescribed_motion',
                                          femur_id, 'y', 1, 'prescribed')
femur_force_Ry_id = model \
    .add_rigid_body_prescribed_constraint('femur_prescribed_force',
                                          femur_id, 'Ry', 1, 'force')

t = np.linspace(0, 1, 10)
model.add_loadcurve(femur_motion_y_id, 'smooth', 'constant',
                    t, .5 * np.sin(2 * np.pi * t) + 0.5)
model.add_loadcurve(femur_force_Ry_id, 'linear', 'extrapolate',
                    t, 0.01 * np.sin(2 * np.pi * t))

# add step
model.add_step(FEBioExporter.get_default_step_parameters())

# export
model.export('tests/', 'febio_test1.feb')
