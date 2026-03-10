import json
import time
import network
import socket
import secrets
from machine import Pin
from ir_rx.acquire import IR_GET
from ir_tx import Player


def connect():
    #wifi setup
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.SSID, secrets.PASSWORD)
    while wlan.isconnected() == False:
        print("connecting")
        time.sleep(1)
    print(wlan.ifconfig())


# Setup
RX_PIN = 16
TX_PIN = 17
CODES_FILE = 'ir_codes.json'

# Load saved codes
ir_codes = {}
try:
    with open(CODES_FILE, 'r') as f:
        ir_codes = json.load(f)
    print(f"Loaded {len(ir_codes)} commands from {CODES_FILE}")
except OSError:
    print("No saved codes found. Starting fresh.")


# Functions
def save_codes():
    try:
        with open(CODES_FILE, 'w') as f:
            json.dump(ir_codes, f)
        print(f" → Saved {len(ir_codes)} commands")
    except Exception as e:
        print(f"Save failed: {e}")

def list_codes():
    if not ir_codes:
        print("No recorded codes yet.")
        return
    print(f"\nSaved commands ({len(ir_codes)} total):")
    for i, (name, timings) in enumerate(ir_codes.items(), 1):
        print(f"  {i:2d}. {name} ({len(timings)} edges)")

def playback(cmd):
    cmd = cmd.strip()
    if not cmd:
        print("No command entered.")
        return
    if cmd not in ir_codes:
        print(f"Unrecognised command: '{cmd}'")
        return

    print(f" → Playing '{cmd}' ({len(ir_codes[cmd])} edges)...")
    try:
        tx_pin = Pin(TX_PIN, Pin.OUT, value=0)
        player = Player(tx_pin)
        player.play(ir_codes[cmd])
        time.sleep(0.3)  
        print(f"Playback of '{cmd}' finished.")
    except Exception as e:
        print(f"Playback error: {e}")

def capture_mode():
    print("\nCapture mode. Enter command name or 'q' to return.")
    while True:
        name = input("Command name: ").strip()
        if name.lower() == 'q':
            return
        if not name:
            print("Name cannot be empty.")
            continue
        if name in ir_codes:
            ow = input(f"'{name}' exists. Overwrite? (y/n): ").lower().strip()
            if ow != 'y':
                continue

        print(f" → Capturing '{name}'... Press and hold remote button (1–3 sec)")
        try:
            rx_pin = Pin(RX_PIN, Pin.IN, Pin.PULL_UP)
            acq = IR_GET(rx_pin)
            timings = acq.acquire()
        except Exception as e:
            print(f"Capture setup failed: {e}")
            continue

        edge_count = len(timings)
        if edge_count > 10:
            ir_codes[name] = timings
            print(f"Success! Captured {edge_count} edges.")
            save_codes()
        else:
            print(f"Capture too short ({edge_count} edges). Try closer or hold longer.")


# Main menu
def menu():
    while True:
        print("\nIR Remote Tool")
        print("  (1) Capture new command")
        print("  (2) List recorded codes")
        print("  (3) Use / replay command")
        print("  (0) Quit")
        print(f"     ({len(ir_codes)} commands loaded)")

        choice = input("Select: ").strip()
        try:
            choice = int(choice)
        except ValueError:
            print("Please enter a number.")
            continue

        if choice == 1:
            capture_mode()
        elif choice == 2:
            list_codes()
        elif choice == 3:
            list_codes() 
            cmd = input("Enter command name to play: ").strip()
            playback(cmd)
        elif choice == 0:
            save_codes()  
            print("\nGoodbye. All changes saved.")
            break
        else:
            print("Invalid choice (0–3).")


#menu()

connect()