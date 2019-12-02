import os
import numpy as np
import trimesh
import argparse

parser = argparse.ArgumentParser(description="Transform a mesh with an affine transform")
parser.add_argument("-f", required=True, nargs="+", dest="meshfiles", help="Input mesh files")
parser.add_argument("-o", required=True, dest="output", help="Output file (if single file output) or folder (if multiple files as input)")
parser.add_argument("-round", required=False, dest="round", help="Number of decimal to round the vertices positions (default: no rounding)")
parser.add_argument("-pivot", required=False, dest="pivot", help="Defines the pivot for scaling and rotation. Should contain 3 elements (x, y and z), comma separated. Example -pivot 12,1,0 (default: 0,0,0)")
parser.add_argument("-translation", required=False, dest="translation", help="Translates the mesh. Should contain 3 elements (x, y and z), comma separated. Example -translation 0,12,13.5 (default: 0,0,0)")
parser.add_argument("-scale", required=False, dest="scale", help="Rescales the mesh, should contain 1 or 3 elements (global, or x, y and z), comma separated. Example -scale 2 OR -scale 1.2,1.8,2.5 (default: 1)")
parser.add_argument("-rotation", required=False, dest="rotation", help="Rotates the mesh, should contain 4 elements (angle in radians, direction x, y and z. The direction is from the pivot point), comma separated. Example -rotation 3.1415,0,1,0 (default: 1)")
args = vars(parser.parse_args())

round = False
if args["round"] is not None:
    round = int(args["round"])

# default pivot point
pivot = [0., 0., 0.]

# default scale
scale = 1.

# default rotation angle
angle = 0.

# default rotation axis
axis = [1., 0., 0]

# default translation
translation = [0., 0., 0.]

# getting pivot point from arguments
if args["pivot"]:
    try:
        tmp_pivot = list(map( lambda n: float(n), args["pivot"].split(",")))
        if len(tmp_pivot) == 3:
            pivot = tmp_pivot
        else:
            raise ValueError("The pivot is a 3D point and should contain 3 comma-saparated elements.")
    except Exception as e:
        print(e)
        exit(1)

# getting scale from arguments
if args["scale"]:
    try:
        tmp_scale = list(map( lambda n: float(n), args["scale"].split(",")))
        if len(tmp_scale) == 1:
            tmp_scale = tmp_scale[0]
            scale = tmp_scale
        elif len(tmp_scale) == 3:
            raise ValueError("Scaling with 3 values is not implemented yet.")
            scale = tmp_scale
        else:
            raise ValueError("The scale must be made of 3 comma-saparated elements (x,y,z) or of a single element to apply to the 3 dimensions.")
    except Exception as e:
        print(e)
        exit(1)

# getting translation from arguments
if args["translation"]:
    try:
        tmp_translation = list(map( lambda n: float(n), args["translation"].split(",")))
        if len(tmp_translation) == 3:
            translation = tmp_translation
        else:
            raise ValueError("The translation must be made of 3 comma-saparated elements (x,y,z).")
    except Exception as e:
        print(e)
        exit(1)

# getting rotation from arguments
if args["rotation"]:
    try:
        tmp_rotation = list(map( lambda n: float(n), args["rotation"].split(",")))
        if len(tmp_rotation) == 4:
            angle = tmp_rotation[0]
            axis = [tmp_rotation[1], tmp_rotation[2], tmp_rotation[3]]
        else:
            raise ValueError("The rotation must be made of 4 comma-saparated elements (angle,xaxis,yaxis,zaxis).")
    except Exception as e:
        print(e)
        exit(1)

print("pivot point", pivot)
print("scale", scale)
print("translation", translation)
print("angle", angle)
print("rotation axis", axis)

m_scale = trimesh.transformations.scale_matrix(scale, pivot)
m_translation = trimesh.transformations.translation_matrix(translation)
m_rotation = trimesh.transformations.rotation_matrix(angle, axis, pivot)
m_transform = trimesh.transformations.concatenate_matrices(m_translation, m_rotation, m_scale)

print("Homogeneous matrix", m_transform)



def processMesh(meshfile):
    # mesh_data = pywavefront.Wavefront(meshfile)
    mesh_data = trimesh.load(meshfile)
    mesh_data.apply_transform(m_transform)

    if round:
        mesh_data.vertices = np.around(mesh_data.vertices, decimals=round)

    # print(mesh_data.vertices)
    # # print(mesh_data.facets)
    return mesh_data



if __name__ == "__main__":
    input_files = args["meshfiles"]
    output_location = args["output"]

    output_is_existing_folder = os.path.isdir(output_location)
    more_than_one_file = len(input_files) > 1

    if (not output_is_existing_folder) and len(input_files) > 1:
        print("The output path is expected to be an existing directory when more than 1 files are input")
        exit(1)



    # objparser.parse('fghjk')
    for meshfile in input_files:
        mesh = processMesh(meshfile)
        save_path = os.path.join(output_location, os.path.basename(meshfile)) if output_is_existing_folder else output_location
        mesh.export(save_path)
