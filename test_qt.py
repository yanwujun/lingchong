#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test Qt platform plugin"""

import sys
from PyQt5.QtWidgets import QApplication

try:
    app = QApplication(sys.argv)
    print("SUCCESS: Qt platform plugin loaded!")
    print(f"Platform: {app.platformName()}")
    print("You can now run main.py")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

