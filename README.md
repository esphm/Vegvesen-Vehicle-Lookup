# 🚗 Vegvesen Vehicle Lookup - Custom Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Validate](https://github.com/esphm/Vegvesen-Vehicle-Lookup/actions/workflows/validate.yml/badge.svg)](https://github.com/esphm/Vegvesen-Vehicle-Lookup/actions/workflows/validate.yml)
[![GitHub release](https://img.shields.io/github/v/release/esphm/Vegvesen-Vehicle-Lookup)](https://github.com/esphm/Vegvesen-Vehicle-Lookup/releases)

A Home Assistant custom integration for looking up Norwegian vehicle technical data from [Statens vegvesen](https://www.vegvesen.no/) using the **Autosys enkeltoppslag** API.

Enter a registration number → get 106 vehicle attributes as sensor entities.

---

## ✨ Features

- **106 vehicle attributes** — make, model, fuel type, engine specs, weights, dimensions, CO₂/WLTP/NEDC emissions, noise levels, inspection dates, and more
- **24 sensors enabled by default** — enable any of the remaining 82 from the HA entity UI
- **On-demand only** — no polling; lookups trigger on text input change, button press, service call, or HA restart
- **Smart debounce** — configurable delay with fallback timeout for rapid edits
- **Diagnostic sensors** — lookup status, timestamp, and raw JSON response

## ⚠️ Limitations

- Only **technical vehicle data** is returned — no owner information
- Registration number validation expects `2 letters + 5 digits` (e.g. `AB12345` or `AB 12345`)
- API rate limit: **50,000 calls/day** per key

---

## 📦 Installation

### HACS (recommended)

1. Open **HACS** → **Integrations** → ⋮ → **Custom repositories**
2. Add `https://github.com/esphm/Vegvesen-Vehicle-Lookup` as **Integration**
3. Install and restart Home Assistant

### Updating

HACS periodically checks the repository's published GitHub releases. When a newer
version is available, HACS shows an update for the integration. Install the update
in HACS and restart Home Assistant when prompted.

If an update does not appear immediately, open HACS, use ⋮ → **Update information**,
and check again. Git tags alone are not enough: a version must be published as a
GitHub release before HACS offers it to existing installations.

### Manual

Copy `custom_components/vegvesen_vehicle_lookup/` to your HA `config/custom_components/` and restart.

---

## ⚙️ Setup

1. **Settings** → **Devices & Services** → **Add Integration** → search **Vegvesen Vehicle Lookup**
2. Enter your Statens vegvesen API key ([apply here](https://www.vegvesen.no/dinside/data-og-api-er/tilgang-til-api-for-kjoretoyopplysninger/vis))
3. Optionally configure debounce timing under **Configure**:
   - `debounce_seconds` (default `15`) — delay before lookup after text change
   - `fallback_lookup_seconds` (default `60`) — max wait during rapid edits

---

## 🔍 Usage

1. Set the **Vehicle Registration Number** text entity to a registration number
2. Wait for the debounce timer, or press **Lookup Now**
3. Sensor entities populate with vehicle data

### Service call

```yaml
service: vegvesen_vehicle_lookup.lookup
data:
  regnr: "AB12345"
```

Omit `regnr` to use the currently entered registration number.

### Automation example

```yaml
automation:
  - alias: "Look up vehicle on NFC tag scan"
    trigger:
      - platform: tag
        tag_id: my_nfc_tag
    action:
      - service: vegvesen_vehicle_lookup.lookup
        data:
          regnr: "AB12345"
```

---

## 📊 Entities

| Entity | Type | Description |
|---|---|---|
| Vehicle Registration Number | `text` | Editable registration number input |
| Lookup Now | `button` | Trigger an immediate lookup |
| *(106 attribute sensors)* | `sensor` | See [full list](#-supported-attributes) below |
| Last Lookup Status | `sensor` | 🔧 Diagnostic — success / not_found / error |
| Last Updated | `sensor` | 🔧 Diagnostic — timestamp of last lookup |
| Raw Response | `sensor` | 🔧 Diagnostic — raw JSON (disabled by default) |

---

## 📋 Supported Attributes

106 attributes from the API. **24 enabled by default** (✅). Enable the rest from **Settings** → **Entities**.

<details>
<summary>Show all 106 attributes</summary>

| Key | Name | Unit | On |
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

## 🐛 Troubleshooting

| Problem | Solution |
|---|---|
| `invalid_auth` during setup | Verify your API key — it may have been revoked or expired |
| `not_found` status | Registration number doesn't exist or wrong format |
| `connection_error` | Check HA internet connectivity |
| Sensors show `None` | Field doesn't exist for this vehicle type (e.g. EVs have no cylinder count) |
| Sensors missing | Most are disabled by default — enable them from the device page |

<details>
<summary>🔧 Debug logging</summary>

```yaml
logger:
  default: warning
  logs:
    custom_components.vegvesen_vehicle_lookup: debug
```

</details>

<details>
<summary>🧪 Test with curl</summary>

```bash
curl -s \
  -H "Accept: application/json" \
  -H "SVV-Authorization: Apikey YOUR_API_KEY" \
  "https://www.vegvesen.no/ws/no/vegvesen/kjoretoy/felles/datautlevering/enkeltoppslag/kjoretoydata?kjennemerke=AB12345" \
  | python3 -m json.tool
```

</details>

---

## 📚 API Reference

| | |
|---|---|
| **Endpoint** | `https://www.vegvesen.no/ws/no/vegvesen/kjoretoy/felles/datautlevering/enkeltoppslag/kjoretoydata` |
| **Method** | GET |
| **Query param** | `kjennemerke` (registration number) |
| **Headers** | `Accept: application/json` · `SVV-Authorization: Apikey {key}` |
| **Docs** | [API UI](https://autosys-kjoretoy-api.atlas.vegvesen.no/api-ui/index-enkeltoppslag.html) · [OpenAPI spec](https://akfell-datautlevering.atlas.vegvesen.no/v3/api-docs/Default) |

---

## 📄 License

[MIT](LICENSE)
