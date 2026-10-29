"""
config.py — Single source of truth for the Manufacturing Defect Traceability
Synthetic Data Generator.

This module defines every parameter, constant, enum, and reference-data
lookup used by the generator scripts.  Nothing here has side effects; it is
safe to ``import config`` from any module.
"""

from datetime import datetime

# ---------------------------------------------------------------------------
# Global constants
# ---------------------------------------------------------------------------
DEFAULT_SEED: int = 20261022
YEAR: int = 2026
BASE_DATE: datetime = datetime(2026, 1, 1)
END_DATE: datetime = datetime(2026, 10, 28)

# ---------------------------------------------------------------------------
# Scale configurations (row counts per dataset size)
# ---------------------------------------------------------------------------
SCALES: dict = {
    "full": {
        "num_products": 200,
        "num_suppliers": 50,
        "num_material_lots": 2000,
        "num_production_orders": 5000,
        "num_inspection_results": 20000,
        "num_machines": 30,
        "num_inspection_plans_per_product": 2,   # average
        "anomaly_count_per_type": 5,
    },
    "small": {
        "num_products": 20,
        "num_suppliers": 10,
        "num_material_lots": 200,
        "num_production_orders": 500,
        "num_inspection_results": 2000,
        "num_machines": 10,
        "num_inspection_plans_per_product": 2,
        "anomaly_count_per_type": 2,
    },
}

# ---------------------------------------------------------------------------
# Product categories & names
# ---------------------------------------------------------------------------
PRODUCT_CATEGORIES: list[str] = [
    "Electronics Assembly",
    "Mechanical Component",
    "Hydraulic System",
    "Electrical Harness",
    "Plastic Molding",
    "Metal Fabrication",
    "PCB Assembly",
    "Sensor Module",
    "Pneumatic Valve",
    "Motor Assembly",
    "Heat Exchanger",
    "Control Panel",
    "Gear Box",
    "Bearing Assembly",
    "Pump Unit",
]

PRODUCT_NAMES: dict[str, list[str]] = {
    "Electronics Assembly": [
        "Main Control Board", "Power Supply Unit", "Signal Processor",
        "Display Module", "Communication Interface", "Sensor Array Board",
    ],
    "Mechanical Component": [
        "Drive Shaft", "Coupling Flange", "Mounting Bracket",
        "Housing Cover", "Support Frame", "Pivot Arm",
    ],
    "Hydraulic System": [
        "Hydraulic Cylinder", "Directional Control Valve", "Hydraulic Power Pack",
        "Accumulator Assembly", "Manifold Block", "Hydraulic Motor",
    ],
    "Electrical Harness": [
        "Main Wiring Harness", "Sensor Cable Assembly", "Power Distribution Harness",
        "Control Signal Harness", "Shielded Data Cable", "Battery Harness",
    ],
    "Plastic Molding": [
        "Enclosure Shell", "Connector Housing", "Fan Shroud",
        "Cable Gland Body", "Button Cap Set", "Light Pipe Array",
    ],
    "Metal Fabrication": [
        "Chassis Frame", "Mounting Plate", "Guard Panel",
        "Structural Beam", "Hinge Assembly", "Reinforcement Rib",
    ],
    "PCB Assembly": [
        "Motor Driver PCB", "I/O Interface Board", "LED Driver Board",
        "Power Regulator PCB", "Sensor Fusion Board", "Relay Control PCB",
    ],
    "Sensor Module": [
        "Temperature Sensor Module", "Pressure Transducer", "Proximity Sensor Unit",
        "Vibration Sensor Pack", "Load Cell Module", "Flow Meter Assembly",
    ],
    "Pneumatic Valve": [
        "Solenoid Valve 5/2", "Proportional Valve", "Check Valve Assembly",
        "Pressure Relief Valve", "Flow Control Valve", "Directional Spool Valve",
    ],
    "Motor Assembly": [
        "Brushless DC Motor", "Stepper Motor Unit", "Servo Motor Assembly",
        "Gear Motor Pack", "Linear Actuator", "AC Induction Motor",
    ],
    "Heat Exchanger": [
        "Plate Heat Exchanger", "Shell-and-Tube Exchanger", "Fin-Type Radiator",
        "Oil Cooler Unit", "Condenser Assembly", "Air-Cooled Heat Sink",
    ],
    "Control Panel": [
        "Main Control Panel", "Operator Interface Panel", "Remote I/O Panel",
        "Motor Control Center", "Power Distribution Panel", "Safety Relay Panel",
    ],
    "Gear Box": [
        "Planetary Gear Box", "Worm Gear Reducer", "Helical Gear Unit",
        "Bevel Gear Drive", "Cycloidal Reducer", "Spur Gear Train",
    ],
    "Bearing Assembly": [
        "Deep Groove Ball Bearing", "Tapered Roller Bearing", "Needle Bearing Unit",
        "Thrust Bearing Assembly", "Spherical Roller Bearing", "Linear Bearing Block",
    ],
    "Pump Unit": [
        "Centrifugal Pump", "Diaphragm Pump", "Gear Pump Assembly",
        "Peristaltic Pump", "Piston Pump Unit", "Vacuum Pump Module",
    ],
}

