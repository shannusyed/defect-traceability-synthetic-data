# Manufacturing Defect Traceability Synthetic Data Generator

A production-ready, self-contained Python framework for generating realistic, fully linked, and reproducible synthetic datasets modeling end-to-end defect traceability in modern discrete and hybrid manufacturing environments.

The dataset enables bi-directional traceability across the entire product lifecycle:
$$\text{Product \& BOM} \longleftrightarrow \text{Supplier} \longleftrightarrow \text{Material Lot} \longleftrightarrow \text{Production Order} \longleftrightarrow \text{Process Step / Machine} \longleftrightarrow \text{Inspection} \longleftrightarrow \text{Defect} \longleftrightarrow \text{CAPA}$$

---

## 1. Project Overview & Architecture

Modern industrial analytics, root cause analysis (RCA), and quality management systems require rigorous data structures linking shop-floor execution with quality inspections and engineering corrective actions. This generator models this ecosystem with:

- **Entity-Relationship Integrity:** Strict primary key and foreign key relationships with zero orphan records (except controlled, labelled anomalies).
- **Physical Reconciliation:** Material consumption matches BOM specifications and enforces that total consumption from any lot never exceeds initial received inventory.
- **Chronological Coherence:** Every timestamp respects physical causality:
  $$\text{Lot Receipt} \le \text{Order Start} \le \text{Process Step} \le \text{Inspection} \le \text{Defect Detection} \le \text{CAPA Resolution} \le \text{Verification}$$
- **Controlled Anomaly Injection:** Explicitly isolated and labelled anomalies recorded strictly in `ground_truth.csv` for training and benchmarking data quality monitoring algorithms.

---

## 2. Directory Structure

```text
defect_traceability_synthetic/
├── generate_data.py              # Main CLI entry point & validation engine
├── config.py                     # Central configuration, enums, scales & seed
├── schema/
│   └── data_dictionary.md        # Complete field-level documentation & ER diagrams
├── data/                         # Generated CSV data files (13 tables)
│   ├── products.csv              # Finished goods catalog
│   ├── bom.csv                   # Bill of materials mapping
│   ├── suppliers.csv             # Tier-1 and Tier-2 supplier directory
│   ├── material_lots.csv         # Raw material inventory batches
│   ├── production_orders.csv     # Manufacturing work orders
│   ├── order_lot_consumption.csv # M:N bridge table with consumed quantities
│   ├── machines.csv              # Plant asset registry
│   ├── process_steps.csv         # Execution routing and step-level yield
│   ├── inspection_plans.csv      # Quality control sampling plans
│   ├── inspection_results.csv    # Inspection execution records
│   ├── defects.csv               # Non-conformance defect occurrences
│   ├── corrective_actions.csv    # CAPA engineering lifecycle records
│   └── ground_truth.csv          # Labelled anomaly ground truth catalog
├── validation/
│   └── validation_report.md      # Auto-generated verification audit report
├── README.md                     # Project documentation & run guide
└── requirements.txt              # Minimal dependency definitions
```

---

## 3. Installation & Prerequisites

The generator uses pure Python 3.10+ and standard numerical libraries (`pandas`, `numpy`).

```bash
# Clone or navigate to the repository directory
cd MFG_Traceability_DataGenerator

# Install required dependencies
pip install -r requirements.txt
```

---

## 4. How to Run

The tool provides an intuitive command-line interface via `generate_data.py`.

### 4.1 Full Scale Generation (Default)
Generates the complete enterprise-scale dataset with 200 products, 50 suppliers, 2,000 lots, 5,000 work orders, and ~20,000 inspection results.

```bash
python generate_data.py --scale full --seed 20261022
```

### 4.2 Small Scale Generation (Fast Prototyping)
Generates a lightweight dataset ideal for CI/CD pipelines, unit testing, and rapid schema prototyping.

```bash
python generate_data.py --scale small --seed 20261022
```

### 4.3 Custom Output Directory
You can redirect output CSVs to any folder:

```bash
python generate_data.py --scale small --seed 20261022 --output-dir ./custom_data
```

---

## 5. Parameterized Volumes & Scale Specifications

