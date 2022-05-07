# -*- coding: utf-8 -*-
# @Time    : 20/3/22 7:38 μ.μ.
# @Author  : Kostas Risvas
# @Email   : krisvas@ece.upatras.gr
# @File    : febio_exporter_modular1.py
import os
import copy
import sys
import numpy as np
from model import FEBioExporter
from model import Discrete
from model import Rigid
# from util import readkneedata
from utils import scale, translate, select_nodes_inside_boundary, transform
from aclr_knee_data import FEBio_rigidbody_bone, FEBio_step

sys.path.insert(0, os.path.abspath('../meshio'))
import meshio


def return_nodesets(sphere, scale_vector_a, scale_vector_b,
                    body_a, body_b,
                    body_a_landmark, body_b_landmark):
    body_a_sphere = copy.copy(sphere)
    body_a_sphere.points = scale(body_a_sphere.points,
                                 scale_vector_a[0],
                                 scale_vector_a[1],
                                 scale_vector_a[2])
    body_a_sphere.points = translate(body_a_sphere.points,
                                     body_a_landmark)
    body_a_nodes = select_nodes_inside_boundary(body_a, body_a_sphere)

    body_b_sphere = copy.copy(sphere)
    body_b_sphere.points = scale(body_b_sphere.points,
                                 scale_vector_b[0],
                                 scale_vector_b[1],
                                 scale_vector_b[2])
    body_b_sphere.points = translate(body_b_sphere.points,
                                     body_b_landmark)
    body_b_nodes = select_nodes_inside_boundary(body_b, body_b_sphere)

    return body_a_nodes, body_b_nodes


use_parts = False
# Subject Data
subject_data = readkneedata("../../data/subject_data.xml", 'oks003')

# ACL ligament
acl_a_fem_landmark = subject_data['ACL']['femur_A_acl_landmark'],
acl_a_tib_landmark = subject_data['ACL']['tibia_A_acl_landmark']
pcl_a_fem_landmark = subject_data['PCL']['femur_A_pcl_landmark'],
pcl_a_tib_landmark = subject_data['PCL']['tibia_A_pcl_landmark'],

# Data Dir
data_dir = os.path.abspath("../../data/oks003/geometries_no_acl")
common_dir = os.path.abspath("../../data/oks003/geometries_common")
sphere = meshio.read(common_dir + "/sphere.stl")
femur = meshio.read(data_dir + "/femur.stl")
tibia = meshio.read(data_dir + "/tibia.stl")

#
acl_a_tib_landmark = tibia.points[acl_a_tib_landmark]
acl_a_fem_landmark = femur.points[acl_a_fem_landmark]

pcl_a_tib_landmark = tibia.points[pcl_a_tib_landmark]
pcl_a_fem_landmark = femur.points[pcl_a_fem_landmark]

tibia_acl_nodeset, femur_acl_nodeset = return_nodesets(
    sphere,
    [7, 2, 3], [7, 3, 3],
    tibia, femur,
    acl_a_tib_landmark, acl_a_fem_landmark)

tibia_pcl_nodeset, femur_pcl_nodeset = return_nodesets(
    sphere,
    [7, 2, 3], [7, 3, 3],
    tibia, femur,
    pcl_a_tib_landmark, pcl_a_fem_landmark)

# joint info
rotation = np.identity(3)
origin = np.array([0, 0, 0])

model = FEBioExporter()
discrete = Discrete(model)
rigid = Rigid(model)

# create bone parts
print("Creating femur\n")
femur_part = None
if use_parts:
    femur_part = model.create_part('femur')

femur_rigidbody_bone = copy.copy(FEBio_rigidbody_bone)
femur_rigidbody_bone['center_of_mass'] = origin.tolist()
femur_material_id = model.add_material('femur_material',
                                       femur_rigidbody_bone)
model.add_domain('femur', 'femur_material', 'Shell')

femur_part, femur_node_offset = model.add_part(
    'femur',
    femur_material_id,
    'tri3',
    transform(femur.points, rotation,
              origin, order='reverse'),
    femur.cells['triangle'],
    construct_part=use_parts)

