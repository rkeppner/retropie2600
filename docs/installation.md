# RetroPie2600 Installation Guide

This guide covers the installation of the retropie2600 daemon on a Raspberry Pi 3B+ running RetroPie, integrated into an Atari 2600 CX-2600A shell.

## Prerequisites

- Raspberry Pi 3B+
- Hardware assembled (reference `docs/hardware-guide.md`)
- RetroPie image flashed to microSD
- Pi connected to HDMI display and network
- 2x 2600-daptor 2e USB adapters (for joysticks/paddles)

## 1. RetroPie Base Setup

### Flash RetroPie Image
1. Download the RetroPie image for Raspberry Pi 2/3 (`retropie-buster-4.x-rpi2_rpi3.img.gz`) from the [official website](https://retropie.org.uk/download/).
2. Use [balenaEtcher](https://www.balena.io/etcher/) to flash the image to your microSD card.

### Initial Boot and Configuration
1. Insert the microSD card, connect a keyboard, and power on the Pi.
2. Follow the on-screen prompts to configure your keyboard/controller in EmulationStation.
3. Configure WiFi: **RetroPie** -> **WiFi**.
4. Enable SSH: **RetroPie** -> **Raspi-Config** -> **Interfacing Options** -> **SSH** -> **Yes**.

### Update System
Connect via SSH (`ssh pi@retropie.local`) and update the system:

```bash
sudo apt update && sudo apt upgrade -y
```

### Install lr-stella
Ensure the Stella core is installed:
1. **RetroPie** -> **RetroPie-Setup**.
2. **Manage Packages** -> **Manage Main Packages**.
3. Select **lr-stella** and choose **Install from binary**.

## 2. System Dependencies

The daemon requires `pigpiod` for GPIO access and a Python virtual environment.

```bash
# Install pigpiod
sudo apt install pigpio -y

# Enable and start pigpiod
sudo systemctl enable pigpiod && sudo systemctl start pigpiod

# Verify pigpiod status
sudo systemctl status pigpiod

# Install python3-venv
sudo apt install python3-venv -y
```

## 3. Daemon Installation

Clone the repository and set up the Python environment.

```bash
# Clone the repository to the standard path
sudo git clone https://github.com/YOUR_USERNAME/retropie2600.git /opt/retropie2600
sudo chown -R pi:pi /opt/retropie2600

# Create Python venv
python3 -m venv /opt/retropie2600/venv

# Install the package in editable mode
/opt/retropie2600/venv/bin/pip install -e /opt/retropie2600/

# Create config directory
sudo mkdir -p /etc/retropie2600/

# Copy and customize config
sudo cp /opt/retropie2600/config/switches.example.yaml /etc/retropie2600/switches.yaml
sudo nano /etc/retropie2600/switches.yaml  # Edit pin assignments if needed
```

## 4. systemd Service Setup

Install the service file and udev rules to allow the daemon to run on boot.

```bash
# Copy service file
sudo cp /opt/retropie2600/systemd/retropie2600.service /etc/systemd/system/

# Copy udev rules (for uinput access)
sudo cp /opt/retropie2600/systemd/99-retropie2600.rules /etc/udev/rules.d/

# Reload systemd and udev
sudo systemctl daemon-reload
sudo udevadm control --reload-rules

# Enable and start the service
sudo systemctl enable retropie2600
sudo systemctl start retropie2600

# Check status
sudo systemctl status retropie2600
```

## 5. RetroArch Configuration

The daemon communicates with RetroArch via UDP to toggle shaders and send commands.

### Network Commands
Enable network commands in `/opt/retropie/configs/all/retroarch.cfg`:

```text
network_cmd_enable = "true"
network_cmd_port = "55355"
```

### CRT Shader
For the Channel switch to work, ensure a CRT shader is configured. See `docs/retroarch-setup.md` for detailed instructions on setting up the Atari 2600 specific CRT shader and core overrides.

## 6. Boot Configuration

Edit `/boot/config.txt` to enable wake-from-halt using the original Atari power switch.

```bash
sudo nano /boot/config.txt
```

Add the following line:

```text
dtoverlay=gpio-shutdown,gpio_pin=26
```

**Note**: This enables the Pi to boot back up when the power switch is flipped to ON after a safe shutdown (assuming the switch is wired to GPIO 26).

Optional: Add a temperature-controlled fan if installed:
```text
dtoverlay=gpio-fan,gpiopin=14,temp=60000
```

## 7. 2600-daptor 2e Setup

The 2600-daptor 2e adapters are natively supported as USB HID devices.

1. Plug in both adapters to the Pi USB ports.
2. In EmulationStation, press **Start** -> **Configure Input**.
3. Follow the prompts for each adapter. The 2600-daptor 2e maps the Atari joystick and fire button to standard USB gamepad buttons.

## 8. Verification Steps

Confirm each component is working by watching the live logs.

```bash
# Watch live daemon logs while testing each switch
journalctl -u retropie2600 -f
```

### Test Each Switch
- **Power switch (OFF)**: Should log "Safe shutdown initiated".
- **Channel switch**: Should log "Shader toggle".
- **TV Type switch**: Should log `SwitchEvent` for `tv_type`.
- **Game Select**: Should log `SwitchEvent` for `game_select` pressed.
- **Game Reset**: Should log `SwitchEvent` for `game_reset` pressed.
- **Difficulty switches**: Should log `SwitchEvent` with position `a` or `b`.

### Manual Shader Test
Test the UDP connection to RetroArch (requires RetroArch to be running):

```bash
echo -n "SHADER_TOGGLE" | nc -u 127.0.0.1 55355
```

### Service Health
Check that the service is active and the watchdog is happy:

```bash
sudo systemctl status retropie2600
```

## Troubleshooting

- **Service fails to start**: Check `journalctl -u retropie2600` for Python tracebacks or configuration errors.
- **"pigpiod not connected"**: Ensure the pigpiod service is running: `sudo systemctl start pigpiod`.
- **Switches not responding**: Verify pin numbers in `/etc/retropie2600/switches.yaml` match your physical wiring.
- **Permission denied on uinput**: Verify the `pi` user is in the `input` group:
  ```bash
  groups pi
  # If 'input' is missing:
  sudo usermod -aG input pi
  sudo reboot
  ```
- **GPIO permissions**: Ensure the `pi` user is in the `gpio` group: `sudo usermod -aG gpio pi`.
