"""
2048 Gesture Game (MediaPipe Edition)
======================================
OpenCV-based 2048 game controlled by hand gestures via camera.
Uses MediaPipe Hands for robust hand tracking (21 landmarks).

Controls:
  - Swipe hand in camera view to move tiles (index fingertip trail)
  - ESC to quit
  - R to reset
"""

import random
import cv2
import numpy as np
import mediapipe as mp


# ====================================================================
# Game Engine
# ====================================================================

class Game2048:
    """Core 2048 game engine."""

    def __init__(self):
        self.size = 4
        self.board = [[0] * self.size for _ in range(self.size)]
        self.score = 0
        self.moved = False
        self._add_random_tile()
        self._add_random_tile()

    def _add_random_tile(self):
        empty = [(r, c) for r in range(self.size)
                 for c in range(self.size) if self.board[r][c] == 0]
        if not empty:
            return
        r, c = random.choice(empty)
        self.board[r][c] = 2 if random.random() < 0.9 else 4

    def _compress(self, row):
        new_row = [v for v in row if v != 0]
        new_row += [0] * (self.size - len(new_row))
        return new_row

    def _merge(self, row):
        new_row = []
        i = 0
        while i < self.size:
            if row[i] == 0:
                i += 1
                continue
            if i + 1 < self.size and row[i] == row[i + 1]:
                val = row[i] * 2
                new_row.append(val)
                self.score += val
                i += 2
            else:
                new_row.append(row[i])
                i += 1
        new_row += [0] * (self.size - len(new_row))
        return new_row

    def _transpose(self):
        self.board = [[self.board[r][c]
                       for r in range(self.size)] for c in range(self.size)]

    def _reverse_rows(self):
        self.board = [row[::-1] for row in self.board]

    def move(self, direction):
        old_board = [row[:] for row in self.board]

        if direction == 'left':
            for i in range(self.size):
                self.board[i] = self._compress(self.board[i])
                self.board[i] = self._merge(self.board[i])
        elif direction == 'right':
            for i in range(self.size):
                self.board[i] = self._compress(self.board[i][::-1])
                self.board[i] = self._merge(self.board[i])[::-1]
        elif direction == 'up':
            self._transpose()
            for i in range(self.size):
                self.board[i] = self._compress(self.board[i])
                self.board[i] = self._merge(self.board[i])
            self._transpose()
        elif direction == 'down':
            self._transpose()
            for i in range(self.size):
                self.board[i] = self._compress(self.board[i][::-1])
                self.board[i] = self._merge(self.board[i])[::-1]
            self._transpose()

        self.moved = (self.board != old_board)
        if self.moved:
            self._add_random_tile()

    def is_game_over(self):
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == 0:
                    return False
                if c + 1 < self.size and self.board[r][c] == self.board[r][c + 1]:
                    return False
                if r + 1 < self.size and self.board[r][c] == self.board[r + 1][c]:
                    return False
        return True

    def has_won(self):
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == 2048:
                    return True
        return False

    def reset(self):
        self.__init__()

    def get_board(self):
        return [row[:] for row in self.board]


# ====================================================================
# Rendering
# ====================================================================