# ---------------------------------------------------------------------------
# Raw materials & units of measure
# ---------------------------------------------------------------------------
RAW_MATERIALS: list[str] = [
    "Steel Sheet (CR)", "Steel Sheet (HR)", "Aluminum Plate 6061",
    "Aluminum Extrusion", "Copper Wire AWG-18", "Copper Bus Bar",
    "Stainless Steel 304", "Stainless Steel 316", "Carbon Steel Rod",
    "Brass Tube", "Titanium Sheet", "Nylon 6/6 Pellets",
    "ABS Pellets", "Polycarbonate Resin", "HDPE Granules",
    "Silicone Rubber Compound", "Epoxy Resin", "Polyurethane Foam",
    "FR4 Laminate", "Solder Paste SAC305", "Flux Core Wire",
    "Thermal Paste", "Ceramic Substrate", "Ferrite Core",
    "Neodymium Magnet", "Capacitor (SMD)", "Resistor (SMD)",
    "IC Chip Package", "Connector Housing", "O-Ring (Viton)",
    "Gasket Material (PTFE)", "Bearing Ball (Chrome Steel)",
    "Spring Wire (Music Wire)", "Hydraulic Fluid ISO-46",
    "Lubricant Grease (Lithium)", "Adhesive (Cyanoacrylate)",
    "Paint Primer (Zinc)", "Powder Coat (RAL 7035)",
    "Anodize Solution", "Nickel Plating Solution",
]

MATERIAL_UNITS: dict[str, str] = {
    # Sheet / plate / bar metals — kilograms
    "Steel Sheet (CR)": "kg",
    "Steel Sheet (HR)": "kg",
    "Aluminum Plate 6061": "kg",
    "Aluminum Extrusion": "kg",
    "Stainless Steel 304": "kg",
    "Stainless Steel 316": "kg",
    "Carbon Steel Rod": "kg",
    "Brass Tube": "kg",
    "Titanium Sheet": "kg",
    # Wire — metres
    "Copper Wire AWG-18": "m",
    "Copper Bus Bar": "kg",
    "Flux Core Wire": "m",
    "Spring Wire (Music Wire)": "m",
    # Polymers / pellets — kilograms
    "Nylon 6/6 Pellets": "kg",
    "ABS Pellets": "kg",
    "Polycarbonate Resin": "kg",
    "HDPE Granules": "kg",
    "Silicone Rubber Compound": "kg",
    "Epoxy Resin": "kg",
    "Polyurethane Foam": "kg",
    # Board / substrate — pieces
    "FR4 Laminate": "pcs",
    "Ceramic Substrate": "pcs",
    # Paste / adhesive — grams
    "Solder Paste SAC305": "g",
    "Thermal Paste": "g",
    "Adhesive (Cyanoacrylate)": "g",
    # Electronic components — pieces
    "Ferrite Core": "pcs",
    "Neodymium Magnet": "pcs",
    "Capacitor (SMD)": "pcs",
    "Resistor (SMD)": "pcs",
    "IC Chip Package": "pcs",
    "Connector Housing": "pcs",
    # Seals / gaskets — pieces
    "O-Ring (Viton)": "pcs",
    "Gasket Material (PTFE)": "pcs",
    "Bearing Ball (Chrome Steel)": "pcs",
    # Fluids — litres
    "Hydraulic Fluid ISO-46": "L",
    "Lubricant Grease (Lithium)": "L",
    "Anodize Solution": "L",
    "Nickel Plating Solution": "L",
    # Coatings / paint — kilograms
    "Paint Primer (Zinc)": "kg",
    "Powder Coat (RAL 7035)": "kg",
}

