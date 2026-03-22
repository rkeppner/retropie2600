# RetroArch and lr-stella Setup Guide

## Overview

The retropie2600 daemon requires specific RetroArch configuration to enable:
1. **Network command interface** — allows the daemon to send shader toggle commands via UDP
2. **CRT shader support** — provides an authentic Atari 2600 display experience

This guide covers the essential setup steps and optional enhancements.

## Enable Network Commands (REQUIRED)

Network commands allow the retropie2600 daemon to toggle the display shader via UDP, triggered by your channel switch hardware.

### Step 1: Get the Configuration

Copy the required settings from the example configuration file:

```bash
cat config/retroarch.cfg.example
```

These settings are:
- `network_cmd_enable = "true"` — enables RetroArch's network command listener
- `network_cmd_port = "55355"` — port for network commands (must match `retroarch_port` in `/etc/retropie2600/switches.yaml`)

### Step 2: Apply to RetroArch Config

On your Raspberry Pi, edit RetroArch's main configuration file:

```bash
sudo nano /opt/retropie/configs/all/retroarch.cfg
```

Add or update these lines:

```cfg
network_cmd_enable = "true"
network_cmd_port = "55355"
```

Save and exit (Ctrl+X, then Y, then Enter).

### Step 3: Test Network Commands (Manual Verification)

Test that RetroArch is listening on port 55355:

```bash
echo -n "SHADER_TOGGLE" | nc -u 127.0.0.1 55355
```

To test from a remote machine on your network:

```bash
echo -n "SHADER_TOGGLE" | nc -u <pi_ip_address> 55355
```

If the command succeeds silently (no error), RetroArch is listening. You can verify by checking if `video_shader_enable` in RetroArch toggles when you run the command.

**Note:** RetroArch must be running (with a game active or in a safe state) for network commands to work.

## CRT Shader Setup (Optional but Recommended)

A CRT shader provides scanlines and color blending for an authentic Atari 2600 display. The **zfast-crt** shader is optimized for Raspberry Pi 3B+ performance.

### Step 1: Verify Shader Availability

SSH into your Pi and check if the shader exists:

```bash
ls -la /opt/retropie/emulators/retroarch/shader/shaders_glsl/crt/
```

You should see files like `zfast-crt.glslp` and related `.glsl` files.

**If the shader is missing**, you may need to install it via RetroPie's setup script or manually copy it from the RetroArch GitHub repository.

### Step 2: Enable Shader in Configuration

Add these settings to `/opt/retropie/configs/all/retroarch.cfg`:

```cfg
video_shader_enable = "true"
video_shader = "/opt/retropie/emulators/retroarch/shader/shaders_glsl/crt/zfast-crt.glslp"
```

### Step 3: Enable Shader via RetroArch UI (Alternative)

If you prefer to set up shaders interactively:

1. Start a game in lr-stella
2. Press **Select** (or your configured menu button) to open the RetroArch Quick Menu
3. Navigate to **Shaders** → **Video Filter** or **Shader** menu
4. Select **zfast-crt** or your preferred shader
5. Press **Save Game Overrides** to apply shader to all games

### Step 4: Test Shader Toggle

Once network commands are enabled and shader is configured:

1. Start an Atari 2600 game in lr-stella
2. Trigger your physical channel switch (wired to GPIO 6 and 13 by default)
3. The shader should toggle ON/OFF on the display

If the shader doesn't toggle:
- Check that `network_cmd_enable = "true"` is in RetroArch config
- Verify the shader path exists on your Pi: `ls /opt/retropie/emulators/retroarch/shader/shaders_glsl/crt/zfast-crt.glslp`
- Check RetroArch logs for network command errors

## lr-stella Core Options

The **lr-stella** core provides Atari 2600 emulation with several optional tweaks. Configure these for better game compatibility and display.

### Accessing Core Options

To adjust lr-stella options while playing a game:

1. Press **Select** to open RetroArch Quick Menu
2. Navigate to **Options**
3. Adjust settings (changes apply immediately)
4. Select **Save Game Overrides** to save per-game, or **Save Core Overrides** for all games

### Recommended Options

**Display Filter** (`stella_filter`)
- `none` — no filter (raw pixels)
- `phosphor` — simulates CRT phosphor glow
- `ntsc` — NTSC color encoding and blur
- `scanlines` — adds scanlines (good with shader disabled)

**Overscan Crop** (`stella_crop_horiz_overscan`)
- `enabled` — crops the left and right borders (reduces pillar-boxing)
- `disabled` — shows full original resolution (may show timing artifacts)

Example core config for `/opt/retropie/configs/all/retroarch-cores/stella_libretro.so.cfg`:

```cfg
stella_filter = "none"
stella_crop_horiz_overscan = "enabled"
```

## Troubleshooting

### RetroArch Not Responding to Network Commands

**Symptom:** `SHADER_TOGGLE` command times out or is ignored.

**Checks:**
1. Verify `network_cmd_enable = "true"` in `/opt/retropie/configs/all/retroarch.cfg`
2. Verify `network_cmd_port = "55355"` matches the port in your command
3. Ensure RetroArch is running (not paused or in menu)
4. Check RetroArch logs: `tail -f ~/.config/retroarch/retroarch.log`

### Shader Not Toggling

**Symptom:** Shader toggle command runs but shader doesn't change.

**Checks:**
1. Verify shader path exists: `ls /opt/retropie/emulators/retroarch/shader/shaders_glsl/crt/zfast-crt.glslp`
2. Verify `video_shader_enable = "true"` in config
3. Verify `video_shader` path is correct (no typos)
4. Check GPU memory is sufficient (Pi 3B+ should have 256MB allocated)

### Port Conflict or Already in Use

**Symptom:** RetroArch won't start or network commands fail with "Address already in use."

**Solution:**
1. Check if another instance of RetroArch is running: `ps aux | grep retroarch`
2. Kill any stray processes: `pkill -f retroarch`
3. Change the port in both RetroArch config and `switches.yaml` to an unused port (e.g., 55356)

### Port Mismatch

**Symptom:** Network command works manually but daemon shader toggle doesn't.

**Solution:**
Verify that `retroarch_port` in `/etc/retropie2600/switches.yaml` matches `network_cmd_port` in RetroArch config (both should be `55355`).

Example from `switches.yaml`:

```yaml
retroarch_port: 55355  # Must match network_cmd_port in RetroArch
```

## Next Steps

Once network commands and shaders are configured, the retropie2600 daemon will:
- Listen for channel switch hardware input
- Send `SHADER_TOGGLE` commands via UDP to RetroArch
- Automatically toggle the CRT shader ON/OFF

See `/etc/retropie2600/switches.yaml` for full daemon configuration options.
