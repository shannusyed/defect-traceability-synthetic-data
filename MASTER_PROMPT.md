# MASTER PROMPT – Manufacturing Defect Traceability Synthetic Data Generator

You are a senior Python data engineer specializing in high-quality, reproducible synthetic data for industrial / manufacturing systems.

Your task is to build a **complete, production-ready, self-contained project** that generates a realistic synthetic dataset for end-to-end defect traceability in a manufacturing plant.

The dataset must allow tracing any defect from Inspection → Production Order → Process Step → Machine → Material Lot → Supplier, and forward to Corrective Action (CAPA).

---

## 1. Project Goal (Non-Negotiable)

Generate a fully linked, validated, reproducible synthetic dataset that models the complete lifecycle:

Product & BOM → Supplier → Material Lot → Production Order → Process Step / Machine → Inspection → Defect → Corrective Action

The output must be ready for use in analytics, quality systems, or ML feature stores. No application, dashboard, or post-processing is required — only high-quality data generation + documentation.

---

## 2. Locked Design Decisions

### 2.1 Entities & Relationships (Final Schema)

| Entity              | Primary Key          | Key Relationships                                      | Cardinality      |
|---------------------|----------------------|--------------------------------------------------------|------------------|
| Product             | sku_id               | -                                                      | -                |
| BOM                 | bom_id               | product → materials                                    | 1:N              |
| Supplier            | supplier_id          | -                                                      | -                |
| MaterialLot         | lot_id               | → Supplier                                             | N:1              |
| ProductionOrder     | order_id             | → Product, consumes MaterialLots                       | N:1 + N:M        |
| Machine             | machine_id           | -                                                      | -                |
| ProcessStep         | step_id              | → ProductionOrder, → Machine                           | N:1              |
| InspectionPlan      | plan_id              | → Product                                              | N:1              |
| InspectionResult    | inspection_id        | → ProductionOrder, → InspectionPlan                    | N:1              |
| Defect              | defect_id            | → InspectionResult, → ProductionOrder, → MaterialLot, → ProcessStep | N:1     |
| CorrectiveAction    | capa_id              | → Defect                                               | N:1              |

Many-to-many between ProductionOrder and MaterialLot must use an explicit bridge table: `order_lot_consumption`.

### 2.2 Strict ID Conventions (Immutable)

- Product:          `SKU-000001`
- Supplier:         `SUP-000001`
- MaterialLot:      `LOT-SUP-000001-2026-000001`
- ProductionOrder:  `WO-2026-000001`
- Machine:          `MCH-000001`
- ProcessStep:      `STEP-WO-2026-000001-001`
- Inspection:       `INSP-WO-2026-000001-001`
- Defect:           `DEF-2026-000001`
- CAPA:             `CAPA-2026-000001`

All counters zero-padded. IDs never change once created.

### 2.3 Volume (Parameterized)

Support two scales via CLI:

**Full scale (default):**
- 200 Products
- 50 Suppliers
- 2,000 Material Lots
- 5,000 Production Orders
- ~20,000 Inspection Results
- Realistic number of Process Steps, Defects, CAPAs

**Small scale (`--scale small`):**
- 20 Products
- 10 Suppliers
- 200 Material Lots
- 500 Production Orders
- 2,000 Inspection Results

Use fixed seed `20261022` by default (overridable).

### 2.4 Generation Order (Must be followed strictly)

1. Products + BOM
2. Suppliers + Machines
3. MaterialLots
4. ProductionOrders + order_lot_consumption (with quantity reconciliation)
5. ProcessSteps
6. InspectionPlans + InspectionResults
7. Defects
8. CorrectiveActions

Never generate children before parents. Never overwrite historical records.

### 2.5 Business Rules (Enforced)

- Total quantity consumed from a MaterialLot ≤ original lot quantity
- Defect quantity ≤ inspected quantity (except labelled anomalies)
- CAPA status can become "Closed" only after verification_date is populated (except labelled anomalies)
- All dates must be chronologically consistent (lot receipt ≤ order start ≤ process ≤ inspection ≤ defect ≤ CAPA)
- Derived fields (defect_rate, remaining_qty, status, etc.) are calculated, never randomly assigned

### 2.6 Required Anomalies (Labelled)

Inject a controlled number of each type and record **only** in `ground_truth.csv`:

1. Defect linked to non-existent MaterialLot
2. BOM component that was never consumed in any order
3. CAPA closed before verification
4. Defect quantity > inspected quantity
5. Broken traceability chain (missing intermediate foreign key)

Normal records must remain clean. Anomalies are explicitly labelled.

---

## 3. Required Project Structure

```text
defect_traceability_synthetic/
├── generate_data.py              # Main CLI entry point
├── config.py                     # All parameters, seed, volumes
├── schema/
│   └── data_dictionary.md        # Complete field-level documentation
├── data/                         # All generated CSV files
│   ├── products.csv
│   ├── bom.csv
│   ├── suppliers.csv
│   ├── material_lots.csv
│   ├── production_orders.csv
│   ├── order_lot_consumption.csv
│   ├── machines.csv
│   ├── process_steps.csv
│   ├── inspection_plans.csv
│   ├── inspection_results.csv
│   ├── defects.csv
│   ├── corrective_actions.csv
│   └── ground_truth.csv
├── validation/
│   └── validation_report.md
├── README.md
└── requirements.txt
```

---

## 4. Technical Implementation Requirements

- Language: Pure Python 3.10+
- Libraries: pandas, numpy only (no other heavy dependencies)
- CLI using argparse:
  ```bash
  python generate_data.py --scale full --seed 20261022
  python generate_data.py --scale small --seed 20261022
  ```

- Fully deterministic with the given seed
- After generation, automatically run comprehensive validation
- At the end print:
  - Row counts of every table
  - MD5 or SHA256 checksums of key files
  - Validation summary (pass/fail)

Code must be modular, well-commented, and easy to maintain.

---

## 5. Documentation Requirements (Must be high quality)

### `data_dictionary.md`
For every field of every table document:
- Data type
- Required / Optional
- Allowed values / enums
- Units
- Uniqueness constraints
- Validation rules
- Relationships / foreign keys

### `README.md` must contain:
- Project purpose
- How to run (both scales)
- Seed used
- Exact volume numbers
- How to verify reproducibility
- Brief explanation of anomalies

### `validation_report.md` must prove:
- Primary key uniqueness
- Foreign key integrity
- Quantity reconciliation (lots vs consumption)
- Date ordering
- Lifecycle rules
- Anomaly counts

---

## 6. Final Acceptance Criteria

When the generator is run with seed `20261022`:
- All tables are created with correct volumes
- All foreign keys are valid (except deliberately broken anomaly cases)
- Quantities reconcile
- Dates are chronologically correct
- `ground_truth.csv` contains only the labelled anomalies
- Running the generator twice with the same seed produces identical row counts and checksums
- Documentation is complete and professional

