#!/usr/bin/python3

import time

def dummy_action():
    """A dummy action to simulate a long-running task."""
    print("Dummy action started...")
    while True:
        print("Performing dummy action...")
        time.sleep(5)  # Wait for 5 seconds before repeating the action

if __name__ == "__main__":
    dummy_action()
