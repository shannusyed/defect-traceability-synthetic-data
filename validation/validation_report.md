# Manufacturing Defect Traceability - Validation Report

- **Execution Timestamp:** 2026-10-29 09:36:35
- **Scale Configuration:** `full`
- **Random Seed:** `20261022`
- **Overall Verdict:** **ALL CHECKS PASSED** (42/42 checks passed)

---

## 1. Table Volume and Entity Counts

| Entity / Table | Primary Key | Total Records | File Size (Bytes) |
|----------------|-------------|---------------|-------------------|
| `products.csv` | `sku_id` | 200 | 14,249 |
| `bom.csv` | `bom_id` | 815 | 45,594 |
| `suppliers.csv` | `supplier_id` | 50 | 4,373 |
| `material_lots.csv` | `lot_id` | 2,000 | 212,674 |
| `production_orders.csv` | `order_id` | 5,000 | 343,255 |
| `order_lot_consumption.csv` | `(order_id, lot_id, material_name)` | 20,638 | 1,415,860 |
| `machines.csv` | `machine_id` | 30 | 2,856 |
| `process_steps.csv` | `step_id` | 39,389 | 5,223,821 |
| `inspection_plans.csv` | `plan_id` | 408 | 40,963 |
| `inspection_results.csv` | `inspection_id` | 20,000 | 1,716,550 |
| `defects.csv` | `defect_id` | 3,976 | 958,728 |
| `corrective_actions.csv` | `capa_id` | 3,393 | 509,228 |
| `ground_truth.csv` | `anomaly_id` | 25 | 5,057 |

---

## 2. Primary Key Uniqueness

| Check | Status | Verification Detail |
|-------|--------|---------------------|
| PK uniqueness: products.sku_id | **PASS** | 200 rows, 200 unique |
| PK uniqueness: bom.bom_id | **PASS** | 815 rows, 815 unique |
| PK uniqueness: suppliers.supplier_id | **PASS** | 50 rows, 50 unique |
| PK uniqueness: material_lots.lot_id | **PASS** | 2,000 rows, 2,000 unique |
| PK uniqueness: production_orders.order_id | **PASS** | 5,000 rows, 5,000 unique |
| PK uniqueness: machines.machine_id | **PASS** | 30 rows, 30 unique |
| PK uniqueness: process_steps.step_id | **PASS** | 39,389 rows, 39,389 unique |
| PK uniqueness: inspection_plans.plan_id | **PASS** | 408 rows, 408 unique |
| PK uniqueness: inspection_results.inspection_id | **PASS** | 20,000 rows, 20,000 unique |
| PK uniqueness: defects.defect_id | **PASS** | 3,976 rows, 3,976 unique |
| PK uniqueness: corrective_actions.capa_id | **PASS** | 3,393 rows, 3,393 unique |
| PK uniqueness: ground_truth.anomaly_id | **PASS** | 25 rows, 25 unique |
| Composite key: order_lot_consumption.(order_id, lot_id, material_name) | **PASS** | 20,638 rows, 20,638 unique |

---

## 3. Foreign Key Integrity

| Relationship | Status | Orphans Detected |
|-------------|--------|------------------|
| bom.sku_id -> products.sku_id | **PASS** | 0 orphan(s) |
| material_lots.supplier_id -> suppliers.supplier_id | **PASS** | 0 orphan(s) |
| production_orders.sku_id -> products.sku_id | **PASS** | 0 orphan(s) |
| order_lot_consumption.order_id -> production_orders.order_id | **PASS** | 0 orphan(s) |
| order_lot_consumption.lot_id -> material_lots.lot_id | **PASS** | 0 orphan(s) |
| process_steps.order_id -> production_orders.order_id | **PASS** | 0 orphan(s) |
| process_steps.machine_id -> machines.machine_id | **PASS** | 0 orphan(s) |
| inspection_plans.sku_id -> products.sku_id | **PASS** | 0 orphan(s) |
| inspection_results.order_id -> production_orders.order_id | **PASS** | 0 orphan(s) |
| inspection_results.plan_id -> inspection_plans.plan_id | **PASS** | 0 orphan(s) |
| corrective_actions.defect_id -> defects.defect_id | **PASS** | 0 orphan(s) |
| defects.inspection_id -> inspection_results.inspection_id (clean) | **PASS** | 0 orphan(s) |
| defects.order_id -> production_orders.order_id (clean) | **PASS** | 0 orphan(s) |
| defects.lot_id -> material_lots.lot_id (excl phantom anomalies) | **PASS** | 0 orphan(s) |
| defects.step_id -> process_steps.step_id (excl broken chain) | **PASS** | 0 orphan(s) |

