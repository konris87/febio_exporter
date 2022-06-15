# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 14:45:10 2020

Constructs a simple model containing two rigid bodies and one
    deformable. The deformable is connected to the bottom rigid body. A
    sliding elastic contact s defined between the upper rigid body and the
    deformable

@author: Dimitar Stanev (jimstanev@gmail.com)

@maintainer: Konstantinos Risvas (krisvas@ece.upatras.gr)

"""
import copy
import numpy as np
import meshio
from febio_exporter.utils import translate, scale
from febio_exporter import model, mesh, material, boundary, rigid, loaddata, \
    step, contact

construct_part = False

# FEBioExporter
model = model.FEBioExporter()
meshes = mesh.Mesh(model)
materials = material.Material(model)
boundaries = boundary.Boundary(model)
contacts = contact.Contact(model)
rigid = rigid.Rigid(model)
loadcurves = loaddata.Loaddata(model)
steps = step.Step(model)

# set a flag to execute FEBio at the end of model creation
execute_model = 1

# set a flag to visualize the geometry prior to execution
visualize_mesh = 1

################################################################################
# Geometries and Materials
################################################################################

# load geometries, build geometry parts, and assign materials
cube = meshio.read('./data/cube.stl')
cube_hex_mesh = meshio.read("data/cube_1.msh")

# add the bottom cube
bottom_cube = copy.copy(cube)
bottom_cube_material_parameters = \
    materials.get_default_rigid_body_parameters()
bottom_cube_material_parameters['density'] = 1
bottom_cube_material_parameters['center_of_mass'] = [0, 0, -1.5]
bottom_cube_material_id = materials.add_material(
    'bottom_cube_material',
    bottom_cube_material_parameters)

meshes.add_domain('bottom_cube', 'bottom_cube_material', 'Shell')
bottom_cube_part = None
bottom_cube_nodes = scale(translate(bottom_cube.points, [0.0, 0.0, -1.5]),
                          [2.0, 2.0, 1.0]),
bottom_cube_node_offset = meshes.add_nodes(
    'bottom_cube_nodes',
    bottom_cube_nodes[0],
    bottom_cube_part
)
meshes.add_element('bottom_cube_elements',
                   bottom_cube_material_id,
                   'tri3',
                   bottom_cube.cells_dict['triangle'],
                   bottom_cube_node_offset,
                   bottom_cube_part)

# add a thin layer on top of the cube that is rigidly attached to it
layer_material_parameters = materials.get_default_fung_orthotropic_parameters()
layer_material_parameters['E1'] = 125
layer_material_parameters['E2'] = 27.5
layer_material_parameters['E3'] = 27.5
layer_material_parameters['G12'] = 2
layer_material_parameters['G23'] = 12.5
layer_material_parameters['G31'] = 2
layer_material_parameters['v12'] = 0.1
layer_material_parameters['v23'] = 0.33
layer_material_parameters['v31'] = 0.1
layer_material_parameters['c'] = 1
layer_material_parameters['k'] = 10

# create bottom layer material
bottom_layer_material_id = materials.add_material('bottom_layer_material',
                                                  layer_material_parameters)

meshes.add_domain('bottom_layer', 'bottom_layer_material', 'Solid')

bottom_layer_nodes = translate(scale(
    translate(cube_hex_mesh.points, [-0.5, -0.5, -0.5]),
    [4, 4, 0.5]), [0.0, 0.0, -0.25]),
bottom_layer_part, bottom_layer_node_offset = meshes.add_part(
    'bottom_layer',
    bottom_layer_material_id,
    'hex8',
    bottom_layer_nodes[0],
    cube_hex_mesh.cells_dict['hexahedron'],
    construct_part=construct_part, root=None)

# create top layer material
top_layer_material_id = materials.add_material('top_layer_material',
                                               layer_material_parameters)
meshes.add_domain('top_layer', 'top_layer_material', 'Solid')

top_layer_nodes = translate(
    scale
    (translate(cube_hex_mesh.points,
               [-0.5, -0.5, -0.5]),
     [2, 2, 0.5]), [0.0, 0.0, 0.25]),

top_layer_part, top_layer_node_offset = meshes.add_part(
    'top_layer',
    top_layer_material_id,
    'hex8',
    top_layer_nodes[0],
    # cube_hex_mesh.points,
    cube_hex_mesh.cells_dict['hexahedron'],
    construct_part=construct_part, root=None)

# add the top cube
top_cube = copy.copy(cube)
top_cube_material_properties = \
    materials.get_default_rigid_body_parameters()
top_cube_material_properties['density'] = 1
top_cube_material_properties['center_of_mass'] = [0, 0, 1.5]
top_cube_material_id = materials.add_material('top_cube_material',
                                              top_cube_material_properties)

meshes.add_domain('top_cube', 'top_cube_material', 'Shell')
top_cube_part = None
top_cube_nodes = translate(top_cube.points, [0, 0, 1.5])
top_cube_node_offset = meshes.add_nodes(
    'top_cube_nodes',
    top_cube_nodes,
    top_cube_part
)
meshes.add_element('top_cube_elements',
                   top_cube_material_id, 'tri3',
                   top_cube.cells_dict['triangle'],
                   top_cube_node_offset,
                   top_cube_part)

################################################################################
# Rigid Connectors
################################################################################

# bottom_cube - layer connector
# first define a nodeset that contains the nodes of the layer that will be
# rigidly attached to the bottom cube
bottom_layer_connection_nodes = np.array(
    [0, 1, 2, 3, 8, 9, 11, 13, 20, 27, 28,
     30, 32, 39, 60, 61, 63, 84, 88, 85, 86,
     92, 108, 109, 113])

top_layer_connection_nodes = np.array([
    3, 4, 5, 6, 15, 16, 17, 18, 24, 49, 50, 51, 52, 57, 75, 76, 77, 81, 99,
    100, 101, 105, 118, 119, 122
])

meshes.add_node_set('bottom_layer_to_bottom_cube_nodes',
                    bottom_layer_connection_nodes,
                    bottom_layer_node_offset,
                    bottom_layer_part)

meshes.add_node_set('top_layer_to_top_cube_nodes',
                    top_layer_connection_nodes,
                    top_layer_node_offset,
                    top_layer_part)

# create the rigid connectors that connect the deformable to the rigid body
boundaries.add_rigid_connector('bottom_layer_2_bottom_connector',
                               bottom_cube_material_id,
                               'bottom_layer_to_bottom_cube_nodes')

boundaries.add_rigid_connector('top_layer_2_top_connector',
                               top_cube_material_id,
                               'top_layer_to_top_cube_nodes')

################################################################################
# Contacts
################################################################################
# add a sliding elastic contact between the layer top surface and the bottom
# surface of the upper cube
top_layer_surfaces = np.array([
    [4, 50, 58, 51], [50, 16, 52, 58], [16, 76, 82, 52], [76, 5, 77, 82],
    [51, 58, 53, 17], [58, 52, 25, 53], [52, 82, 78, 25], [82, 77, 18, 78],
    [17, 53, 106, 100], [53, 25, 101, 106], [25, 78, 123, 101],
    [78, 18, 119, 123], [100, 106, 102, 7], [106, 101, 19, 102],
    [101, 123, 120, 19], [123, 119, 6, 120]
])

bottom_layer_surfaces = np.array([
    [3, 86, 92, 84], [86, 13, 85, 92], [13, 109, 113, 85], [109, 2, 108, 113],
    [84, 92, 32, 9], [92, 85, 20, 32], [85, 113, 63, 20], [113, 108, 11, 63],
    [9, 32, 39, 28], [32, 20, 30, 39], [20, 63, 68, 30], [63, 11, 61, 68],
    [28, 39, 27, 0], [39, 30, 8, 27], [30, 68, 60, 8], [68, 61, 1, 60]
])

layer_top_surface = meshes.add_surface(
    'layer_top_surface',
    'quad4',
    top_layer_surfaces,
    bottom_layer_node_offset,
    bottom_layer_part)

layer_bottom_surface = meshes.add_surface(
    'layer_bottom_surface',
    'quad4',
    bottom_layer_surfaces,
    top_layer_node_offset,
    top_layer_part)

contacts.add_surface_pair(
    "layers_surface_pair",
    'layer_bottom_surface',
    'layer_top_surface')

sliding_elastic_parameters = \
    contacts.get_default_sliding_elastic_contact_parameters()
sliding_elastic_parameters['two_pass'] = 1
sliding_elastic_parameters['search_radius'] = 1
sliding_elastic_parameters['auto_penalty'] = 1
contacts.add_contact_model(
    "layers_elastic_contact",
    'sliding-elastic',
    'layers_surface_pair',
    sliding_elastic_parameters
)

################################################################################
# Controls
################################################################################
# add a control step
steps.step_counter = 1
step_parameters = steps.get_default_step_parameters()
step_parameters['time_stepper']['dtmax'] = 0.05
step_parameters['time_stepper']['dtmin'] = 0.001
step_parameters['time_stepper']['max_retries'] = 15
step_parameters['solver']['max_refs'] = 25
step_stepsize = 0.05
time_steps = (1 - 0.0) / step_stepsize
must_points = np.round(
    np.linspace(0.0 + step_stepsize, 1, num=int(round(time_steps)) + 1), 3)
step_parameters['time_steps'] = int(np.round(time_steps)) + 1
step_parameters['step_size'] = step_stepsize
step, step_lc = steps.add_step("Step_0", step_parameters, True)
loadcurves.add_loadcurve(step_lc, 'step', 'constant',
                         must_points, np.ones(len(must_points)))

################################################################################
# Boundary Conditions
################################################################################
# bottom cube is fixed
rigid.add_rigid_body_fixed_constraint('bottom_cube_constraints',
                                      bottom_cube_material_id,
                                      ['Rx', 'Ry', 'Rz', 'Ru', 'Rv', 'Rw'])

rigid.add_rigid_body_fixed_constraint('top_cube_constraints',
                                      top_cube_material_id,
                                      ['Rx', 'Ry', 'Ru', 'Rv', 'Rw'])

# add a z load to bring the top cylinder into contact with the layer
load_parameters = rigid.get_rigid_body_prescribed_force_default_parameters()
# load_parameters = rigid.get_rigid_body_prescribed_motion_default_parameters()
load_parameters['rb'] = str(top_cube_material_id)
load_parameters['dof'] = 'Rz'
top_cube_load_z_id = rigid.add_rigid_body_prescribed_constraint(
    'top_cube_prescribed_force_z',
    load_parameters)

top_cube_load_z_vec = np.round(np.linspace(0.0, -20, num=len(must_points)), 3)

loadcurves.add_loadcurve(top_cube_load_z_id,
                         'linear', 'constant',
                         must_points,
                         top_cube_load_z_vec)

################################################################################
# Export Model
################################################################################
model.name = 'febio_example_1'
model.export('./models/example_1', model.name)

################################################################################
# visualize
################################################################################
if visualize_mesh:
    model.visualize([[top_cube_nodes, top_cube.cells_dict, 'triangle',
                      'top_cube'],
                     [bottom_cube_nodes[0], bottom_cube.cells_dict,
                      'triangle', 'bottom_cube'],
                     [bottom_layer_nodes[0], cube_hex_mesh.cells_dict,
                      'hexahedron', 'bottom_layer'],
                     [top_layer_nodes[0], cube_hex_mesh.cells_dict,
                      'hexahedron', 'top_layer']
                     ])

################################################################################
# execute
################################################################################
if execute_model:
    model.execute('{}.feb'.format(model.name), './models/example_1')
