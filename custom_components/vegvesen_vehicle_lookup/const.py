"""Constants for the Vegvesen Vehicle Lookup integration."""

from __future__ import annotations

from dataclasses import dataclass

DOMAIN = "vegvesen_vehicle_lookup"

# Configuration
CONF_API_KEY = "api_key"

# API
API_BASE_URL = (
    "https://www.vegvesen.no/ws/no/vegvesen/kjoretoy/felles/"
    "datautlevering/enkeltoppslag/kjoretoydata"
)
API_TIMEOUT = 30

# Registration number validation (2 letters + 5 digits)
REGNR_PATTERN = r"^[A-Za-z]{2}\d{5}$"

# Defaults
DEFAULT_DEBOUNCE_SECONDS = 15
DEFAULT_FALLBACK_LOOKUP_SECONDS = 60

# Options keys
CONF_DEBOUNCE_SECONDS = "debounce_seconds"
CONF_FALLBACK_LOOKUP_SECONDS = "fallback_lookup_seconds"

# Platforms
PLATFORMS: list[str] = ["text", "button", "sensor"]

# Service
SERVICE_LOOKUP = "lookup"
ATTR_REGNR = "regnr"


def safe_get(data: dict | list | None, *path, default=None):
    """Safely navigate a nested dict/list structure.

    Args:
        data: The root dict or list.
        *path: Keys (str for dict) or indices (int for list) to follow.
        default: Value to return if the path is not reachable.

    Returns:
        The value at the end of the path, or default if any step fails.
    """
    current = data
    for key in path:
        if current is None:
            return default
        if isinstance(key, int):
            if isinstance(current, (list, tuple)) and len(current) > key:
                current = current[key]
            else:
                return default
        elif isinstance(current, dict):
            current = current.get(key)
        else:
            return default
    return current if current is not None else default


@dataclass(frozen=True)
class AttributeDefinition:
    """Definition of a supported vehicle attribute."""

    name: str
    path: tuple
    icon: str
    unit: str | None = None
    enabled_default: bool = True


# ---------------------------------------------------------------------------
# Complete attribute list with JSON paths from the Vegvesen API (OpenAPI spec).
#
# Paths reference fields within a single vehicle object obtained from
# KjoretoydataResponse.kjoretoydataListe[0].
#
# All access MUST use safe_get() to handle missing or changed fields.
#
# enabled_default=True  → entity enabled by default in HA
# enabled_default=False → entity exists but disabled; user enables via UI
# ---------------------------------------------------------------------------

# Shorthand path prefixes (not exported – used to build tuples below)
_TD = ("godkjenning", "tekniskGodkjenning", "tekniskeData")
_GEN = (*_TD, "generelt")
_KAR = (*_TD, "karosseriOgLasteplan")
_KCL = ("godkjenning", "tekniskGodkjenning", "kjoretoyklassifisering")
_FG = ("godkjenning", "forstegangsGodkjenning")
_MOD = (*_TD, "motorOgDrivverk")
_MOT = (*_MOD, "motor", 0)
_DRV = (*_MOT, "drivstoff", 0)
_VEK = (*_TD, "vekter")
_DIM = (*_TD, "dimensjoner")
_PER = (*_TD, "persontall")
_MIL = (*_TD, "miljodata")
_MG = (*_MIL, "miljoOgdrivstoffGruppe", 0)
_FOU = (*_MG, "forbrukOgUtslipp", 0)
_WLTP = (*_FOU, "wltpKjoretoyspesifikk")
_LYD = (*_MG, "lyd")
_BRE = (*_TD, "bremser")
_AKS = (*_TD, "akslinger")

