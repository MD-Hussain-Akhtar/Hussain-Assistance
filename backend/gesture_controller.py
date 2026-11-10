import mediapipe as mp
import cv2
import numpy as np
from mouse_controller import MouseController
from screen_capture import ScreenCapture

class GestureController:
    def __init__(self):
        self.mouse = MouseController()
        self.capture = ScreenCapture()
        
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Gesture detection state
        self.last_gesture = None
        self.pinch_threshold = 0.05
        self.gesture_history = []
        
    def detect_gesture(self, frame=None):
        """Detect hand gesture from frame"""
        try:
            if frame is None:
                # Capture from screen
                pil_img = self.capture.capture_screen()
                if not pil_img:
                    return None
                frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(frame_rgb)
            
            if results.multi_hand_landmarks and results.multi_handedness:
                landmarks = results.multi_hand_landmarks[0]
                handedness = results.multi_handedness[0].classification[0].label
                
                gesture = self._classify_gesture(landmarks)
                return {
                    'gesture': gesture,
                    'landmarks': landmarks,
                    'handedness': handedness,
                    'confidence': results.multi_handedness[0].classification[0].score
                }
            
            return None
        except Exception as e:
            print(f"Error detecting gesture: {e}")
            return None
    
    def _classify_gesture(self, landmarks):
        """Classify hand gesture from landmarks"""
        try:
            # Get hand coordinates
            lm = landmarks.landmark
            h, w, c = 480, 640, 3  # Default dimensions
            
            # Key points
            thumb_tip = lm[4]
            index_tip = lm[8]
            middle_tip = lm[12]
            ring_tip = lm[16]
            pinky_tip = lm[20]
            palm_center = lm[0]
            
            # Calculate distances
            thumb_index_dist = self._distance(thumb_tip, index_tip)
            index_middle_dist = self._distance(index_tip, middle_tip)
            all_fingers_open = all(
                tip.y < lm[0].y 
                for tip in [index_tip, middle_tip, ring_tip, pinky_tip]
            )
            
            # Gestures
            if thumb_index_dist < self.pinch_threshold:
                if middle_tip.y < lm[0].y and ring_tip.y < lm[0].y:
                    return 'PINCH'  # Click
            
            # Fist
            if thumb_index_dist > 0.1 and not all_fingers_open:
                return 'FIST'  # Drag
            
            # Open hand
            if all_fingers_open:
                return 'OPEN'  # Neutral
            
            # Two fingers (scroll)
            if index_tip.y < lm[0].y and middle_tip.y < lm[0].y:
                if index_middle_dist < 0.08:
                    return 'TWO_FINGERS'  # Scroll
            
            return 'NEUTRAL'
        except:
            return 'NEUTRAL'
    
    def _distance(self, point1, point2):
        """Calculate distance between two landmarks"""
        return np.sqrt(
            (point1.x - point2.x) ** 2 + 
            (point1.y - point2.y) ** 2
        )
    
    def handle_gesture(self, gesture_data):
        """Handle detected gesture with mouse control"""
        if not gesture_data:
            return None
        
        gesture = gesture_data['gesture']
        landmarks = gesture_data['landmarks']
        lm = landmarks.landmark
        
        # Get screen dimensions
        screen_width, screen_height = self.capture.get_all_monitors()[0]['width'], self.capture.get_all_monitors()[0]['height']
        
        # Index finger position as cursor
        cursor_x = int(lm[8].x * screen_width)
        cursor_y = int(lm[8].y * screen_height)
        
        if gesture == 'PINCH':
            # Click
            return self.mouse.click(cursor_x, cursor_y)
        elif gesture == 'FIST':
            # Start drag
            self.mouse.move_mouse(cursor_x, cursor_y, duration=0.1)
            return {'action': 'drag_start', 'x': cursor_x, 'y': cursor_y}
        elif gesture == 'TWO_FINGERS':
            # Scroll
            return self.mouse.scroll(5)
        else:
            # Move cursor
            return self.mouse.move_mouse(cursor_x, cursor_y, duration=0.1)
    
    def gesture_control_loop(self, duration=None, callback=None):
        """Continuous gesture control"""
        import time
        start_time = time.time()
        
        try:
            cap = cv2.VideoCapture(0)
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                gesture_data = self.detect_gesture(frame)
                result = self.handle_gesture(gesture_data)
                
                if callback and result:
                    callback(result)
                
                if cv2.waitKey(5) & 0xFF == ord('q'):
                    break
                
                if duration and (time.time() - start_time) > duration:
                    break
            
            cap.release()
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"Error in gesture control loop: {e}")
    
    def draw_landmarks(self, frame, landmarks):
        """Draw hand landmarks on frame"""
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(frame_rgb)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        frame, 
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS
                    )
            
            return frame
        except Exception as e:
            print(f"Error drawing landmarks: {e}")
            return frame
    
    def get_gesture_history(self, limit=10):
        """Get recent gesture history"""
        return self.gesture_history[-limit:]
