from typing import Final

# 🔹 Mapping used to normalize team names across
# different external data sources (WhoScored, FIFA, Elo, etc.).
# Keys represent source-specific names and values represent
# the standardized names used during dataset merging.
NAME_MAPPING: Final[dict[str, str]] = {
    "IR Iran": "Iran",
    "Korea Republic": "South Korea",
    "Congo DR": "DR Congo",
    "Côte d'Ivoire": "Ivory Coast",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Türkiye": "Turkey",
}

# 🔹 Reverse mapping used when converting standardized team names
# back to the naming convention required by a specific source.
# This is commonly used for lookups, joins, and URL generation.
NAME_MAPPING2: Final[dict[str, str]] = {
    "Iran": "IR Iran",
    "Ivory Coast": "Côte d'Ivoire",
    "Bosnia and Herzegovina": "Bosnia-Herzegovina",
    "USA": "United States",
    "DR Congo": "Congo DR",
    "Curacao": "Curaçao",
    "Turkiye": "Türkiye",
    "South Korea": "Korea Republic",
}