SUPPORTED_ATTRIBUTES: dict[str, AttributeDefinition] = {
    # ══ 1–2: Identity ════════════════════════════════════════════════════
    "registration_number": AttributeDefinition(
        name="Registration Number",
        path=("kjoretoyId", "kjennemerke"),
        icon="mdi:card-text",
    ),
    "chassis_number": AttributeDefinition(
        name="Chassis Number (VIN)",
        path=("kjoretoyId", "understellsnummer"),
        icon="mdi:identifier",
    ),
    # ══ 3–13: General / Description ══════════════════════════════════════
    "make": AttributeDefinition(
        name="Make",
        path=(*_GEN, "merke", 0, "merke"),
        icon="mdi:car",
    ),
    "make_code": AttributeDefinition(
        name="Make Code",
        path=(*_GEN, "merke", 0, "merkeKode"),
        icon="mdi:barcode",
        enabled_default=False,
    ),
    "model": AttributeDefinition(
        name="Model",
        path=(*_GEN, "handelsbetegnelse", 0),
        icon="mdi:car-info",
    ),
    "type_designation": AttributeDefinition(
        name="Type Designation",
        path=(*_GEN, "typebetegnelse"),
        icon="mdi:tag",
        enabled_default=False,
    ),
    "manufacturer_name": AttributeDefinition(
        name="Manufacturer Name",
        path=(*_GEN, "fabrikant", 0, "fabrikantNavn"),
        icon="mdi:factory",
        enabled_default=False,
    ),
    "color": AttributeDefinition(
        name="Color",
        path=(*_KAR, "rFarge", 0, "kodeNavn"),
        icon="mdi:palette",
    ),
    "body_type": AttributeDefinition(
        name="Body Type",
        path=(*_KAR, "karosseritype", "kodeNavn"),
        icon="mdi:car-side",
    ),
    "body_art": AttributeDefinition(
        name="Body Art",
        path=(*_KAR, "karosseriArt"),
        icon="mdi:car-side",
        enabled_default=False,
    ),
    "steering_side": AttributeDefinition(
        name="Steering Side",
        path=(*_KAR, "kjoringSide"),
        icon="mdi:steering",
    ),
    "num_doors": AttributeDefinition(
        name="Number of Doors",
        path=(*_KAR, "antallDorer", 0),
        icon="mdi:car-door",
    ),
    "bus_category": AttributeDefinition(
        name="Bus Category",
        path=(*_KAR, "bussKategori"),
        icon="mdi:bus",
        enabled_default=False,
    ),
    # ══ 14–20: Classification ════════════════════════════════════════════
    "vehicle_group": AttributeDefinition(
        name="Vehicle Group",
        path=(*_KCL, "beskrivelse"),
        icon="mdi:shape",
    ),
    "vehicle_category_code": AttributeDefinition(
        name="Vehicle Category Code",
        path=(*_KCL, "tekniskKode", "kodeVerdi"),
        icon="mdi:code-tags",
        enabled_default=False,
    ),
    "vehicle_subcategory_code": AttributeDefinition(
        name="Vehicle Subcategory Code",
        path=(*_KCL, "tekniskUnderkode", "kodeVerdi"),
        icon="mdi:code-tags",
        enabled_default=False,
    ),
    "vehicle_tax_code": AttributeDefinition(
        name="Vehicle Tax Code",
        path=(*_KCL, "kjoretoyAvgiftsKode", "kodeVerdi"),
        icon="mdi:cash",
        enabled_default=False,
    ),
    "special_characteristics": AttributeDefinition(
        name="Special Characteristics",
        path=(*_KCL, "spesielleKjennetegn"),
        icon="mdi:star",
        enabled_default=False,
    ),
    "type_approval_conformity": AttributeDefinition(
        name="Type Approval Conformity",
        path=(*_KCL, "iSamsvarMedTypegodkjenning"),
        icon="mdi:check-decagram",
        enabled_default=False,
    ),
    "ef_type_approval_number": AttributeDefinition(
        name="EF Type Approval Number",
        path=(*_KCL, "efTypegodkjenning", "typegodkjenningNrTekst"),
        icon="mdi:certificate",
        enabled_default=False,
    ),
    # ══ 21–26: Registration & Status ═════════════════════════════════════
    "registration_status": AttributeDefinition(
        name="Registration Status",
        path=("registrering", "registreringsstatus", "kodeNavn"),
        icon="mdi:check-circle",
    ),
    "first_registration_date": AttributeDefinition(
        name="First Registration Date",
        path=("forstegangsregistrering", "registrertForstegangNorgeDato"),
        icon="mdi:calendar",
    ),
    "first_technical_approval_date": AttributeDefinition(
        name="First Technical Approval Date",
        path=(*_FG, "forstegangRegistrertDato"),
        icon="mdi:calendar-check",
        enabled_default=False,
    ),
    "driving_purpose": AttributeDefinition(
        name="Driving Purpose",
        path=("registrering", "kjoringensArt", "kodeNavn"),
        icon="mdi:road-variant",
        enabled_default=False,
    ),
    "industry_code_description": AttributeDefinition(
        name="Industry Code Description",
        path=("registrering", "neringskodeBeskrivelse"),
        icon="mdi:domain",
        enabled_default=False,
    ),
    "deregistered_since_date": AttributeDefinition(
        name="Deregistered Since Date",
        path=("registrering", "avregistrertSidenDato"),
        icon="mdi:calendar-remove",
        enabled_default=False,
    ),
    # ══ 27–29: Import ════════════════════════════════════════════════════
    "import_country": AttributeDefinition(
        name="Import Country",
        path=(*_FG, "bruktimport", "importland", "landNavn"),
        icon="mdi:earth",
        enabled_default=False,
    ),
    "odometer_at_import": AttributeDefinition(
        name="Odometer at Import",
        path=(*_FG, "bruktimport", "kilometerstand"),
        icon="mdi:counter",
        unit="km",
        enabled_default=False,
    ),
    "previous_foreign_plate": AttributeDefinition(
        name="Previous Foreign Plate",
        path=(*_FG, "bruktimport", "tidligereUtenlandskKjennemerke"),
        icon="mdi:card-text-outline",
        enabled_default=False,
    ),
    # ══ 30–50: Engine & Drivetrain ═══════════════════════════════════════
    "num_cylinders": AttributeDefinition(
        name="Number of Cylinders",
        path=(*_MOT, "antallSylindre"),
        icon="mdi:numeric",
        enabled_default=False,
    ),
    "displacement_cc": AttributeDefinition(
        name="Engine Displacement",
        path=(*_MOT, "slagvolum"),
        icon="mdi:engine-outline",
        unit="cm³",
        enabled_default=False,
    ),
    "engine_code": AttributeDefinition(
        name="Engine Code",
        path=(*_MOT, "motorKode"),
        icon="mdi:engine",
        enabled_default=False,
    ),
    "engine_working_principle": AttributeDefinition(
        name="Engine Working Principle",
        path=(*_MOT, "arbeidsprinsipp", "kodeNavn"),
        icon="mdi:engine",
    ),
    "cylinder_arrangement": AttributeDefinition(
        name="Cylinder Arrangement",
        path=(*_MOT, "sylinderArrangement", "kodeNavn"),
        icon="mdi:cylinder",
        enabled_default=False,
    ),
    "supercharged": AttributeDefinition(
        name="Supercharged (Turbo)",
        path=(*_MOT, "overladet"),
        icon="mdi:turbine",
        enabled_default=False,
    ),
    "catalytic_converter": AttributeDefinition(
        name="Catalytic Converter",
        path=(*_MOT, "katalysator"),
        icon="mdi:filter",
        enabled_default=False,
    ),
    "motor_fuel_type": AttributeDefinition(
        name="Motor Fuel Type",
        path=(*_DRV, "drivstoffKode", "kodeNavn"),
        icon="mdi:fuel",
    ),
    "engine_power_kw": AttributeDefinition(
        name="Engine Power",
        path=(*_DRV, "maksNettoEffekt"),
        icon="mdi:flash",
        unit="kW",
    ),
    "max_power_at_rpm": AttributeDefinition(
        name="Max Power at RPM",
        path=(*_DRV, "maksNettoEffektVedOmdreiningstallMin1"),
        icon="mdi:gauge",
        unit="rpm",
        enabled_default=False,
    ),
    "max_rpm": AttributeDefinition(
        name="Max RPM",
        path=(*_DRV, "maksOmdreining"),
        icon="mdi:gauge",
        unit="rpm",
        enabled_default=False,
    ),
    "voltage": AttributeDefinition(
        name="Voltage",
        path=(*_DRV, "spenning"),
        icon="mdi:lightning-bolt",
        unit="V",
        enabled_default=False,
    ),
    "gearbox_type": AttributeDefinition(
        name="Gearbox Type",
        path=(*_MOD, "girkassetype", "kodeNavn"),
        icon="mdi:car-shift-pattern",
        enabled_default=False,
    ),
    "num_gears": AttributeDefinition(
        name="Number of Gears",
        path=(*_MOD, "antallGir"),
        icon="mdi:numeric",
        enabled_default=False,
    ),
    "num_reverse_gears": AttributeDefinition(
        name="Number of Reverse Gears",
        path=(*_MOD, "antallGirBakover"),
        icon="mdi:numeric",
        enabled_default=False,
    ),
    "hybrid_electric_vehicle": AttributeDefinition(
        name="Hybrid Electric Vehicle",
        path=(*_MOD, "hybridElektriskKjoretoy"),
        icon="mdi:car-electric",
        enabled_default=False,
    ),
    "hybrid_category": AttributeDefinition(
        name="Hybrid Category",
        path=(*_MOD, "hybridKategori", "kodeNavn"),
        icon="mdi:car-electric",
        enabled_default=False,
    ),
    "exclusively_electric_drive": AttributeDefinition(
        name="Exclusively Electric Drive",
        path=(*_MOD, "utelukkendeElektriskDrift"),
        icon="mdi:ev-station",
        enabled_default=False,
    ),
    "max_speed": AttributeDefinition(
        name="Max Speed",
        path=(*_MOD, "maksimumHastighet", 0),
        icon="mdi:speedometer",
        unit="km/h",
        enabled_default=False,
    ),
    "max_speed_measured": AttributeDefinition(
        name="Max Speed (Measured)",
        path=(*_MOD, "maksimumHastighetMalt", 0),
        icon="mdi:speedometer",
        unit="km/h",
        enabled_default=False,
    ),
    "obd_equipped": AttributeDefinition(
        name="OBD Equipped",
        path=(*_MOD, "obd"),
        icon="mdi:car-wrench",
        enabled_default=False,
    ),
    # ══ 51–63: Weights ═══════════════════════════════════════════════════
    "curb_weight": AttributeDefinition(
        name="Curb Weight",
        path=(*_VEK, "egenvekt"),
        icon="mdi:weight-kilogram",
        unit="kg",
        enabled_default=False,
    ),
    "curb_weight_min": AttributeDefinition(
        name="Curb Weight (Min)",
        path=(*_VEK, "egenvektMinimum"),
        icon="mdi:weight-kilogram",
        unit="kg",
        enabled_default=False,
    ),
    "curb_weight_max": AttributeDefinition(
        name="Curb Weight (Max)",
        path=(*_VEK, "egenvektMaksimum"),
        icon="mdi:weight-kilogram",
        unit="kg",
        enabled_default=False,
    ),
    "gross_weight": AttributeDefinition(
        name="Permitted Total Weight",
        path=(*_VEK, "tillattTotalvekt"),
        icon="mdi:weight-kilogram",
        unit="kg",
        enabled_default=False,
    ),
    "technical_gross_weight": AttributeDefinition(
        name="Technical Total Weight",
        path=(*_VEK, "tekniskTillattTotalvekt"),
        icon="mdi:weight-kilogram",
        unit="kg",
        enabled_default=False,
    ),
    "technical_gross_weight_road": AttributeDefinition(
        name="Technical Total Weight (Road)",
        path=(*_VEK, "tekniskTillattTotalvektVeg"),
        icon="mdi:weight-kilogram",
        unit="kg",
        enabled_default=False,
    ),
    "payload": AttributeDefinition(
        name="Payload",
        path=(*_VEK, "nyttelast"),
        icon="mdi:weight-kilogram",
        unit="kg",
    ),
    "trailer_weight_braked": AttributeDefinition(
        name="Trailer Weight (Braked)",
        path=(*_VEK, "tillattTilhengervektMedBrems"),
        icon="mdi:tow-truck",
        unit="kg",
    ),
    "trailer_weight_unbraked": AttributeDefinition(
        name="Trailer Weight (Unbraked)",
        path=(*_VEK, "tillattTilhengervektUtenBrems"),
        icon="mdi:tow-truck",
        unit="kg",
    ),
    "roof_load": AttributeDefinition(
        name="Permitted Roof Load",
        path=(*_VEK, "tillattTaklast"),
        icon="mdi:arrow-up-box",
        unit="kg",
        enabled_default=False,
    ),
    "vertical_coupling_load": AttributeDefinition(
        name="Vertical Coupling Load",
        path=(*_VEK, "tillattVertikalKoplingslast"),
        icon="mdi:arrow-down-box",
        unit="kg",
        enabled_default=False,
    ),
    "train_weight": AttributeDefinition(
        name="Permitted Train Weight",
        path=(*_VEK, "tillattVogntogvekt"),
        icon="mdi:train-car",
        unit="kg",
        enabled_default=False,
    ),
    "train_weight_road": AttributeDefinition(
        name="Permitted Train Weight (Road)",
        path=(*_VEK, "tillattVogntogvektVeg"),
        icon="mdi:train-car",
        unit="kg",
        enabled_default=False,
    ),
    # ══ 64–66: Dimensions ════════════════════════════════════════════════
    "length_mm": AttributeDefinition(
        name="Length",
        path=(*_DIM, "lengde"),
        icon="mdi:ruler",
        unit="mm",
    ),
    "width_mm": AttributeDefinition(
        name="Width",
        path=(*_DIM, "bredde"),
        icon="mdi:ruler",
        unit="mm",
    ),
    "height_mm": AttributeDefinition(
        name="Height",
        path=(*_DIM, "hoyde"),
        icon="mdi:ruler",
        unit="mm",
    ),
    # ══ 67–70: Persons / Seats ═══════════════════════════════════════════
    "num_seats": AttributeDefinition(
        name="Number of Seats",
        path=(*_PER, "sitteplasserTotalt"),
        icon="mdi:car-seat",
    ),
    "front_seats": AttributeDefinition(
        name="Front Seats",
        path=(*_PER, "sitteplasserForan"),
        icon="mdi:car-seat",
    ),
    "standing_places": AttributeDefinition(
        name="Standing Places",
        path=(*_PER, "staplasser"),
        icon="mdi:human-handsup",
        enabled_default=False,
    ),
    "wheelchair_places": AttributeDefinition(
        name="Wheelchair Places",
        path=(*_PER, "rullestolplasser"),
        icon="mdi:wheelchair-accessibility",
        enabled_default=False,
    ),
    # ══ 71–73: Environment & Fuel ════════════════════════════════════════
    "fuel_type": AttributeDefinition(
        name="Fuel Type",
        path=(*_MG, "drivstoffKodeMiljodata", "kodeNavn"),
        icon="mdi:fuel",
    ),
    "euro_class": AttributeDefinition(
        name="Euro Emission Class",
        path=(*_MIL, "euroKlasse", "kodeNavn"),
        icon="mdi:leaf",
        enabled_default=False,
    ),
    "eco_innovation": AttributeDefinition(
        name="Eco Innovation",
        path=(*_MIL, "okoInnovasjon"),
        icon="mdi:leaf-circle",
        enabled_default=False,
    ),
    # ══ 74–84: Emissions & Consumption (NEDC) ════════════════════════════
    "nedc_co2_combined": AttributeDefinition(
        name="CO₂ Combined (NEDC)",
        path=(*_FOU, "co2BlandetKjoring"),
        icon="mdi:molecule-co2",
        unit="g/km",
        enabled_default=False,
    ),
    "nedc_co2_city": AttributeDefinition(
        name="CO₂ City (NEDC)",
        path=(*_FOU, "co2Bykjoring"),
        icon="mdi:molecule-co2",
        unit="g/km",
        enabled_default=False,
    ),
    "nedc_co2_highway": AttributeDefinition(
        name="CO₂ Highway (NEDC)",
        path=(*_FOU, "co2Landeveiskjoring"),
        icon="mdi:molecule-co2",
        unit="g/km",
        enabled_default=False,
    ),
    "nedc_fuel_combined": AttributeDefinition(
        name="Fuel Consumption Combined (NEDC)",
        path=(*_FOU, "forbrukBlandetKjoring"),
        icon="mdi:gas-station",
        unit="l/100km",
        enabled_default=False,
    ),
    "nedc_fuel_city": AttributeDefinition(
        name="Fuel Consumption City (NEDC)",
        path=(*_FOU, "forbrukBykjoring"),
        icon="mdi:gas-station",
        unit="l/100km",
        enabled_default=False,
    ),
    "nedc_fuel_highway": AttributeDefinition(
        name="Fuel Consumption Highway (NEDC)",
        path=(*_FOU, "forbrukLandeveiskjoring"),
        icon="mdi:gas-station",
        unit="l/100km",
        enabled_default=False,
    ),
    "nox_mg_per_km": AttributeDefinition(
        name="NOx Emissions",
        path=(*_FOU, "utslippNOxMgPrKm"),
        icon="mdi:smog",
        unit="mg/km",
        enabled_default=False,
    ),
    "particles_mg_per_km": AttributeDefinition(
        name="Particle Emissions",
        path=(*_FOU, "utslippPartiklerMgPrKm"),
        icon="mdi:blur",
        unit="mg/km",
        enabled_default=False,
    ),
    "nedc_electric_range": AttributeDefinition(
        name="Electric Range (NEDC)",
        path=(*_FOU, "rekkeviddeKm"),
        icon="mdi:ev-station",
        unit="km",
        enabled_default=False,
    ),
    "nedc_el_energy_consumption": AttributeDefinition(
        name="El. Energy Consumption (NEDC)",
        path=(*_FOU, "elEnergiforbruk"),
        icon="mdi:lightning-bolt",
        unit="Wh/km",
        enabled_default=False,
    ),
    "particle_filter_factory": AttributeDefinition(
        name="Particle Filter (Factory-fitted)",
        path=(*_FOU, "partikkelfilterFabrikkmontert"),
        icon="mdi:filter",
        enabled_default=False,
    ),
    # ══ 85–97: Emissions & Consumption (WLTP) ════════════════════════════
    "wltp_co2_combined": AttributeDefinition(
        name="CO₂ Combined (WLTP)",
        path=(*_WLTP, "co2Kombinert"),
        icon="mdi:molecule-co2",
        unit="g/km",
        enabled_default=False,
    ),
    "wltp_co2_low": AttributeDefinition(
        name="CO₂ Low (WLTP)",
        path=(*_WLTP, "co2Lav"),
        icon="mdi:molecule-co2",
        unit="g/km",
        enabled_default=False,
    ),
    "wltp_co2_medium": AttributeDefinition(
        name="CO₂ Medium (WLTP)",
        path=(*_WLTP, "co2Middels"),
        icon="mdi:molecule-co2",
        unit="g/km",
        enabled_default=False,
    ),
    "wltp_co2_high": AttributeDefinition(
        name="CO₂ High (WLTP)",
        path=(*_WLTP, "co2Hoy"),
        icon="mdi:molecule-co2",
        unit="g/km",
        enabled_default=False,
    ),
    "wltp_co2_extra_high": AttributeDefinition(
        name="CO₂ Extra High (WLTP)",
        path=(*_WLTP, "co2EkstraHoy"),
        icon="mdi:molecule-co2",
        unit="g/km",
        enabled_default=False,
    ),
    "wltp_co2_weighted_combined": AttributeDefinition(
        name="CO₂ Weighted Combined (WLTP)",
        path=(*_WLTP, "co2VektetKombinert"),
        icon="mdi:molecule-co2",
        unit="g/km",
        enabled_default=False,
    ),
    "wltp_fuel_combined": AttributeDefinition(
        name="Fuel Consumption Combined (WLTP)",
        path=(*_WLTP, "forbrukKombinert"),
        icon="mdi:gas-station",
        unit="l/100km",
        enabled_default=False,
    ),
    "wltp_fuel_low": AttributeDefinition(
        name="Fuel Consumption Low (WLTP)",
        path=(*_WLTP, "forbrukLav"),
        icon="mdi:gas-station",
        unit="l/100km",
        enabled_default=False,
    ),
    "wltp_fuel_high": AttributeDefinition(
        name="Fuel Consumption High (WLTP)",
        path=(*_WLTP, "forbrukHoy"),
        icon="mdi:gas-station",
        unit="l/100km",
        enabled_default=False,
    ),
    "wltp_fuel_weighted_combined": AttributeDefinition(
        name="Fuel Consumption Weighted Combined (WLTP)",
        path=(*_WLTP, "forbrukVektetKombinert"),
        icon="mdi:gas-station",
        unit="l/100km",
        enabled_default=False,
    ),
    "wltp_electric_range_mixed": AttributeDefinition(
        name="Electric Range Mixed (WLTP)",
        path=(*_WLTP, "rekkeviddeKmBlandetkjoring"),
        icon="mdi:ev-station",
        unit="km",
        enabled_default=False,
    ),
    "wltp_electric_range_city": AttributeDefinition(
        name="Electric Range City (WLTP)",
        path=(*_WLTP, "rekkeviddeKmBykjoring"),
        icon="mdi:ev-station",
        unit="km",
        enabled_default=False,
    ),
    "wltp_el_energy_consumption": AttributeDefinition(
        name="El. Energy Consumption (WLTP)",
        path=(*_WLTP, "elEnergiforbruk"),
        icon="mdi:lightning-bolt",
        unit="Wh/km",
        enabled_default=False,
    ),
    # ══ 98–100: Noise ════════════════════════════════════════════════════
    "noise_driving": AttributeDefinition(
        name="Driving Noise",
        path=(*_LYD, "kjorestoy"),
        icon="mdi:volume-high",
        unit="dB",
        enabled_default=False,
    ),
    "noise_stationary": AttributeDefinition(
        name="Stationary Noise",
        path=(*_LYD, "standstoy"),
        icon="mdi:volume-medium",
        unit="dB",
        enabled_default=False,
    ),
    "noise_interior": AttributeDefinition(
        name="Interior Noise",
        path=(*_LYD, "innvendigStoyniva"),
        icon="mdi:volume-low",
        unit="dB",
        enabled_default=False,
    ),
    # ══ 101–103: Brakes & Axles ══════════════════════════════════════════
    "abs": AttributeDefinition(
        name="ABS",
        path=(*_BRE, "abs"),
        icon="mdi:car-brake-abs",
        enabled_default=False,
    ),
    "brake_system": AttributeDefinition(
        name="Brake System",
        path=(*_BRE, "bremsesystem"),
        icon="mdi:car-brake-alert",
        enabled_default=False,
    ),
    "num_axles": AttributeDefinition(
        name="Number of Axles",
        path=(*_AKS, "antallAksler"),
        icon="mdi:axes",
        enabled_default=False,
    ),
    # ══ 104–105: Periodic Inspection ═════════════════════════════════════
    "next_inspection_date": AttributeDefinition(
        name="Next Inspection Date",
        path=("periodiskKjoretoyKontroll", "kontrollfrist"),
        icon="mdi:calendar-clock",
    ),
    "last_inspection_date": AttributeDefinition(
        name="Last Inspection Date",
        path=("periodiskKjoretoyKontroll", "sistGodkjent"),
        icon="mdi:calendar-check",
        enabled_default=False,
    ),
    # ══ 106: Remarks ═════════════════════════════════════════════════════
    "vehicle_remarks": AttributeDefinition(
        name="Vehicle Remarks",
        path=("godkjenning", "kjoretoymerknad", 0, "merknad"),
        icon="mdi:comment-text",
        enabled_default=False,
    ),
}
