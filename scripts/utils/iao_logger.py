#!/usr/bin/env python3
"""Shim for iao_middleware.logger — see iao-middleware/iao_middleware/logger.py"""
from iao_middleware.logger import log_event

if __name__ == "__main__":
    # If called directly, it doesn't do much, but we could add a CLI test
    log_event("command", "shim-test", "none", "test")
