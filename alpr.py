"""Compatibility wrapper for the Raspberry Pi ALPR script.

The actual implementation now lives in rpi/alpr.py to avoid hardware side
effects on import and to make it clear that it targets Raspberry Pi.
Run this file or rpi/alpr.py directly on the Pi.
"""

from rpi.alpr import main


if __name__ == "__main__":
    main()
