# airTune - Hand Gesture Volume Control

Control your system volume with a simple hand gesture. **airTune** lets you adjust volume by rotating your **index finger** in the air, similar to luxury car infotainment systems.

## Overview

**airTune** uses OpenCV and MediaPipe to track hand gestures via webcam and adjusts system volume accordingly.

## Features

- Rotate clockwise to increase volume (+10% per full circle)
- Rotate counterclockwise to decrease volume (-10% per full circle)
- Works with both hands
- Displays real-time volume percentage

## Installation

Make sure Python is installed (**Python 3.9 or later**). Then install the required libraries:

```sh
pip install opencv-python mediapipe
```

## Usage

1. Run the script:
   ```sh
   python volume_control.py
   ```
2. The webcam detects your hand.
3. Rotate your **index finger** to adjust volume.
4. The current volume percentage is displayed on the screen.
5. Press **Esc** to exit.

## Adjusting System Volume

### For macOS

Uses `osascript` to change volume:

```python
subprocess.run(["osascript", "-e", f"set volume output volume {volume}"])
```

### For Windows

Uses `ctypes` to adjust volume:

```python
import ctypes
win_volume = int((volume / 100) * 65535)
ctypes.windll.winmm.waveOutSetVolume(0, win_volume | (win_volume << 16))
```

## Future Improvements

- Smoother gesture tracking
- Support for multiple hands & fingers
- Customizable gestures

## Contributing

Feel free to fork this project and improve it. PRs are welcome.

## License

This project is open-source and available under the **MIT License**.

---

Enjoy hands-free volume control with **airTune**!

