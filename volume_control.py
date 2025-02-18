import cv2
import mediapipe as mp
import math
import subprocess

# initialize mediapipe hands
mp_hands = mp.solutions.hands

# open a connection to the webcam
cap = cv2.VideoCapture(0)

# initial volume, previous angle, and accumulated rotation
volume = 50  # in percent (0 to 100)
prev_angle = None
accumulated_angle = 0

# set the initial system volume using osascript
subprocess.run(["osascript", "-e", f"set volume output volume {volume}"])

with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # flip the frame for a mirror view
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # convert the frame to rgb
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # process the first detected hand (works for both left and right)
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]

            # get landmarks for the index finger tip (8) and base (mcp, 5)
            tip = hand_landmarks.landmark[8]
            mcp = hand_landmarks.landmark[5]
            tip_x, tip_y = int(tip.x * w), int(tip.y * h)
            mcp_x, mcp_y = int(mcp.x * w), int(mcp.y * h)

            # calculate the angle (in degrees) from mcp to tip
            dx = tip_x - mcp_x
            dy = tip_y - mcp_y
            angle = math.degrees(math.atan2(dy, dx))

            # initialize previous angle when first detected
            if prev_angle is None:
                prev_angle = angle
            else:
                # calculate the change in angle between frames
                angle_diff = angle - prev_angle

                # normalize the angle difference to the range [-180, 180]
                if angle_diff > 180:
                    angle_diff -= 360
                elif angle_diff < -180:
                    angle_diff += 360

                accumulated_angle += angle_diff

                # check if a full circle (360°) has been completed
                if abs(accumulated_angle) >= 360:
                    if accumulated_angle > 0:
                        volume += 10  # clockwise rotation increases volume
                    else:
                        volume -= 10  # anticlockwise rotation decreases volume

                    # clamp volume between 0 and 100
                    volume = max(0, min(100, volume))

                    # update system volume using osascript
                    subprocess.run(["osascript", "-e", f"set volume output volume {volume}"])

                    # remove one full circle from the accumulated angle
                    if accumulated_angle > 0:
                        accumulated_angle -= 360
                    else:
                        accumulated_angle += 360

                # update previous angle for the next iteration
                prev_angle = angle

            # draw a white dot at the index finger tip
            cv2.circle(frame, (tip_x, tip_y), 10, (255, 255, 255), -1)
        else:
            # if no hand is detected, reset the previous angle
            prev_angle = None

        # display the current volume percentage
        cv2.putText(frame, f'Volume: {volume}%', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow("Volume Control", frame)
        if cv2.waitKey(5) & 0xFF == 27:  # press esc to exit
            break

cap.release()
cv2.destroyAllWindows()
