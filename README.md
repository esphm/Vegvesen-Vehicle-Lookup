# Vegvesen Vehicle Lookup

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration that looks up Norwegian vehicle technical data from [Statens vegvesen](https://www.vegvesen.no/) using their **Autosys Kjøretøydata – enkeltoppslag** API.

This repository was made with Claude Opus 4.6.

---

## Features

- **106 vehicle attributes** – Make, model, fuel type, engine specs, weights, dimensions, CO₂/WLTP/NEDC emissions, noise levels, inspection dates, and more. 24 sensors are enabled by default; the remaining 82 can be individually enabled via the Home Assistant entity UI.
- **On-demand updates only** – No polling. Lookups are triggered only when:
  - The registration number is changed (debounced).
  - The "Lookup Now" button is pressed.
  - The `vegvesen_vehicle_lookup.lookup` service is called.
  - Home Assistant starts (if a registration number was previously entered).
- **Entity-level control** – Enable or disable individual sensors from the Home Assistant Entities page — no options flow needed.
- **Debounce control** – Configure debounce delay and a fallback timeout via the Options flow.
- **Diagnostic entities** – Last lookup status, last updated timestamp, and raw JSON response for troubleshooting.
- **HACS compatible** – Install via the Home Assistant Community Store.

## Limitations

- **Owner information is not available** from the enkeltoppslag API. Only technical vehicle data is returned.
- Registration number format is validated as 2 letters + 5 digits (e.g., `EF56000`). Personal/veteran plates with other formats are not supported by the validation, though the API itself may accept them.
- The API has a rate limit of **50,000 calls per API key per day**.

---

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant.
2. Go to **Integrations** → click the three-dot menu (⋮) → **Custom repositories**.
3. Add this repository URL and select **Integration** as the category.
4. Click **Install** on the Vegvesen Vehicle Lookup card.
5. Restart Home Assistant.

### Manual

1. Copy the `custom_components/vegvesen_vehicle_lookup` folder into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.

---

## Configuration

### Step 1: Add the integration

1. In Home Assistant, go to **Settings** → **Devices & Services** → **Add Integration**.
2. Search for **Vegvesen Vehicle Lookup**.
3. Enter your Statens vegvesen API key.
   - You can apply for a key at: <https://www.vegvesen.no/dinside/data-og-api-er/tilgang-til-api-for-kjoretoyopplysninger/vis>
4. The integration validates your key against the API. If it fails, double-check your key.

### Step 2: Configure options (optional)

1. Go to **Settings** → **Devices & Services** → **Vegvesen Vehicle Lookup** → **Configure**.
2. Set debounce behaviour:
   - **`debounce_seconds`** (default `15`): After you commit a registration number change, wait this many seconds before performing the lookup. Resets if the value changes again within the window. Set to `0` to look up immediately.
   - **`fallback_lookup_seconds`** (default `60`): Maximum wait time after the *first* change in a series of rapid edits. Even if the user keeps changing the value, a lookup is forced after this duration. Set to `0` to disable.

### Step 3: Enable/disable sensors

After your first lookup, all 106 attribute sensors are created. 24 are enabled by default. To enable additional sensors:

1. Go to **Settings** → **Devices & Services** → **Vegvesen Vehicle Lookup** → your device.
2. Click a disabled entity → **Enable** (or use the Entities page to bulk-enable).

---

## Usage

### Basic flow

1. Find the **Vehicle Registration Number** text entity (under your Vegvesen Vehicle Lookup device).
2. Enter a registration number (e.g., `EF56000`) and press Enter / save.
3. Wait for the debounce timer (default 15 seconds), or press the **Lookup Now** button for an immediate result.
4. Sensor entities update with the vehicle's technical data.

### Service call

You can also trigger lookups from automations or scripts:

```yaml
service: vegvesen_vehicle_lookup.lookup
data:
  regnr: "EF56000"
```

If `regnr` is omitted, the lookup uses the currently entered registration number.

### Automation example

```yaml
automation:
  - alias: "Look up vehicle on tag scan"
    trigger:
      - platform: tag
        tag_id: my_nfc_tag
    action:
      - service: vegvesen_vehicle_lookup.lookup
        data:
          regnr: "AB12345"
```

---

## Entities

| Entity | Type | Description |
|---|---|---|
| Vehicle Registration Number | `text` | Editable field for the registration number |
| Lookup Now | `button` | Trigger an immediate lookup |
| *(106 vehicle attribute sensors)* | `sensor` | See [Supported Attributes](#supported-attributes) below |
| Last Lookup Status | `sensor` | Diagnostic: success / not_found / error |
| Last Updated | `sensor` | Diagnostic: timestamp of last lookup |
| Raw Response | `sensor` | Diagnostic: truncated raw JSON (disabled by default) |

---

## Supported Attributes

All 106 attributes from the Statens vegvesen API are available as sensor entities. **24 are enabled by default** (marked ✅); the remaining 82 are created but disabled. Enable them from the Home Assistant Entities page.

<details>
<summary>Full list of 106 attributes</summary>

| Key | Name | Unit | Default |
|---|---|---|:---:|
| `registration_number` | Registration Number | | ✅ |
| `chassis_number` | Chassis Number (VIN) | | ✅ |
| `make` | Make | | ✅ |
| `make_code` | Make Code | | |
| `model` | Model | | ✅ |
| `type_designation` | Type Designation | | |
| `manufacturer_name` | Manufacturer Name | | |
| `color` | Color | | ✅ |
| `body_type` | Body Type | | ✅ |
| `body_art` | Body Art | | |
| `steering_side` | Steering Side | | ✅ |
| `num_doors` | Number of Doors | | ✅ |
| `bus_category` | Bus Category | | |
| `vehicle_group` | Vehicle Group | | ✅ |
| `vehicle_category_code` | Vehicle Category Code | | |
| `vehicle_subcategory_code` | Vehicle Subcategory Code | | |
| `vehicle_tax_code` | Vehicle Tax Code | | |
| `special_characteristics` | Special Characteristics | | |
| `type_approval_conformity` | Type Approval Conformity | | |
| `ef_type_approval_number` | EF Type Approval Number | | |
| `registration_status` | Registration Status | | ✅ |
| `first_registration_date` | First Registration Date | | ✅ |
| `first_technical_approval_date` | First Technical Approval Date | | |
| `driving_purpose` | Driving Purpose | | |
| `industry_code_description` | Industry Code Description | | |
| `deregistered_since_date` | Deregistered Since Date | | |
| `import_country` | Import Country | | |
| `odometer_at_import` | Odometer at Import | km | |
| `previous_foreign_plate` | Previous Foreign Plate | | |
| `num_cylinders` | Number of Cylinders | | |
| `displacement_cc` | Engine Displacement | cm³ | |
| `engine_code` | Engine Code | | |
| `engine_working_principle` | Engine Working Principle | | ✅ |
| `cylinder_arrangement` | Cylinder Arrangement | | |
| `supercharged` | Supercharged (Turbo) | | |
| `catalytic_converter` | Catalytic Converter | | |
| `motor_fuel_type` | Motor Fuel Type | | ✅ |
| `engine_power_kw` | Engine Power | kW | ✅ |
| `max_power_at_rpm` | Max Power at RPM | rpm | |
| `max_rpm` | Max RPM | rpm | |
| `voltage` | Voltage | V | |
| `gearbox_type` | Gearbox Type | | |
| `num_gears` | Number of Gears | | |
| `num_reverse_gears` | Number of Reverse Gears | | |
| `hybrid_electric_vehicle` | Hybrid Electric Vehicle | | |
| `hybrid_category` | Hybrid Category | | |
| `exclusively_electric_drive` | Exclusively Electric Drive | | |
| `max_speed` | Max Speed | km/h | |
| `max_speed_measured` | Max Speed (Measured) | km/h | |
| `obd_equipped` | OBD Equipped | | |
| `curb_weight` | Curb Weight | kg | |
| `curb_weight_min` | Curb Weight (Min) | kg | |
| `curb_weight_max` | Curb Weight (Max) | kg | |
| `gross_weight` | Permitted Total Weight | kg | |
| `technical_gross_weight` | Technical Total Weight | kg | |
| `technical_gross_weight_road` | Technical Total Weight (Road) | kg | |
| `payload` | Payload | kg | ✅ |
| `trailer_weight_braked` | Trailer Weight (Braked) | kg | ✅ |
| `trailer_weight_unbraked` | Trailer Weight (Unbraked) | kg | ✅ |
| `roof_load` | Permitted Roof Load | kg | |
| `vertical_coupling_load` | Vertical Coupling Load | kg | |
| `train_weight` | Permitted Train Weight | kg | |
| `train_weight_road` | Permitted Train Weight (Road) | kg | |
| `length_mm` | Length | mm | ✅ |
| `width_mm` | Width | mm | ✅ |
| `height_mm` | Height | mm | ✅ |
| `num_seats` | Number of Seats | | ✅ |
| `front_seats` | Front Seats | | ✅ |
| `standing_places` | Standing Places | | |
| `wheelchair_places` | Wheelchair Places | | |
| `fuel_type` | Fuel Type | | ✅ |
| `euro_class` | Euro Emission Class | | |
| `eco_innovation` | Eco Innovation | | |
| `nedc_co2_combined` | CO₂ Combined (NEDC) | g/km | |
| `nedc_co2_city` | CO₂ City (NEDC) | g/km | |
| `nedc_co2_highway` | CO₂ Highway (NEDC) | g/km | |
| `nedc_fuel_combined` | Fuel Consumption Combined (NEDC) | l/100km | |
| `nedc_fuel_city` | Fuel Consumption City (NEDC) | l/100km | |
| `nedc_fuel_highway` | Fuel Consumption Highway (NEDC) | l/100km | |
| `nox_mg_per_km` | NOx Emissions | mg/km | |
| `particles_mg_per_km` | Particle Emissions | mg/km | |
| `nedc_electric_range` | Electric Range (NEDC) | km | |
| `nedc_el_energy_consumption` | El. Energy Consumption (NEDC) | Wh/km | |
| `particle_filter_factory` | Particle Filter (Factory-fitted) | | |
| `wltp_co2_combined` | CO₂ Combined (WLTP) | g/km | |
| `wltp_co2_low` | CO₂ Low (WLTP) | g/km | |
| `wltp_co2_medium` | CO₂ Medium (WLTP) | g/km | |
| `wltp_co2_high` | CO₂ High (WLTP) | g/km | |
| `wltp_co2_extra_high` | CO₂ Extra High (WLTP) | g/km | |
| `wltp_co2_weighted_combined` | CO₂ Weighted Combined (WLTP) | g/km | |
| `wltp_fuel_combined` | Fuel Consumption Combined (WLTP) | l/100km | |
| `wltp_fuel_low` | Fuel Consumption Low (WLTP) | l/100km | |
| `wltp_fuel_high` | Fuel Consumption High (WLTP) | l/100km | |
| `wltp_fuel_weighted_combined` | Fuel Consumption Weighted Combined (WLTP) | l/100km | |
| `wltp_electric_range_mixed` | Electric Range Mixed (WLTP) | km | |
| `wltp_electric_range_city` | Electric Range City (WLTP) | km | |
| `wltp_el_energy_consumption` | El. Energy Consumption (WLTP) | Wh/km | |
| `noise_driving` | Driving Noise | dB | |
| `noise_stationary` | Stationary Noise | dB | |
| `noise_interior` | Interior Noise | dB | |
| `abs` | ABS | | |
| `brake_system` | Brake System | | |
| `num_axles` | Number of Axles | | |
| `next_inspection_date` | Next Inspection Date | | ✅ |
| `last_inspection_date` | Last Inspection Date | | |
| `vehicle_remarks` | Vehicle Remarks | | |

</details>

---

## Troubleshooting

### Common issues

| Problem | Solution |
|---|---|
| `invalid_auth` during setup | Verify your API key. Keys can be revoked or expire. |
| `not_found` status | The registration number doesn't exist or is in the wrong format. |
| `connection_error` | Check your Home Assistant's internet connectivity. |
| Sensors show `None` | The field may not exist for that vehicle type (e.g., electric cars have no cylinder count). Enable the **Raw Response** diagnostic entity and inspect the JSON. |
| Sensors missing | Most sensors are disabled by default. Go to the device page and enable the ones you need. |

### Testing with curl

You can test your API key and a registration number directly:

```bash
curl -s \
  -H "Accept: application/json" \
  -H "SVV-Authorization: Apikey YOUR_API_KEY_HERE" \
  "https://www.vegvesen.no/ws/no/vegvesen/kjoretoy/felles/datautlevering/enkeltoppslag/kjoretoydata?kjennemerke=EF56000" \
  | python3 -m json.tool
```

Replace `YOUR_API_KEY_HERE` with your actual key and `EF56000` with a valid registration number.

### Enabling debug logging

Add to your `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.vegvesen_vehicle_lookup: debug
```

---

## API Reference

- **Endpoint**: `https://www.vegvesen.no/ws/no/vegvesen/kjoretoy/felles/datautlevering/enkeltoppslag/kjoretoydata`
- **Method**: GET
- **Query parameter**: `kjennemerke` (registration number)
- **Headers**:
  - `Accept: application/json`
  - `SVV-Authorization: Apikey {your_key}`
- **Documentation**: <https://autosys-kjoretoy-api.atlas.vegvesen.no/api-ui/index-enkeltoppslag.html>
- **OpenAPI spec**: <https://akfell-datautlevering.atlas.vegvesen.no/v3/api-docs/Default>

---

## License

This project is provided as-is under the [MIT License](LICENSE).
