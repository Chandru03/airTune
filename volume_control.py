import cv2
import mediapipe as mp
import math
import subprocess

# Initialize MediaPipe Hands.
mp_hands = mp.solutions.hands

# Open a connection to the webcam.
cap = cv2.VideoCapture(0)

# Initial volume, previous angle, and accumulated rotation.
volume = 50  # in percent (0 to 100)
prev_angle = None
accumulated_angle = 0

# Set the initial system volume using osascript.
subprocess.run(["osascript", "-e", f"set volume output volume {volume}"])

with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame for a mirror view.
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # Convert the frame to RGB.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # Process the first detected hand (works for both left and right).
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]

            # Get landmarks for the index finger tip (8) and base (MCP, 5).
            tip = hand_landmarks.landmark[8]
            mcp = hand_landmarks.landmark[5]
            tip_x, tip_y = int(tip.x * w), int(tip.y * h)
            mcp_x, mcp_y = int(mcp.x * w), int(mcp.y * h)

            # Calculate the angle (in degrees) from MCP to tip.
            dx = tip_x - mcp_x
            dy = tip_y - mcp_y
            angle = math.degrees(math.atan2(dy, dx))

            # Initialize previous angle when first detected.
            if prev_angle is None:
                prev_angle = angle
            else:
                # Calculate the change in angle between frames.
                angle_diff = angle - prev_angle

                # Normalize the angle difference to the range [-180, 180].
                if angle_diff > 180:
                    angle_diff -= 360
                elif angle_diff < -180:
                    angle_diff += 360

                accumulated_angle += angle_diff

                # Check if a full circle (360°) has been completed.
                if abs(accumulated_angle) >= 360:
                    if accumulated_angle > 0:
                        volume += 10  # Clockwise rotation increases volume.
                    else:
                        volume -= 10  # Anticlockwise rotation decreases volume.

                    # Clamp volume between 0 and 100.
                    volume = max(0, min(100, volume))

                    # Update system volume using osascript.
                    subprocess.run(["osascript", "-e", f"set volume output volume {volume}"])

                    # Remove one full circle from the accumulated angle.
                    if accumulated_angle > 0:
                        accumulated_angle -= 360
                    else:
                        accumulated_angle += 360

                # Update previous angle for the next iteration.
                prev_angle = angle

            # Draw a white dot at the index finger tip.
            cv2.circle(frame, (tip_x, tip_y), 10, (255, 255, 255), -1)
        else:
            # If no hand is detected, reset the previous angle.
            prev_angle = None

        # Display the current volume percentage.
        cv2.putText(frame, f'Volume: {volume}%', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow("Volume Control", frame)
        if cv2.waitKey(5) & 0xFF == 27:  # Press Esc to exit.
            break

cap.release()
cv2.destroyAllWindows()