---

## 4. Quantity Reconciliation

| Check | Status | Detail |
|-------|--------|--------|
| consumed <= lot original quantity | **PASS** | 0 lot(s) over-consumed |
| remaining_quantity = original - consumed | **PASS** | 0 mismatch(es) |

---

## 5. Chronological Date Ordering

| Chronological Constraint | Status | Violations |
|-------------------------|--------|------------|
| order start <= end | **PASS** | 0 violation(s) |
| step start <= end | **PASS** | 0 violation(s) |
| inspection_date within order start/end range | **PASS** | 0 violation(s) |
| defect detection_date >= inspection_date | **PASS** | 0 violation(s) |
| CAPA completion_date <= verification_date | **PASS** | 0 violation(s) |

---

## 6. Business Lifecycle Rules

| Rule | Status | Detail |
|------|--------|--------|
| Closed CAPA has verification_date (clean records) | **PASS** | 0 violation(s) |
| defect_quantity <= inspected_quantity (clean records) | **PASS** | 0 violation(s) |

---

## 7. Anomaly Inventory (Ground Truth Audit)

| Anomaly Type | Injected Count | Status |
|--------------|----------------|--------|
| `defect_linked_to_nonexistent_lot` | 5 injected (expected 5) | **PASS** |
| `bom_component_never_consumed` | 5 injected (expected 5) | **PASS** |
| `capa_closed_before_verification` | 5 injected (expected 5) | **PASS** |
| `defect_qty_exceeds_inspected_qty` | 5 injected (expected 5) | **PASS** |
| `broken_traceability_chain` | 5 injected (expected 5) | **PASS** |

---

## 8. Cryptographic File Checksums (SHA-256)

| File Name | SHA-256 Checksum |
|-----------|------------------|
| `bom.csv` | `93388b2b6f6bb04bd5ea02a1683f969f796a3c39fe28a08d08d7340c12daa450` |
| `corrective_actions.csv` | `6399953d8132a230bb0951a0a53c551e600f6e0a730415cd2e5c75cc3b6906d9` |
| `defects.csv` | `21f5dbe55c79570088651c6a7a914226a605d3de826af282dec4f2fadd35728a` |
| `ground_truth.csv` | `f8fe58c73474958991068c74ab09ca1d80ce3a32d1c0b6e59f087d744503bc17` |
| `inspection_plans.csv` | `94a3de9f5770cbfe44424d35b4a029a197b64040fef80a7d18a57e859811ccc8` |
| `inspection_results.csv` | `581d959344d6fddb2f190907a45b66b2ffd4b9b286fb7cce330b5aace9983148` |
| `machines.csv` | `abc6970cd756efbe00bb9c36b3ea245ad4693ccb5133b3ef3ad94ba46ecf58ec` |
| `material_lots.csv` | `db31803d17e4190b1f909d9a8997147866f826a82ebbbc6d8ad17f9e58f3d892` |
| `order_lot_consumption.csv` | `75df909d14a5e00652c9e72211d4c24e92ce088dc8a72f0ee0061a8eb73e3155` |
| `process_steps.csv` | `e1beacb076ee709233dc402bca8b13b94434b78b42941f9c821437c86c6ceb1a` |
| `production_orders.csv` | `57ce6e6ff71e3ce968e0c131d274d80543e7c35a32e3f0a604d2eddbad4a843e` |
| `products.csv` | `392e8ac583133bff1a96849ff3c02913e576fbd8e580a29854b3aa08fcf6a988` |
| `suppliers.csv` | `46860582cf357505a5640ea1a31ff440fd665fd1c4dc3cdfbefe16cd2f8500e0` |