| Entity / Metric | Small Scale (`--scale small`) | Full Scale (`--scale full`) | Primary Key Convention |
|-----------------|------------------------------:|----------------------------:|------------------------|
| **Products** | 20 | 200 | `SKU-000001` |
| **BOM Entries** | ~70–80 | ~700–900 | `BOM-000001` |
| **Suppliers** | 10 | 50 | `SUP-000001` |
| **Machines** | 10 | 30 | `MCH-000001` |
| **Material Lots** | 200 | 2,000 | `LOT-SUP-000001-2026-000001` |
| **Production Orders** | 500 | 5,000 | `WO-2026-000001` |
| **Consumption Bridge** | ~1,500–1,800 | ~16,000–19,000 | `(order_id, lot_id, material_name)` |
| **Process Steps** | ~4,000 | ~40,000 | `STEP-WO-2026-000001-001` |
| **Inspection Plans** | ~40 | ~400 | `PLAN-000001` |
| **Inspection Results** | 2,000 | 20,000 | `INSP-WO-2026-000001-001` |
| **Defects** | ~350–450 | ~3,500–4,500 | `DEF-2026-000001` |
| **Corrective Actions** | ~300–400 | ~3,000–4,000 | `CAPA-2026-000001` |
| **Anomalies Injected** | 10 (2 per type) | 25 (5 per type) | `ANOM-0001` |

---

## 6. Reproducibility & Determinism

The generator utilizes NumPy's high-performance BitGenerator (`numpy.random.default_rng`) seeded with a fixed integer seed (default: `20261022`).

### Verifying Determinism:
1. Run the generation script once:
   ```bash
   python generate_data.py --scale small --seed 20261022
   ```
2. Note the SHA-256 checksums printed at the completion of the run.
3. Delete the `./data` folder and re-run with the exact same parameters:
   ```bash
   python generate_data.py --scale small --seed 20261022
   ```
4. Verify that:
   - Row counts for all 13 tables are byte-for-byte identical.
   - All SHA-256 file hashes match exactly.

---

## 7. Labelled Anomalies (Ground Truth Catalog)

To support automated data-quality testing, anomaly detection models, and audit simulations, the generator injects five controlled classes of industrial data discrepancies. Normal records remain completely clean; injected issues are tracked strictly in `ground_truth.csv`.

| # | Anomaly Type Key | Description | Affected Entity | Target Field |
|---|------------------|-------------|-----------------|--------------|
| 1 | `defect_linked_to_nonexistent_lot` | Defect record references a phantom material lot ID not found in `material_lots.csv`. | `defects` | `lot_id` |
| 2 | `bom_component_never_consumed` | A component defined in the BOM is never recorded in any order's consumption ledger. | `bom` | `material_name` |
| 3 | `capa_closed_before_verification` | Corrective Action is marked with status `"Closed"` while `verification_date` is `NULL`. | `corrective_actions` | `status` |
| 4 | `defect_qty_exceeds_inspected_qty` | Reported defect quantity exceeds total number of units physically inspected. | `defects` | `defect_quantity` |
| 5 | `broken_traceability_chain` | Defect references an invalid process step ID (`STEP-WO-2026-999999-999`), breaking the link to machine and line. | `defects` | `step_id` |

---

## 8. Automated Validation Suite

At the conclusion of each generation cycle, `generate_data.py` executes 42 automated integrity checks:

1. **Primary Key Uniqueness:** Verifies 100% uniqueness across all 12 operational entities and the anomaly registry.
2. **Bridge Composite Key Integrity:** Ensures composite primary key `(order_id, lot_id, material_name)` in `order_lot_consumption` has no duplicates.
3. **Foreign Key Integrity:** Verifies all 10 standard foreign keys have 0 orphans, and isolates clean vs. anomalous defect foreign keys.
4. **Physical Quantity Reconciliation:** Asserts that consumed lot quantity $\le$ original lot quantity, and `remaining_quantity = quantity - consumed`.
5. **Causal Timeline Ordering:** Asserts all date intervals follow physical manufacturing flow without inversion.
6. **Regulatory Lifecycle Validation:** Asserts closed CAPAs have verification dates (clean) and defect quantities are bounded by inspection volume.
7. **Anomaly Ledger Audit:** Confirms exact counts of each anomaly category in `ground_truth.csv`.

The full report is saved to `validation/validation_report.md` after every run.

