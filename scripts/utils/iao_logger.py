#!/usr/bin/env python3
"""Shim for iao.logger — see iao/iao/logger.py"""
from iao.logger import log_event

if __name__ == "__main__":
    # If called directly, it doesn't do much, but we could add a CLI test
    log_event("command", "shim-test", "none", "test")
