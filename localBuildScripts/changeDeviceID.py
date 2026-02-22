#!/usr/bin/env python3
import asyncio
import json
import websockets
import os

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "localData", "scriptData.json")
BACKUP_FILE = os.path.join(SCRIPT_DIR, "localData", "ha_entities_output.yaml")

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def parse_device_backups():
    if not os.path.exists(BACKUP_FILE):
        return []
    
    devices = {}
    with open(BACKUP_FILE, 'r') as f:
        blocks = f.read().split("### NAME: ")[1:]
        for block in blocks:
            lines = block.strip().split('\n')
            # Extract name from header: "### NAME: phone | LOCATION: Bedroom"
            name = lines[0].split(" | ")[0].strip()
            
            data = {}
            for line in lines[1:]:
                if ": " in line:
                    k, v = line.split(": ", 1)
                    data[k.strip()] = v.strip()
            
            # Map by device_id to ensure we only rename the hardware once
            dev_id = data.get('device_id')
            if dev_id and dev_id != "NO_DEVICE_ID":
                devices[dev_id] = name
    return devices

async def rename_devices_in_ha(device_map):
    config = load_config().get("ha_config", {})
    url = config.get("HA_URL").replace("http", "ws", 1) + "/api/websocket"
    token = config.get("HA_TOKEN")

    async with websockets.connect(url) as ws:
        await ws.recv() 
        await ws.send(json.dumps({"type": "auth", "access_token": token}))
        auth_resp = json.loads(await ws.recv())
        
        if auth_resp.get("type") != "auth_ok":
            print("❌ Auth Failed")
            return

        print(f"🔗 Connected. Prepared to rename {len(device_map)} devices.")
        
        for i, (dev_id, new_name) in enumerate(device_map.items()):
            msg_id = 2000 + i
            payload = {
                "id": msg_id,
                "type": "config/device_registry/update",
                "device_id": dev_id,
                "name_by_user": new_name  # This targets the 'Friendly Name' in HA
            }
            await ws.send(json.dumps(payload))
            result = json.loads(await ws.recv())
            
            if result.get("success"):
                print(f"✅ Renamed Device {dev_id} to '{new_name}'")
            else:
                print(f"⚠️ Could not rename {dev_id}: {result.get('error', {}).get('message')}")

async def main():
    device_data = parse_device_backups()
    
    if not device_data:
        print("❌ No valid device data found in backup.")
        return

    print("\n--- DEVICE RENAME PREVIEW ---")
    for dev_id, name in list(device_data.items())[:5]: # Show first 5
        print(f"Hardware ID: {dev_id} --> New Name: {name}")
    print("-----------------------------\n")

    confirm = input(f"❓ Push these {len(device_data)} name changes to the hardware registry? (y/n): ").lower()
    
    if confirm == 'y':
        await rename_devices_in_ha(device_data)
    else:
        print("👋 Cancelled.")

if __name__ == "__main__":
    asyncio.run(main())