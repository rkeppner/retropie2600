# RetroPie2600 Hardware Wiring Guide

This document provides a comprehensive guide for integrating a Raspberry Pi 3B+ into a vintage Atari 2600 CX-2600A shell. The project involves repurposing the original physical switches, power LED, and enclosure to create an authentic-feeling Atari emulation console.

## 1. Bill of Materials (BOM)

The following components are required for the conversion.

| Component | Description |
| :--- | :--- |
| **Raspberry Pi 3B+** | Main controller with built-in Wi-Fi and 40-pin GPIO header |
| **MicroSD Card** | 16GB+ recommended, Class 10 for performance |
| **2× 2600-daptor 2e** | USB adapters for original Atari joysticks and paddles |
| **2× USB Panel-Mount Cables** | Extension cables for external controller ports |
| **1× Ethernet Panel-Mount Cable** | Extension for networking access |
| **1× 5V Micro-USB Power Supply** | 2.5A minimum recommended |
| **1× 40mm 5V Fan + Heatsink** | For active cooling inside the enclosed shell |
| **1× Red LED (3mm or 5mm)** | To replace original power jack with status indicator |
| **1× 330Ω Resistor** | Current limiting for the power LED |
| **DuPont Jumper Wires** | At least 12 female-to-female wires |
| **Solder + Soldering Iron** | For making connections to the Atari board switch pads |
| **Dremel / Rotary Tool** | For rear port cutouts (HDMI, Power, USB, Ethernet) |
| **Multimeter** | Essential for continuity testing and safety checks |

## 2. GPIO Pin Assignment Table

The following pin assignments match the default configuration in `config/switches.example.yaml`. All inputs use the Pi's internal 3.3V pull-up resistors (active-low logic).

| Switch / Component | BCM Pin | Physical Pin | Type | Stella Key / Function |
| :--- | :--- | :--- | :--- | :--- |
| **Power (Shutdown)** | 26 | 37 | Toggle | `gpio-shutdown` |
| **TV Type Color** | 4 | 7 | Toggle | F3 |
| **TV Type B&W** | 17 | 11 | Toggle | F4 |
| **Game Select** | 22 | 15 | Momentary | F1 |
| **Game Reset** | 27 | 13 | Momentary | F2 |
| **Left Difficulty A** | 23 | 16 | Toggle | F5 |
| **Left Difficulty B** | 24 | 18 | Toggle | F6 |
| **Right Difficulty A** | 25 | 22 | Toggle | F7 |
| **Right Difficulty B** | 5 | 29 | Toggle | F8 |
| **Channel 2** | 6 | 31 | Toggle | CRT Shader ON |
| **Channel 3** | 13 | 33 | Toggle | CRT Shader OFF |
| **Power LED** | 12 | 32 | Output | Red LED indicator |
| **Fan** | 5V | Pin 4 | Direct | Always-on power |
| **Fan Ground** | GND | Pin 6 | Direct | Common Ground |

## 3. Switch Wiring Instructions

The Atari 2600 uses DPDT (Double Pole Double Throw) switches for toggles and momentary actions. After removing the original ICs from the Atari board, you can solder directly to the pads beneath the switches.

### Identifying Signal Contacts
Use a multimeter in continuity mode to identify which pins on the switch close when flipped or pressed.
- **Toggle Switches:** One center pin (common) and two outer pins. One outer pin will show continuity to common in position A, the other in position B.
- **Momentary Switches:** Pins will show continuity only while the switch is actively depressed.

### Wiring Diagram (ASCII)
Connect the Common pin of each switch to a Pi Ground (GND) pin. Connect the signal pins to the respective GPIO pins.

```text
Toggle Switch (DPDT)          Momentary Switch
   [Pin A] -- GPIO X             [Pin A] -- GPIO Y
   [Common] -- GND               [Common] -- GND
   [Pin B] -- GPIO Z
```

### Pull-Up Resistors
All switch pins use the Pi's internal 3.3V pull-ups configured via `pigpio`. No external resistors are needed for switch inputs. The daemon software detects when a pin is pulled to Ground (LOW) when the switch is closed.

## 4. Power LED Installation

The original Atari 2600 power jack hole is repurposed for a red status LED.

- **Anode (+):** Connect to Pi **Pin 32 (GPIO 12)** via a 330Ω resistor.
- **Cathode (-):** Connect to any Ground pin (e.g., **Pin 30**).
- **Calculation:** (3.3V - 2.0V) / 0.02A = 65Ω minimum; 330Ω provides a safe, visible brightness.

## 5. Fan Installation

Active cooling is necessary for the Pi 3B+ when housed inside the plastic Atari shell.

- **Power:** Connect the red wire to **Pin 4 (5V)**.
- **Ground:** Connect the black wire to **Pin 6 (GND)**.
- **Mounting:** Attach heatsinks to the Pi CPU and GPU. Mount the 40mm fan near the top vents of the Atari case to ensure proper exhaust airflow.
- **Optional Control:** To enable temperature-controlled activation, use `dtoverlay=gpio-fan` in `/boot/config.txt`.

## 6. Port Cutout Guide

The Raspberry Pi should be oriented so the ports face the rear of the Atari case.

1. **HDMI:** Cut a slot for a standard HDMI cable or panel-mount extension.
2. **Power:** Align with the original power entry area for micro-USB.
3. **USB/Ethernet:** Use panel-mount extensions to bring the 2600-daptor connections and network port to the rear panel.
4. **Safety:** Use a Dremel with a plastic-cutting wheel. Wear eye protection.

## 7. Safety Warnings ⚠️

⚠️ **Voltage Check FIRST:** The original Atari board may have residual 5V logic. Connecting 5V to the Pi's 3.3V GPIO pins will destroy the Pi. Use a multimeter to verify there is **zero voltage** on the switch pads before connecting them to the Pi.

⚠️ **ESD Precautions:** Handle the Raspberry Pi by the edges. Ground yourself before touching GPIO pins to prevent electrostatic discharge damage.

⚠️ **Common Ground:** The Pi Ground and the Atari board ground must share a common ground bus. Ensure the GND connections from the switches are tied back to the Pi's GND pins.

⚠️ **Wire Routing:** Ensure all DuPont wires are secured with cable ties. Route wires away from the fan blades and ensure no bare wires can cross or short against the shell or other components.

⚠️ **Power Off Before Wiring:** Always disconnect the 5V power supply from the Pi before changing any GPIO connections.

## 8. /boot/config.txt Configuration

Add the following lines to your `/boot/config.txt` to enable system-level hardware features:

```text
# Enable software-controlled shutdown and wake-from-halt
dtoverlay=gpio-shutdown,gpio_pin=26

# Optional: Temperature controlled fan (turns on at 60°C)
# Replace X with BCM pin if using a transistor/MOSFET driver
# dtoverlay=gpio-fan,gpiopin=X,temp=60000
```

**Note:** `gpio-shutdown` allows the power switch to trigger a clean shutdown and also allows the Pi to boot from a halted state by flipping the switch.

## 9. Testing Your Wiring

Once wired, you can verify the hardware integration using the system logs.

1. Power on the system and SSH into the Pi.
2. Run the following command:
   ```bash
   journalctl -u retropie2600 -f
   ```
3. Flip each switch and observe the output.
   - **Toggles:** Should show "Switch [Name] changed to [State]"
   - **Momentary:** Should show "Button [Name] pressed" and "released"
4. If the LED does not light up, check the orientation (polarity) and the resistor connection.