TILE_COLORS = {
    0:    (205, 193, 180),
    2:    (238, 228, 218),
    4:    (237, 224, 200),
    8:    (242, 177, 121),
    16:   (245, 149, 99),
    32:   (246, 124, 95),
    64:   (246, 94, 59),
    128:  (237, 207, 114),
    256:  (237, 204, 97),
    512:  (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}

TILE_TEXT_COLOR = {
    0:  (205, 193, 180),
    2:  (119, 110, 101),
    4:  (119, 110, 101),
    8:  (249, 246, 242),
    16: (249, 246, 242),
    32: (249, 246, 242),
    64: (249, 246, 242),
    128: (249, 246, 242),
    256: (249, 246, 242),
    512: (249, 246, 242),
    1024: (249, 246, 242),
    2048: (249, 246, 242),
}

CELL_SIZE = 100
GAP = 8
BOARD_PADDING = 10
BOARD_SIZE = CELL_SIZE * 4 + GAP * 5


def draw_board(game, img_size=(600, 700)):
    """Render the 2048 game board as an OpenCV image."""
    board_img = np.zeros((img_size[1], img_size[0], 3), dtype=np.uint8)
    board_img[:] = (187, 173, 160)

    # Title
    cv2.putText(board_img, "2048", (20, 60),
                cv2.FONT_HERSHEY_DUPLEX, 2.0, (119, 110, 101), 2)
    cv2.putText(board_img, "MediaPipe Gesture",
                (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (119, 110, 101), 1)

    # Score
    score_text = "SCORE: {}".format(game.score)
    (tw, _), _ = cv2.getTextSize(score_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
    cv2.putText(board_img, score_text,
                (img_size[0] - tw - 10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (119, 110, 101), 2)
    cv2.putText(board_img, "R=Reset  ESC=Quit",
                (img_size[0] - 200, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (119, 110, 101), 1)

    # Board offset
    board_x = (img_size[0] - BOARD_SIZE) // 2
    board_y = 100

    # Draw tiles
    for r in range(4):
        for c in range(4):
            x = board_x + c * (CELL_SIZE + GAP) + GAP
            y = board_y + r * (CELL_SIZE + GAP) + GAP
            val = game.board[r][c]
            color = TILE_COLORS.get(val, (60, 58, 50))
            cv2.rectangle(board_img, (x, y), (x + CELL_SIZE, y + CELL_SIZE),
                          color, -1)

            if val != 0:
                text = str(val)
                font_scale = 1.5 if val < 100 else 1.2 if val < 1000 else 0.9
                text_color = TILE_TEXT_COLOR.get(val, (255, 255, 255))
                (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX,
                                              font_scale, 2)
                tx = x + (CELL_SIZE - tw) // 2
                ty = y + (CELL_SIZE + th) // 2
                cv2.putText(board_img, text, (tx, ty),
                            cv2.FONT_HERSHEY_DUPLEX, font_scale, text_color, 2)

    # Game over overlay
    if game.is_game_over():
        overlay = board_img.copy()
        cv2.rectangle(overlay, (board_x, board_y),
                      (board_x + BOARD_SIZE, board_y + BOARD_SIZE),
                      (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, board_img, 0.5, 0, board_img)
        text = "GAME OVER"
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 1.5, 3)
        cv2.putText(board_img, text,
                    ((img_size[0] - tw) // 2, img_size[1] // 2),
                    cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 3)

    return board_img


# ====================================================================
# Hand Detection (MediaPipe)
# ====================================================================

class HandDetector:
    """Wrapper for MediaPipe Hands detection."""

    def __init__(self, max_hands=1, detection_confidence=0.7, tracking_confidence=0.5):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self.fingertip = None       # (x, y) of index finger tip
        self.landmarks = None       # raw landmarks list
        self.hand_rect = None       # (x1, y1, x2, y2) bounding box
        self.detected = False

    def process(self, frame):
        """
        Process a BGR frame.
        Updates self.fingertip, self.detected, etc.
        """
        self.fingertip = None
        self.landmarks = None
        self.hand_rect = None
        self.detected = False

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        if not results.multi_hand_landmarks:
            return

        hand_landmarks = results.multi_hand_landmarks[0]
        self.landmarks = hand_landmarks
        self.detected = True

        h, w, _ = frame.shape

        # Index finger tip (landmark 8)
        tip = hand_landmarks.landmark[8]
        self.fingertip = (int(tip.x * w), int(tip.y * h))

        # Bounding box
        xs = [lm.x for lm in hand_landmarks.landmark]
        ys = [lm.y for lm in hand_landmarks.landmark]
        self.hand_rect = (
            int(min(xs) * w), int(min(ys) * h),
            int(max(xs) * w), int(max(ys) * h),
        )

    def draw(self, img):
        """Draw hand landmarks, fingertip, and bounding box on image."""
        if self.landmarks:
            self.mp_draw.draw_landmarks(
                img, self.landmarks, self.mp_hands.HAND_CONNECTIONS,
                self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                self.mp_draw.DrawingSpec(color=(255, 255, 255), thickness=1),
            )

        if self.fingertip:
            cv2.circle(img, self.fingertip, 10, (0, 0, 255), -1)

        if self.hand_rect:
            x1, y1, x2, y2 = self.hand_rect
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

    def close(self):
        self.hands.close()


# ====================================================================
# Gesture Recognition
# ====================================================================

class GestureController:
    """Track finger movement over time and detect swipe directions."""

    def __init__(self, swipe_threshold=80, cooldown_ms=500):
        self.track_points = []
        self.max_track = 10
        self.swipe_threshold = swipe_threshold
        self.last_trigger_time = 0
        self.cooldown_ms = cooldown_ms
        self.last_direction = None

    def update(self, fingertip):
        """Process a new fingertip position. Returns direction or None."""
        import time
        now = time.time() * 1000

        if fingertip is None:
            self.track_points.clear()
            return None

        self.track_points.append(fingertip)
        if len(self.track_points) > self.max_track:
            self.track_points.pop(0)

        if len(self.track_points) < self.max_track:
            return None

        # Cooldown check
        if now - self.last_trigger_time < self.cooldown_ms:
            return None

        # Calculate movement from track history
        first = self.track_points[0]
        last = self.track_points[-1]
        dx = last[0] - first[0]
        dy = last[1] - first[1]

        if abs(dx) < self.swipe_threshold and abs(dy) < self.swipe_threshold:
            return None

        if abs(dx) > abs(dy):
            direction = 'left' if dx > 0 else 'right'  # mirrored: swap left/right
        else:
            direction = 'down' if dy > 0 else 'up'

        self.last_trigger_time = now
        self.last_direction = direction
        return direction

    def draw_track(self, img):
        """Draw finger tracking trail on the image."""
        for pt in self.track_points:
            cv2.circle(img, pt, 5, (0, 0, 255), -1)
        if len(self.track_points) > 1:
            for i in range(len(self.track_points) - 1):
                cv2.line(img, self.track_points[i], self.track_points[i + 1],
                         (0, 255, 0), 2)


# ====================================================================
# Main Program
# ====================================================================

def main():
    print("[OK] Starting 2048 Gesture Game (MediaPipe Edition)...")
    game = Game2048()
    gesture = GestureController()
    hand_detector = HandDetector()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot open camera")
        return
    print("[OK] Camera opened")
    print("[INFO] Swipe index finger in camera view to control tiles")
    print("      ESC=Quit  R=Reset")

    cam_width, cam_height = 240, 180
    last_direction = None
    direction_display_timer = 0
    debug_info = "Move hand to start"

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        h, w = frame.shape[:2]

        # Flip frame horizontally (mirror) for natural interaction
        frame = cv2.flip(frame, 1)

        # MediaPipe detection on flipped frame (coordinates match display)
        hand_detector.process(frame)

        # Gesture recognition from index fingertip
        direction = gesture.update(hand_detector.fingertip)
        if direction:
            game.move(direction)
            print("[ACTION] Swipe {}".format(direction))
            last_direction = direction
            direction_display_timer = 30

        # Debug info on PIP
        debug_info = "No hand"
        if hand_detector.fingertip and len(gesture.track_points) >= 2:
            first = gesture.track_points[0]
            last = gesture.track_points[-1]
            dx = last[0] - first[0]
            dy = last[1] - first[1]
            debug_info = "dx={:+d} dy={:+d}".format(dx, dy)

        # Build PIP camera preview
        cam_small = cv2.resize(frame, (cam_width, cam_height))

        # Draw MediaPipe skeleton on PIP
        if hand_detector.detected:
            # Draw landmarks on a fresh copy of the resized camera frame
            cam_overlay = cv2.resize(frame, (cam_width, cam_height))
            hand_detector.draw(cam_overlay)
            cam_small = cam_overlay

            # Draw trail on PIP
            for pt in gesture.track_points:
                sx = int(pt[0] * cam_width / w)
                sy = int(pt[1] * cam_height / h)
                cv2.circle(cam_small, (sx, sy), 3, (0, 0, 255), -1)

        # Render game board
        game_img = draw_board(game)
        h_game, w_game = game_img.shape[:2]

        # Direction indicator
        if direction_display_timer > 0 and last_direction:
            direction_display_timer -= 1
            dir_arrow = {'up': '^', 'down': 'v', 'left': '<', 'right': '>'}
            arrow = dir_arrow.get(last_direction, '')
            cv2.putText(game_img, arrow, (w_game // 2 - 20, h_game - 50),
                        cv2.FONT_HERSHEY_DUPLEX, 2.0, (0, 255, 0), 3)
            cv2.putText(game_img, last_direction.upper(),
                        (w_game // 2 - 40, h_game - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Overlay camera PIP on bottom-right of game board
        pip_x = w_game - cam_width - 15
        pip_y = h_game - cam_height - 15
        game_img[pip_y:pip_y + cam_height, pip_x:pip_x + cam_width] = cam_small
        cv2.rectangle(game_img, (pip_x - 2, pip_y - 2),
                      (pip_x + cam_width + 2, pip_y + cam_height + 2),
                      (255, 255, 255), 2)

        # Debug info on game window
        cv2.putText(game_img, debug_info, (10, h_game - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

        cv2.imshow("2048 - Gesture Control (MediaPipe)", game_img)

        # Keyboard
        key = cv2.waitKey(30) & 0xFF
        if key == 27:  # ESC
            break
        elif key == ord('r'):
            game.reset()
            print("[ACTION] Game reset")
            last_direction = None
        elif key == ord('h'):
            print("[HELP] Swipe index finger in camera to move tiles")
            print("      ESC=Quit  R=Reset")

    hand_detector.close()
    cap.release()
    cv2.destroyAllWindows()
    print("[OK] Program exited")


if __name__ == "__main__":
    main()
