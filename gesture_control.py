import cv2
import mediapipe as mp
from pynput.keyboard import Controller
import threading
import time

# Initialize MediaPipe Hand Detection
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Initialize Keyboard Controller
keyboard = Controller()

# Mapping gestures to game controls
gesture_controls = {
    "LEFT": "d",        # Steer Left
    "RIGHT": "a",       # Steer Right
    "BOOST": "shift",   # Nitro Boost
    "BRAKE": "space"    # Brake/Drift
}

cooldown_time = 0.3  # Time delay to prevent rapid key presses
last_action_time = {}
is_running = False  # Track if the process is active

# Function to detect gestures
def detect_gesture(landmarks):
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    palm_base = landmarks[0]  # Base of the hand

    # Measure finger spread (distance between index & pinky)
    finger_spread = abs(index_tip.x - pinky_tip.x)

    # 🚀 BOOST (All fingers extended & spread out)
    if (index_tip.y < middle_tip.y and middle_tip.y < ring_tip.y and ring_tip.y < pinky_tip.y) and finger_spread > 0.1:
        return "BOOST"

    # 🛑 BRAKE (Thumbs Down Gesture)
    if (thumb_tip.y > index_tip.y + 0.05 and 
        thumb_tip.y > middle_tip.y + 0.05 and 
        thumb_tip.y > palm_base.y + 0.05):
        return "BRAKE"

    # ⬅️ LEFT (Hand tilted left)
    if thumb_tip.x > index_tip.x and index_tip.x > middle_tip.x:
        return "LEFT"

    # ➡️ RIGHT (Hand tilted right)
    if thumb_tip.x < index_tip.x and index_tip.x < middle_tip.x:
        return "RIGHT"

    return None  # No gesture detected

# Function to run gesture recognition
def run_gesture_control():
    global is_running
    is_running = True
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not access the webcam.")
        is_running = False
        return

    while is_running:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # Flip frame horizontally
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                detected_gesture = detect_gesture(hand_landmarks.landmark)

                if detected_gesture:
                    current_time = time.time()
                    if detected_gesture not in last_action_time or (current_time - last_action_time[detected_gesture] > cooldown_time):
                        keyboard.press(gesture_controls[detected_gesture])
                        keyboard.release(gesture_controls[detected_gesture])
                        print(f"Performed Action: {detected_gesture}")
                        last_action_time[detected_gesture] = current_time

        cv2.imshow("Gesture Control", frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    is_running = False

# Function to stop gesture recognition
def stop_gesture_control():
    global is_running
    is_running = False