# ---------------------------------------------------------------------------
# Suppliers
# ---------------------------------------------------------------------------
SUPPLIER_NAMES: list[str] = [
    "Precision Metals Inc.", "Advanced Polymer Solutions", "GlobalTech Components",
    "Apex Steel Corp.", "NovaChem Industries", "ElectroParts International",
    "Pacific Alloy Supply", "Summit Materials Group", "CoreTech Ceramics",
    "ProFlow Hydraulics", "TitanForge Metals", "OmniPlast Polymers",
    "Vertex Electronics", "Cascade Fasteners", "Atlas Bearing Co.",
    "Pinnacle Coatings Ltd.", "EagleTech Semiconductors", "Horizon Wire & Cable",
    "Nordic Precision AB", "RheinStahl GmbH", "Fuji Component Works",
    "Donghua Materials Co.", "Samwon Tech Corp.", "Formosa Plastics Supply",
    "Monterrey Steel SA", "TechStar Components", "Quantum Sensor Solutions",
    "Alpine Magnetics", "Heritage Alloy Foundry", "Continental Rubber Works",
    "Delta Fluid Power", "Spartan Surface Tech", "AeroSpec Alloys",
    "CrossLink Adhesives", "MidWest Stamping Inc.", "Southern Tube & Pipe",
    "LightPath Optics", "Dynamo Electric Supply", "BlueLine Fastening Systems",
    "Terra Mineral Processing", "ShinEtsu Silicones", "Premier Die Casting",
    "OakRidge Composites", "Sterling Hydraulics Ltd.", "SummitView Logistics",
    "GreenField Chemicals", "MetaPower Magnetics", "TransPacific Metals",
    "NorthStar Bearings", "Unified Plating Services", "IronBridge Fabrication",
    "NeoChem Polymers", "EliteWire Solutions", "PureTech Substrates",
    "Sakura Electronics Co.", "Han River Materials", "BrightCoat Finishes",
    "SolidState Devices", "ProCast Foundry", "Westlake Plastics Supply",
]

SUPPLIER_COUNTRIES: list[str] = [
    "USA", "Germany", "Japan", "China", "South Korea",
    "Taiwan", "Mexico", "India", "Italy", "Canada", "UK", "Brazil",
]

SUPPLIER_CERTIFICATIONS: list[str] = [
    "ISO 9001", "ISO 14001", "IATF 16949", "AS9100",
    "ISO 13485", "NADCAP", "ISO 45001",
]

# ---------------------------------------------------------------------------
# Machines
# ---------------------------------------------------------------------------
MACHINE_TYPES: dict[str, list[str]] = {
    "CNC": [
        "CNC Lathe", "CNC Mill", "CNC Router", "5-Axis CNC Center",
    ],
    "Press": [
        "Hydraulic Press 200T", "Mechanical Press 100T", "Servo Press 50T",
    ],
    "Injection Molding": [
        "IM Machine 150T", "IM Machine 300T", "IM Machine 500T",
    ],
    "Assembly": [
        "Robotic Assembly Cell", "Manual Assembly Station", "Automated Assembly Line",
    ],
    "Welding": [
        "MIG Welder", "TIG Welder", "Spot Welder", "Laser Welder",
    ],
    "Testing": [
        "CMM Machine", "Tensile Tester", "Vibration Test Bench", "Thermal Chamber",
    ],
    "Surface Treatment": [
        "Paint Booth", "Powder Coating Line", "Anodizing Tank", "Plating Line",
    ],
    "SMT": [
        "Pick-and-Place Machine", "Reflow Oven", "Wave Solder Machine", "Stencil Printer",
    ],
}

MACHINE_LOCATIONS: list[str] = [
    "Building A - Line 1", "Building A - Line 2", "Building A - Line 3",
    "Building B - Line 1", "Building B - Line 2",
    "Building C - Lab", "Building C - Line 1",
    "Building D - Assembly",
]

