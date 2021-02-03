# fSpy USD converter
# Copyright (C) 2018 - Ben Skinner
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math
from . import fspy
from pxr import Usd, UsdGeom, Tf, Gf, Sdf

def convert(filepath, output, scope_name = "/Cameras/test", aperture_width = 36):
    try:
        # Get fSpy data
        project = fspy.Project(filepath)
        camera_parameters = project.camera_parameters

        # Setup USD scene

        stage = Usd.Stage.CreateInMemory()

        # Setup camera scope

        cameras_scope = Sdf.Path(scope_name)

        for prim in cameras_scope.GetAncestorsRange():
            xform = UsdGeom.Xform.Define(stage, prim)

        camera = UsdGeom.Camera.Define(stage, cameras_scope.AppendChild( Tf.MakeValidIdentifier(project.file_name) ))

        # - Transform
        matrix = Gf.Matrix4d(camera_parameters.camera_transform).GetTranspose()
        rotMat = Gf.Matrix4d(1.0).SetRotate(Gf.Rotation(Gf.Vec3d(1, 0, 0), -90.0))
        matrix = matrix * rotMat
        camera.AddTransformOp().Set(matrix)

        # - Apperture Size

        hfov = math.degrees(camera_parameters.fov_horiz)
        hfov = math.degrees(camera_parameters.fov_verti)

        width = camera_parameters.image_width
        height = camera_parameters.image_height
    
        aspectRatio = width/height
        iaspectRatio = height/width

        # TODO: We likely need to get this from somewhere
        apWidth = aperture_width
        apHeight = apWidth * iaspectRatio

        camera.CreateHorizontalApertureAttr().Set(apWidth)
        camera.CreateVerticalApertureAttr().Set(apHeight)

        # - Focal Length
        focalLength = (0.5*apHeight)/math.tan((0.5*hfov)/57.296)

        camera.CreateFocalLengthAttr().Set(focalLength)

        print(stage.ExportToString())
        stage.Export(output)
    except Exception as e:
        print("Couldnt convert: " + str(e))
        pass
