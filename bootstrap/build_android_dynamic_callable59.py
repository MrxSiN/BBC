#!/usr/bin/env python3
"""Rebuild the BF-owned DSO compiler stages, including iteration-58 core stages.

This delegates to the reproducible native standard-BF stage builder. No target
machine code or ELF contents originate in this Python module.
"""
from .build_android_dynamic_callable58 import main
if __name__=='__main__':main()
