#!/usr/bin/env python3
import asyncio
import json
import websockets
import os
import sys
import subprocess # Added to run the filter script

# Paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "localData", "scriptData.json")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "localData", "ha_entities_output.yaml")
FILTER_SCRIPT = os.path.join(SCRIPT_DIR, "filterData.py") # Path to new script

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Configuration file not found at {CONFIG_FILE}")
        sys.exit(1)
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

async def get_ha_registry():
    full_config = load_config()
    ha_config = full_config.get("ha_config", {})
    
    url = ha_config.get("HA_URL", "").strip()
    token = ha_config.get("HA_TOKEN", "").strip()

    if len(url) < 10 or not token:
        print(f"❌ Error: HA_URL ('{url}') or HA_TOKEN is invalid in scriptData.json")
        sys.exit(1)

    if url.startswith("http"):
        url = url.replace("http", "ws", 1)
    
    if not url.endswith("/api/websocket"):
        url = url.rstrip("/") + "/api/websocket"

    try:
        print(f"🔗 Attempting to connect to: {url}")
        async with websockets.connect(url) as websocket:
            await websocket.recv() 
            await websocket.send(json.dumps({"type": "auth", "access_token": token}))
            
            auth_result = json.loads(await websocket.recv())
            if auth_result.get("type") != "auth_ok":
                print("❌ Auth Failed! Check your token in scriptData.json")
                return

            async def fetch(req_type, req_id):
                await websocket.send(json.dumps({"id": req_id, "type": req_type}))
                resp = await websocket.recv()
                return json.loads(resp).get("result", [])

            devices = {d['id']: d for d in await fetch("config/device_registry/list", 1)}
            entities = await fetch("config/entity_registry/list", 2)
            areas = {a['area_id']: a['name'] for a in await fetch("config/area_registry/list", 3)}

            include_domains = ['light', 'switch', 'climate', 'vacuum', 'calendar', 'tag', 'device_tracker']
            yaml_content = ""

            for ent in entities:
                domain = ent['entity_id'].split('.')[0]
                if domain in include_domains:
                    area_id = ent.get('area_id') or (devices.get(ent['device_id'], {}).get('area_id') if ent.get('device_id') else None)
                    area_name = areas.get(area_id, "No Area")
                    name = ent.get('name') or ent.get('original_name') or ent['entity_id']

                    yaml_content += f"### NAME: {name} | LOCATION: {area_name}\n"
                    yaml_content += f"type: turn_off\n"
                    yaml_content += f"device_id: {ent.get('device_id', 'NO_DEVICE_ID')}\n"
                    yaml_content += f"entity_id: {ent['entity_id']}\n"
                    yaml_content += f"domain: {domain}\n\n"

            with open(OUTPUT_FILE, "w") as f:
                f.write(yaml_content)
            
            print(f"💾 Success! Exported to: {OUTPUT_FILE}")

            # --- NEW INTERACTIVE SECTION ---
            print("\n" + "-"*30)
            user_input = input("❓ Would you like to filter this data now? (y/n): ").lower()
            if user_input == 'y':
                search_term = input("🔍 Enter search term (Room, Domain, or Name): ")
                # Run the filter script using the search term
                subprocess.run([sys.executable, FILTER_SCRIPT, search_term])
            # -------------------------------

    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_ha_registry())