# ---------------------------------------------------------------------------
# Process-step templates (ordered) for each product category
# ---------------------------------------------------------------------------
PROCESS_STEP_TEMPLATES: dict[str, list[str]] = {
    "Electronics Assembly": [
        "Component Preparation", "SMT Placement", "Reflow Soldering",
        "Through-Hole Assembly", "Wave Soldering", "Functional Test",
        "Conformal Coating", "Final Assembly",
    ],
    "Mechanical Component": [
        "Raw Material Cutting", "CNC Machining", "Deburring",
        "Heat Treatment", "Surface Finishing", "Dimensional Inspection", "Assembly",
    ],
    "Hydraulic System": [
        "Component Machining", "Honing", "Seal Installation",
        "Sub-Assembly", "Pressure Test", "System Integration",
        "Leak Test", "Final Inspection",
    ],
    "Electrical Harness": [
        "Wire Cutting", "Terminal Crimping", "Connector Assembly",
        "Continuity Test", "Harness Routing", "Labeling",
        "Insulation Test", "Final Inspection",
    ],
    "Plastic Molding": [
        "Material Drying", "Injection Molding", "Trimming",
        "Quality Check", "Surface Treatment", "Packaging",
    ],
    "Metal Fabrication": [
        "Sheet Cutting", "Bending / Forming", "Welding",
        "Grinding", "Surface Preparation", "Painting / Coating",
        "Dimensional Inspection", "Packaging",
    ],
    "PCB Assembly": [
        "Bare Board Inspection", "Solder Paste Application", "Component Placement",
        "Reflow Soldering", "AOI Inspection", "Through-Hole Insertion",
        "Wave Soldering", "In-Circuit Test", "Functional Test",
    ],
    "Sensor Module": [
        "Sensor Element Preparation", "Die Bonding", "Wire Bonding",
        "Encapsulation", "Calibration", "Functional Test",
        "Environmental Screening", "Final Inspection",
    ],
    "Pneumatic Valve": [
        "Body Machining", "Spool Machining", "Seal Assembly",
        "Valve Assembly", "Pressure Test", "Leak Test",
        "Flow Calibration", "Final Inspection",
    ],
    "Motor Assembly": [
        "Stator Winding", "Rotor Assembly", "Bearing Installation",
        "Housing Assembly", "Electrical Connection", "No-Load Test",
        "Load Test", "Final Inspection",
    ],
    "Heat Exchanger": [
        "Tube Cutting", "Fin Stamping", "Core Assembly",
        "Brazing / Soldering", "Pressure Test", "Leak Test",
        "Surface Treatment", "Final Inspection",
    ],
    "Control Panel": [
        "Back-Panel Preparation", "Component Mounting", "Wiring",
        "Labeling", "Continuity Test", "Functional Test",
        "Hi-Pot Test", "Final Inspection",
    ],
    "Gear Box": [
        "Gear Machining", "Heat Treatment", "Gear Grinding",
        "Shaft Assembly", "Housing Assembly", "Lubrication Fill",
        "Noise / Vibration Test", "Final Inspection",
    ],
    "Bearing Assembly": [
        "Race Grinding", "Ball / Roller Sorting", "Assembly",
        "Lubrication", "Seal Installation", "Noise Test",
        "Dimensional Inspection", "Packaging",
    ],
    "Pump Unit": [
        "Impeller Machining", "Casing Machining", "Shaft Fitting",
        "Seal Installation", "Assembly", "Pressure Test",
        "Flow Test", "Final Inspection",
    ],
}

# ---------------------------------------------------------------------------
# Defects
# ---------------------------------------------------------------------------
DEFECT_TYPES: list[str] = [
    "Dimensional Out-of-Spec", "Surface Scratch", "Porosity", "Crack",
    "Solder Bridge", "Cold Solder Joint", "Missing Component",
    "Wrong Component", "Contamination", "Discoloration", "Warpage",
    "Burr", "Corrosion", "Delamination", "Short Circuit",
    "Open Circuit", "Misalignment", "Weld Defect", "Paint Defect",
    "Hardness Out-of-Spec",
]

DEFECT_SEVERITIES: list[str] = ["Critical", "Major", "Minor", "Cosmetic"]
DEFECT_SEVERITY_WEIGHTS: list[float] = [0.05, 0.20, 0.50, 0.25]  # sums to 1.0

# ---------------------------------------------------------------------------
# Inspections
# ---------------------------------------------------------------------------
INSPECTION_TYPES: list[str] = [
    "Incoming Material", "In-Process", "Final", "Dimensional",
    "Visual", "Functional", "Destructive Test",
]

# ---------------------------------------------------------------------------
# CAPA (Corrective and Preventive Action)
# ---------------------------------------------------------------------------
CAPA_ACTION_TYPES: list[str] = [
    "Containment", "Root Cause Analysis", "Corrective Action",
    "Preventive Action", "Design Change", "Process Change",
    "Supplier Corrective Action", "Training",
]

CAPA_STATUSES: list[str] = [
    "Open", "In Progress", "Pending Verification", "Closed",
]

# ---------------------------------------------------------------------------
# Production orders
# ---------------------------------------------------------------------------
PRODUCTION_ORDER_PRIORITIES: list[str] = ["Low", "Normal", "High", "Urgent"]
PRODUCTION_ORDER_PRIORITY_WEIGHTS: list[float] = [0.10, 0.55, 0.25, 0.10]  # sums to 1.0

PRODUCTION_ORDER_STATUSES: list[str] = [
    "Planned", "In Progress", "Completed", "On Hold", "Cancelled",
]
PRODUCTION_ORDER_STATUS_WEIGHTS: list[float] = [0.05, 0.10, 0.70, 0.10, 0.05]  # sums to 1.0

# ---------------------------------------------------------------------------
# Anomaly types (intentionally injected data-quality issues)
# ---------------------------------------------------------------------------

class AnomalyType:
    """Enumeration of anomaly tags injected into synthetic data for testing
    data-quality and traceability-audit scenarios."""

    PHANTOM_LOT = "defect_linked_to_nonexistent_lot"
    UNCONSUMED_BOM = "bom_component_never_consumed"
    PREMATURE_CAPA_CLOSE = "capa_closed_before_verification"
    EXCESS_DEFECT_QTY = "defect_qty_exceeds_inspected_qty"
    BROKEN_CHAIN = "broken_traceability_chain"
