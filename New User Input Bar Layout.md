Hey champ, look at the rough outline below for settings and their arrangement/logic.

# Section 1
## Location Settings (header)
Lat (degrees)
Long (degrees)

# Section 2
## Use Case
(Dropdown option to change between them) Fixed (Small Scale) / Automobile / Fixed (Large Scale) / Mobile Generator

# Section 2.1 (If Fixed (Small Scale) selected)
## Fixed (Small Scale)
Single Array / Split Array (dropdown option to change between them)
(If single array selected):
    - Tilt Angle (deg)
    - Azimuth Angle (deg)

    Shading Obstructions (checkbox)
    (If shading obstructions checked):
        - Add Obstruction (this is the setting we already have)
        - Left Edge Azimuth (deg)
        - Right Edge Azimuth (deg)
        - Elevation Angle (deg)

    Turnkey Cost / Cost Breakdown (dropdown option to change between them)
    (If turnkey selected):
        - Turnkey Cost ($)
        - Installed Capacity (kW)
        - Years Since Installation (years)
        - Degradation Rate (%/yr)

    (If cost breakdown selected):
        - No. of Modules
        - Years Since Installation (years)
        - Degradation Rate (%/yr)
        - Module Unit Cost ($)
        - Module Capacity (W) (STC)
        - Module Efficiency (%) (STC)
        - Racking Cost ($)
        - Inverter Cost ($)
        - Balance of System (BOS) ($)
        - Labour Cost ($)

(If split array selected):
    - Add Array (this is the one we already have that has multiple arrays, each with their own tilt/az etc.)
    - Array 'n' Tilt Angle (deg)
    - Array 'n' Azimuth Angle (deg)

        Shading Obstructions (checkbox)
        (If shading obstructions checked):
            - Add Obstruction (this is the setting we already have)
            - Left Edge Azimuth (deg)
            - Right Edge Azimuth (deg)
            - Elevation Angle (deg)

        Turnkey Cost / Cost Breakdown (dropdown option to change between them)
        (If turnkey selected):
            - Turnkey Cost ($)
            - Installed Capacity (kW)
            - Years Since Installation (years)
            - Degradation Rate (%/yr)

        (If cost breakdown selected):
            - No. of Modules
            - Years Since Installation (years)
            - Degradation Rate (%/yr)
            - Module Unit Cost ($)
            - Module Capacity (W) (STC)
            - Module Efficiency (%) (STC)
            - Racking Cost ($)
            - Inverter Cost ($)
            - Balance of System (BOS) ($)
            - Labour Cost ($)


# Section 2.1.1
## Battery Electric Storage System (BESS)

# Section 2.1.2
## ICE Generator Backup

# Section 2.2 (If Automobile selected)
## Automobile

# Section 2.2.1
## Battery Electric Storage System (BESS)

# Section 2.2.2
## ICE Generator Backup

# Section 2.3 (If Fixed (Large Scale) selected)
## Fixed (Large Scale)

# Section 2.3.1
## Battery Electric Storage System (BESS)

# Section 2.3.2
## ICE Generator Backup

# Section 2.4 (If Mobile Generator selected)
## Mobile Generator

# Section 2.4.1
## Battery Electric Storage System (BESS)

# Section 2.4.2
## ICE Generator Backup

# Section 2.5 (If Mobile Generator selected)
## Mobile Generator

# Section 2.5.1
## Battery Electric Storage System (BESS)

# Section 2.5.2
## ICE Generator Backup

# Section 3
## Grid Import/Export Cost