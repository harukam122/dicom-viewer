# ----------------------------------------------------------------------------

# 
#  \file    DicomViewerMacro.py
#  \author  Haruka Masamura
#  \date    2022-06-22
#
#  Builds a 3D Dicom Viewer

# ----------------------------------------------------------------------------

from mevis import *

# clears data upon opening application
def init():
  clearData()
        
# button action for loading data
def loadData():
  ctx.field("DirectDicomImport.dplImport").touch()
  ctx.field("GVRVolumeSave.save").touch()
  ctx.field("GVRVolumeLoad.filename").value = ctx.field("GVRVolumeSave.filename").value
  initPosition()

# reorients the camera to initial position/orientation
def initPosition():
  ctx.field("flightControl.position").value = [-1., -240., -200.]
  ctx.field("flightControl.orientation").value = (-1., 0., 0., 4.5)

# button action for clearing DICOM volume data
def clearData():
  ctx.field("LocalPath.localName").value = ""
  ctx.field("DirectDicomImport.dplImport").touch()
  ctx.field("GVRVolumeLoad.filename").value = ""
  
# called whenever the collisionThreshold field is updated
def collisionThresholdCommand(field):
  '''
  :type field: MLABField
  '''
  ctx.field("collisionThreshold.threshold").value = field.doubleValue()

# called whenever the cameraAngle field is updated
def cameraAngleCommand(field):
  '''
  :type field: MLABField
  '''
  if field.value == "degree0":
    ctx.field("flightControl.cameraAngle").value = 0
  if field.value == "degree30":
    ctx.field("flightControl.cameraAngle").value = 1
  if field.value == "degree70":
    ctx.field("flightControl.cameraAngle").value = 2
