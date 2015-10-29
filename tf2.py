################################################################################
# Copyright (C) 2012-2013 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################
import os, sys, thread, time, inspect
import struct, fcntl, termios, readline
from subprocess import Popen, PIPE
from pymouse import PyMouse

sys.path.insert(0, "lib/")

import Leap
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture


thresholds = {"pitch": 15, "roll": 15}
mouseMovement = 10

class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']
    lastPrint = 0;

    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        for i in range(0, self.lastPrint):
            deleteLine()

        self.lastPrint = 0

        if len(frame.hands) is 0:
            keyUp('w')
            keyUp('a')
            keyUp('s')
            keyUp('d')

        for hand in frame.hands:
            self.lastPrint += 1
            normal = hand.palm_normal
            direction = hand.direction
            pitch = direction.pitch * Leap.RAD_TO_DEG
            roll = normal.roll * Leap.RAD_TO_DEG
            handType = "\033[31mLeft\033[0m " if hand.is_left else "\033[32mRight\033[0m"

            if hand.palm_velocity.y > 500:
                keyDown('space')
                keyUp('space')

            x = hand.palm_position[0]
            y = hand.palm_position[1]
            z = hand.palm_position[2]

            print "%s - x: %3f | y: %3f | z: %3f | pitch: %3f | roll: %3f | v: %s" % (handType, x, y, z, pitch, roll, hand.palm_velocity)

            #looking
            if hand.is_right:
                m = PyMouse()
                mouseX, mouseY = m.position()
                deltaX = abs(int(roll)) - thresholds["roll"]
                deltaY = abs(int(pitch)) - thresholds["pitch"]


                if hand.grab_strength > .95:
                    m.click(mouseX, mouseY, 1)

                #look left
                if roll > thresholds["roll"]:
                    mouseX -= deltaX

                #look right
                if roll < -1 * thresholds["roll"]:
                    mouseX += deltaX

                #look down
                if pitch > thresholds["pitch"]:
                    mouseY -= deltaY

                #look up
                if pitch < -1 * thresholds["pitch"]:
                    mouseY += deltaY

                m.move(mouseX, mouseY)
            else:
                if hand.grab_strength > .95:
                    keyDown('p')
                    keyUp('p')

                if roll > thresholds["roll"]:
                    keyDown('a')
                else:
                    keyUp('a')

                if roll < -1 * thresholds["roll"]:
                    keyDown('d')
                else:
                    keyUp('d')

                if pitch > thresholds["pitch"]:
                    keyDown('s')
                else:
                    keyUp('s')

                if pitch < -1 * thresholds["pitch"]:
                    keyDown('w')
                else:
                    keyUp('w')


        def state_string(self, state):
            if state == Leap.Gesture.STATE_START:
                return "STATE_START"

            if state == Leap.Gesture.STATE_UPDATE:
                return "STATE_UPDATE"

            if state == Leap.Gesture.STATE_STOP:
                return "STATE_STOP"

            if state == Leap.Gesture.STATE_INVALID:
                return "STATE_INVALID"



def keyDown(key):
    sequence = "keydown %s\n" % (key)
    p = Popen(['xte'], stdin = PIPE)
    p.communicate(input = sequence)

def keyUp(key):
    sequence = "keyup %s\n" % (key)
    p = Popen(['xte'], stdin = PIPE)
    p.communicate(input = sequence)



def deleteLine():
	# Next line said to be reasonably portable for various Unixes
	(rows,cols) = struct.unpack('hh', fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ,'1234'))

	text_len = len(readline.get_line_buffer())+2

	# ANSI escape sequences (All VT100 except ESC[0G)
	sys.stdout.write('\x1b[1A')                         # Move cursor up
	sys.stdout.write('\x1b[0G')                         # Move to start of line
	sys.stdout.write('\x1b[2K')                         # Clear current line

def main():
    print "\n\n\n\n\n\n"
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()
