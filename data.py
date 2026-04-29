# data.py
# ─────────────────────────────────────────────────────────────────────────────
# Single source of truth for all category and subcategory definitions.
#
# WHY its own file:
#   If you ever add a category, rename a subcategory, or change a color,
#   this is the ONLY file you touch. The UI and chart code never need to
#   know about those changes — they just read from this dictionary.
#
# HOW other files use this:
#   from data import CATEGORIES, CAT_NAMES
# ─────────────────────────────────────────────────────────────────────────────

CATEGORIES = {
    "WATER CONSERVATION": {
        "subcategories": [
            "Irrigation Scheduling",
            "Irrigation Audit",
            "Functional Turf Coverage",
            "Turfgrass Species & Management",
            "Non-Turfgrass Areas",
            "Other Water Conservation",
        ],
        "color": "#4285F4",
        "keys": [
            "IrrigationScheduling",
            "IrrigationAudit",
            "FunctionalTurfCoverage",
            "TurfgrassSpeciesManagement",
            "NonTurfgrassAreas",
            "OtherWaterConservation",
        ],
        "css_class": "cat-water",
    },
    "ECOSYSTEM SERVICES": {
        "subcategories": [
            "Soil Health",
            "Biodiversity & Biomass",
            "Invasive Plants",
            "Native Plants",
            "Urban Heat Reduction",
            "Wildlife & Pollinator Support",
        ],
        "color": "#2A9D8F",
        "keys": [
            "SoilHealth",
            "BiodiversityBiomass",
            "InvasivePlants",
            "NativePlants",
            "UrbanHeatReduction",
            "WildlifePollinatorSupport",
        ],
        "css_class": "cat-ecosystem",
    },
    "DESIGN AND MANAGEMENT": {
        "subcategories": [
            "Energy Consumption",
            "Light Pollution",
            "Responsible Waste Disposal",
            "Sustainable Care",
            "Physical & Social Wellbeing",
            "Mental Wellbeing",
        ],
        "color": "#E9C46A",
        "keys": [
            "EnergyConsumption",
            "LightPollution",
            "ResponsibleWasteDisposal",
            "SustainableCare",
            "PhysicalSocialWellbeing",
            "MentalWellbeing",
        ],
        "css_class": "cat-design",
    },
}

# CAT_NAMES is a convenience — lets other files iterate categories in order
# without having to call list(CATEGORIES.keys()) every time.
CAT_NAMES = list(CATEGORIES.keys())
