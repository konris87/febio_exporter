# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 14:49:48 2020

Tests deformable fixed and prescribed boundary conditions, as well as,
    sliding-facet-on-facet contact model using dynamic analysis.

## author: Dimitar Stanev (jimstanev@gmail.com)

## maintainer: Konstantinos Risvas (krisvas@ece.upatras.gr)
"""

import numpy as np
from model import FEBioExporter, translate

construct_part = False

# FEBioExporter
model = FEBioExporter()

# geometries
cube_nodes = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
                       [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]])
cube_elements = np.array([[0, 1, 2, 3, 4, 5, 6, 7]])

# add meniscus
femur_id = model.add_material_mooney_rivlin('femur_material', 1, 1, 0, 100)
femur_nodes = translate(cube_nodes, [-0.5, 1.0, 0])
femur_elements = cube_elements
femur_part, femur_node_offset = model.add_part('femur', femur_id, 'hex8',
                                               femur_nodes, femur_elements,
                                               construct_part=construct_part)

# add meniscus
tibia_id = model.add_material_mooney_rivlin('tibia_material', 1, 1, 0, 100)
tibia_nodes = translate(cube_nodes, [-0.5, -0.5, 0])
tibia_elements = cube_elements
tibia_part, tibia_node_offset = model.add_part('tibia', tibia_id, 'hex8',
                                               tibia_nodes, tibia_elements,
                                               construct_part=construct_part)

# add boundary conditions
femur_sup_node_set = np.array([3, 2, 7, 6])
model.add_node_set('femur_sup', femur_sup_node_set,
                   femur_node_offset, femur_part)
model.add_deformable_fixed_displacement('femur_fix_con',
                                        ['x', 'y', 'z'],
                                        'femur_sup')

femur_inf_node_set = np.array([0, 1, 5, 4])
model.add_node_set('femur_inf', femur_inf_node_set,
                   femur_node_offset, femur_part)
femur_pre_lc_id = model \
    .add_deformable_prescribed_displacement('femur_pre_con',
                                            'y', 'femur_inf', 1)
model.add_loadcurve(femur_pre_lc_id, 'linear', 'constant',
                    np.array([0, 1]), np.array([0, -1]))

tibia_inf_node_set = femur_inf_node_set
model.add_node_set('tibia_inf', tibia_inf_node_set,
                   tibia_node_offset, tibia_part)
model.add_deformable_fixed_displacement('tibia_fix_con',
                                        ['x', 'y', 'z'],
                                        'tibia_inf')

# add sliding-facet-on-facet contact model
model.add_surface('femur_master_surf', 'quad4',
                  femur_inf_node_set.reshape(1, -1),
                  femur_node_offset, femur_part)
model.add_surface('tibia_slave_surf', 'quad4',
                  tibia_inf_node_set.reshape(1, -1) + 2,
                  tibia_node_offset, tibia_part)
model.add_surface_pair('femur_tibia_surf_pair',
                       'femur_master_surf',
                       'tibia_slave_surf')
model.add_contact_model('f2t_cont',
                        'sliding-facet-on-facet',
                        'femur_tibia_surf_pair',
                        model.get_default_sliding_elastic_contact_parameters())

# add step
step_parameters = FEBioExporter.get_default_step_parameters()
step_parameters['analysis']['type'] = 'dynamic'
model.add_step(step_parameters)

# export
model.export('tests/', 'febio_test2.feb')