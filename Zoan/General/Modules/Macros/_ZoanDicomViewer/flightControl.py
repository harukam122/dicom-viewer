import numpy as np
import math
from Inventor.base import SbVec3d, SbRotationd

def radians(deg):
    return deg * math.pi / 180.0

class FlightControl:

    def __init__(self):
        self._imageData          = None
        self._imageExtent        = None
        self._worldToVoxelMatrix = None

    def updateImage(self):
        image = ctx.field("inImage").image()
        if image:
            # store values for collision detection:
            self._imageExtent = image.imageExtent()
            self._imageData = image.getTile((0,0,0,0,0,0), self._imageExtent).squeeze()
            self._worldToVoxelMatrix = image.worldToVoxelMatrixInventor()
    
    def forward(self):
        self._move(SbVec3d(0, 0, -self._moveSpeed()))

    def backward(self):
        self._move(SbVec3d(0, 0, self._moveSpeed()))

    def left(self):
        self._move(SbVec3d(-self._moveSpeed(), 0, 0))

    def right(self):
        self._move(SbVec3d(self._moveSpeed(), 0, 0))

    def down(self):
        self._move(SbVec3d(0, -self._moveSpeed(), 0))

    def up(self):
        self._move(SbVec3d(0, self._moveSpeed(), 0))

    def rotateX(self, angle):
        self._rotate(SbRotationd(SbVec3d(0,1,0), radians(angle) * self._turnSpeed()))

    def rotateY(self, angle):
        self._rotate(SbRotationd(SbVec3d(1,0,0), radians(angle) * self._turnSpeed()))

    def rotateZ(self, angle):
        self._rotate(SbRotationd(SbVec3d(0,0,1), radians(angle) * self._turnSpeed()))

    def viewAll(self):
        ctx.field("SoCameraViewAll.viewAll").touch()
        # viewAll will set nearDistance and farDistance to the minimum required values,
        # adapt these values, so that moving around will not trigger clipping too early:
        def adaptClipping():
            ctx.field("SoPerspectiveCamera.nearDistance").value = 1
            ctx.field("SoPerspectiveCamera.farDistance").value = 10000
        ctx.callLater(0.0, adaptClipping)

    def _orientation(self):
        return ctx.field("SoPerspectiveCamera.orientation").inventorValue()

    def _move(self, relOffset):
        absOffset = self._orientation().transformPoint(relOffset)
        newPos = ctx.field("SoPerspectiveCamera.position").inventorValue() + absOffset
        currRot = ctx.field("SoPerspectiveCamera.orientation").inventorValue()
        if self._canMoveTo(newPos, currRot):
            ctx.field("SoPerspectiveCamera.position").setValue(newPos)

    def _rotate(self, rotation):
        newRot = rotation * self._orientation()
        currPos = ctx.field("SoPerspectiveCamera.position").inventorValue()
        if self._canMoveTo(currPos, newRot):
            ctx.field("SoPerspectiveCamera.orientation").setValue(newRot)

    def _canMoveTo(self, newPos, newRot):
        for value in self._nextCylinderPos(newPos, newRot):
            n = self._worldToVoxelMatrix.transformPoint(value)
            if self._isInImage(n):
                voxelValue = self._imageData[int(n[2])][int(n[1])][int(n[0])]
                if voxelValue == 1:
                    return False
        return True
      
    def _nextCylinderPos(self, newPos, newRot):
        angleSteps = 10
        heightSteps = 50
        cylHeight = 120
        for i in range(angleSteps):
          angle = math.pi*2*(i/angleSteps)
          for j in range(heightSteps):
            height = cylHeight*j/heightSteps
            point = SbVec3d(math.cos(angle), math.sin(angle), height)
            point = newRot.transformPoint(point)
            point += newPos
            yield point

    def _isInImage(self, position):
        return position[0] >= 0 and \
               position[1] >= 0 and \
               position[2] >= 0 and \
               position[0] < self._imageExtent[0] and \
               position[1] < self._imageExtent[1] and \
               position[2] < self._imageExtent[2]

    def _moveSpeed(self):
        return ctx.field("moveSpeed").value

    def _turnSpeed(self):
        return ctx.field("turnSpeed").value
      
    def incline(self, child):
        ctx.field("SoSwitch.whichChild").value = child

__object__ = FlightControl()
gFlightControl = __object__

lastOffsetX = ctx.field("GenericPointingAction.offsetX").value
lastOffsetY = ctx.field("GenericPointingAction.offsetY").value

def init():
    gFlightControl.viewAll()

def onKeyPressed():
    key = ctx.field("SoKeyGrabber.lastKey").value
    if key == "W":
        gFlightControl.forward()
    elif key == "S":
        gFlightControl.backward()
    elif key == "A":
        gFlightControl.left()
    elif key == "D":
        gFlightControl.right()
    elif key == "SPACE":
        gFlightControl.down()
    elif key == "C":
        gFlightControl.up()
    elif key == "LEFT_ARROW":
        gFlightControl.rotateX(5)
    elif key == "RIGHT_ARROW":
        gFlightControl.rotateX(-5)
    elif key == "UP_ARROW":
        gFlightControl.rotateY(5)
    elif key == "DOWN_ARROW":
        gFlightControl.rotateY(-5)
    elif key == "COMMA":
        gFlightControl.rotateZ(-5)
    elif key == "PERIOD":
        gFlightControl.rotateZ(5)
    elif key == "V":
        gFlightControl.viewAll()
    elif key == "NUMBER_1":
        gFlightControl.incline(0)
    elif key == "NUMBER_2":
        gFlightControl.incline(1)
    elif key == "NUMBER_3":
        gFlightControl.incline(2)

def onHeadNod(field):
    if imageExists():
      global lastOffsetX
      oldOffsetX = lastOffsetX
      lastOffsetX = field.value
      deltaX =  lastOffsetX - oldOffsetX
      if deltaX:
          gFlightControl.rotateY(deltaX)

def onHeadTurn(field):
    if imageExists():
      global lastOffsetY
      oldOffsetY = lastOffsetY
      lastOffsetY = field.value
      deltaY =  lastOffsetY - oldOffsetY
      if deltaY:
          gFlightControl.rotateX(-deltaY)

def onUpdateImage():
    gFlightControl.updateImage()

def imageExists():
    image = ctx.field("inImage").image()
    if image:
      return True
    else:
      return False