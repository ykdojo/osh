#!/usr/bin/env python3
"""
Minimal test for clipboard image operations.
Let's simplify even more and try a different approach.
"""

import platform
import copykitten
import subprocess
import time

print(f"Running on: {platform.system()} {platform.release()}")
print("Testing clipboard operations")

# Step 1: First, save original clipboard content (text only)
print("\n1. Saving original clipboard content...")
try:
    original_text = copykitten.paste()
    print(f"  Original clipboard text: '{original_text}'")
except Exception as e:
    print(f"  No text in clipboard or error: {e}")
    original_text = None

# Step 2: Use the system to copy an image to the clipboard
print("\n2. Creating screenshot to clipboard...")
is_macos = platform.system() == 'Darwin'

if is_macos:
    # On macOS, use screencapture to take a small screenshot directly to clipboard
    try:
        # -c means copy to clipboard, -R specifies region (x,y,width,height)
        subprocess.run(['screencapture', '-c', '-R100,100,200,200'], check=True)
        print("  Screenshot taken and copied to clipboard")
        time.sleep(1)  # Give time for clipboard to update
    except Exception as e:
        print(f"  Error taking screenshot: {e}")
else:
    print("  This test only works on macOS currently")
    exit(1)

# Step 3: Check what's in the clipboard now
print("\n3. Checking clipboard content...")

# Check for text
try:
    text = copykitten.paste()
    print(f"  Clipboard text: '{text}'")
except Exception as e:
    print(f"  No text in clipboard or error: {e}")

# Step 4: Try to get the image
print("\n4. Trying to retrieve image from clipboard...")
try:
    # First check how paste_image works
    print(f"  paste_image signature: {copykitten.paste_image.__doc__}")
    
    # Now try to get the image
    image_data = copykitten.paste_image()
    if image_data:
        print(f"  Successfully retrieved image (data size: {len(image_data)} bytes)")
    else:
        print("  No image found in clipboard")
except Exception as e:
    print(f"  Error retrieving image: {e}")

# Step 5: Restore original clipboard content
print("\n5. Restoring original clipboard content...")
if original_text:
    try:
        copykitten.copy(original_text)
        print(f"  Restored original text to clipboard")
    except Exception as e:
        print(f"  Error restoring clipboard: {e}")
else:
    try:
        copykitten.clear()
        print("  Cleared clipboard")
    except Exception as e:
        print(f"  Error clearing clipboard: {e}")

print("\nTest completed.")