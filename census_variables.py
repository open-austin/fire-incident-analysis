# Census variable definitions for ATX fire resource analysis

# B25034: Year structure built
YEAR_BUILT_VARS = {
    "B25034_001E": "Total",
    "B25034_002E": "Built 2020 or later",
    "B25034_003E": "Built 2010-2019",
    "B25034_004E": "Built 2000-2009",
    "B25034_005E": "Built 1990-1999",
    "B25034_006E": "Built 1980-1989",
    "B25034_007E": "Built 1970-1979",
    "B25034_008E": "Built 1960-1969",
    "B25034_009E": "Built 1950-1959",
    "B25034_010E": "Built 1940-1949",
    "B25034_011E": "Built 1939 or earlier",
    "NAME": "Census tract name"
}

# B25024: Housing units by type
HOUSING_VARS = {
    "B25024_001E": "Total",
    "B25024_002E": "1-unit, detached",
    "B25024_003E": "1-unit, attached",
    "B25024_004E": "2 units",
    "B25024_005E": "3-4 units",
    "B25024_006E": "5-9 units",
    "B25024_007E": "10-19 units",
    "B25024_008E": "20-49 units",
    "B25024_009E": "50 or more units",
    "B25024_010E": "Mobile home",
    "B25024_011E": "Boat, RV, van",
    "NAME": "Census tract name"
}

# B01003: Total population
POPULATION_VARS = {
    "B01003_001E": "Total population",
    "NAME": "Census tract name"
}

ALL_CENSUS_VARS = {
    **POPULATION_VARS,
    **HOUSING_VARS,
    **YEAR_BUILT_VARS
}
