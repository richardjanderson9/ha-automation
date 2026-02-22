# Home Assistant Automations & Scripts

This repository contains a collection of Home Assistant (HA) automations, scripts, and tools for managing and enhancing home automation.

## Structure

- **automations/** — YAML files for automating various tasks in Home Assistant.
- **scripts/** — Reusable HA scripts categorized by purpose (e.g., user activity, monitoring).
- **blueprints/** — Home Assistant blueprints for creating automations with predefined templates.
- **docs/** — Documentation and deployment notes for the project.
- **localBuildScripts/** — Scripts and data for local development, including:
  - `installPythonRequirements.sh` — Installs Python dependencies.
  - `getDeviceData.py` — Fetches and exports HA entity data.
  - `filterData.py` — Filters exported data based on user input.
  - `localData/` — Contains configuration files and output data (e.g., `scriptData.json`, `ha_entities_output.yaml`).

## Notes

- The `localBuildScripts/localData/` folder is ignored in version control to protect sensitive data (e.g., tokens, configuration files).
- Python dependencies are managed via `scriptData.json` and installed using `installPythonRequirements.sh`.
- The repository includes blank YAML files for user and monitoring scripts, which can be customized as needed.

## Usage

1. Clone the repository.
2. Configure `localBuildScripts/localData/scriptData.json` with your Home Assistant URL and token.
3. Run `installPythonRequirements.sh` to set up dependencies.
4. Use `getDeviceData.py` to fetch and export HA entity data.
5. Customize scripts and automations as needed.