print("Creating tibia\n")
tibia_material_id = model.add_material('tibia_material',
                                       femur_rigidbody_bone)
tibia_part, tibia_node_offset = model.add_part(
    'tibia',
    tibia_material_id,
    'tri3',
    transform(tibia.points, rotation,
              origin, order='reverse'),
    tibia.cells['triangle'],
    construct_part=use_parts)
model.add_domain('tibia', 'tibia_material', 'Shell')

################################################################################
print("Creating cylindrical joint")
knee_joint_y_parameters = \
    FEBioExporter.get_default_cylindrical_joint_parameters()
knee_joint_y_parameters['body_a'] = femur_material_id
knee_joint_y_parameters['body_b'] = tibia_material_id
knee_joint_y_parameters['joint_origin'] = origin
knee_joint_y_parameters['joint_axis'] = [1, 0, 0]
knee_joint_y_parameters['moment_penalty'] = 3e7
knee_joint_y_parameters['auto_penalty'] = 0
knee_joint_y_parameters['angtol'] = 0.0001
knee_joint_y_parameters['prescribed_rotation'] = 1.0
knee_joint_y_parameters['rotation'] = 1
# knee_joint_y_parameters['prescribed_translation'] = 1.0
# knee_joint_y_parameters['translation'] = 1
knee_joint_y_lc = rigid.add_cylindrical_joint(
    'knee_anterior_posterior',
    knee_joint_y_parameters)
# febio_model.add_loadcurve(knee_joint_y_lc[0], 'linear', 'constant',
#                           total_t, anterior_translation)
model.add_loadcurve(knee_joint_y_lc[0], 'linear', 'constant',
                    np.linspace(0, 1, 10), np.linspace(0, 1, 1))

print("Creating ACL springs\n")
discrete.add_discrete_element('ACL_test',
                              tibia, tibia_acl_nodeset, tibia_node_offset,
                              femur, femur_acl_nodeset, femur_node_offset,
                              1, 366, 22, 0.4, 0, 0, False)

print("Creating PCL springs\n")
discrete.add_discrete_element('PCL_test',
                              tibia, tibia_pcl_nodeset, tibia_node_offset,
                              femur, femur_pcl_nodeset, femur_node_offset,
                              1, 366, 22, 0.4, 0, 0, False)

# Add Boundary conditions

################################################################################
# Add analysis step
t1 = np.linspace(0, 0.5, 21)  # knee flexion
t2 = np.linspace(0.55, 1.05, 10)  # loading

must_point_stepsize_step1 = 0.05
step1_stepsize1 = 0.05
step1_stepsize2 = 0.05
step1_parameters = copy.copy(FEBio_step)
# step1_parameters['time_stepper']['max_retries'] = 10
# step1_parameters['time_stepper']['opt_iter'] = 30
step1_parameters['time_stepper']['dtmax'] = 0.05
step1_parameters['time_stepper']['dtmin'] = 0.001
# step1_parameters['solver']['min_residual'] = 0.01

# if version == 'VV1':
time_steps1 = (t1[-1] - 0.0) / step1_stepsize1
must_points1 = np.linspace(0, t1[-1], num=int(round(time_steps1)) + 1)
time_steps2 = (t2[-1] - must_points1[-1]) / step1_stepsize2
must_points2 = np.linspace(must_points1[-1] + step1_stepsize2,
                           t2[-1],
                           num=int(round(time_steps2)))

idx = None
must_point_time = np.concatenate((must_points1,
                                  must_points2[:idx]))
time_steps = (must_point_time[-1] - must_point_time[0]) / step1_stepsize1
step1_parameters['time_steps'] = int(np.round(time_steps))
step1_parameters['step_size'] = step1_stepsize1
step1, step1_lc = model.add_step("Step01", step1_parameters, True)
t_step1 = must_point_time
model.add_loadcurve(step1_lc, 'step', 'constant',
                    t_step1, np.ones(len(t_step1)))

################################################################################
# Output
model.separate_section(model.geometries, './tests',
                       'model_test_geometry')

model.separate_section(model.discrete, './tests',
                       'model_test_discrete')

model.export('tests/', 'febio_test_modular1.feb')
#
print("test")
