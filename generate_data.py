#!/usr/bin/env python3
"""
Manufacturing Defect Traceability Synthetic Data Generator
==========================================================

Generates a fully linked, validated, reproducible synthetic dataset
that models the complete lifecycle of manufacturing defect traceability:

  Product & BOM -> Supplier -> Material Lot -> Production Order ->
  Process Step / Machine -> Inspection -> Defect -> Corrective Action

Usage:
    python generate_data.py --scale full  --seed 20261022
    python generate_data.py --scale small --seed 20261022

Author: Synthetic Data Engineering Team
"""

import argparse
import hashlib
import os
import sys
import textwrap
from datetime import datetime, timedelta
from pathlib import Path

# Safe stdout reconfiguration for Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Import project configuration
# ---------------------------------------------------------------------------
from config import (
    DEFAULT_SEED,
    YEAR,
    BASE_DATE,
    END_DATE,
    SCALES,
    PRODUCT_CATEGORIES,
    PRODUCT_NAMES,
    RAW_MATERIALS,
    MATERIAL_UNITS,
    SUPPLIER_NAMES,
    SUPPLIER_COUNTRIES,
    SUPPLIER_CERTIFICATIONS,
    MACHINE_TYPES,
    MACHINE_LOCATIONS,
    PROCESS_STEP_TEMPLATES,
    DEFECT_TYPES,
    DEFECT_SEVERITIES,
    DEFECT_SEVERITY_WEIGHTS,
    INSPECTION_TYPES,
    CAPA_ACTION_TYPES,
    CAPA_STATUSES,
    PRODUCTION_ORDER_PRIORITIES,
    PRODUCTION_ORDER_PRIORITY_WEIGHTS,
    PRODUCTION_ORDER_STATUSES,
    PRODUCTION_ORDER_STATUS_WEIGHTS,
    AnomalyType,
)


# ===================================================================
#  HELPER UTILITIES
# ===================================================================

def random_date(rng: np.random.Generator, start: datetime, end: datetime) -> datetime:
    """Return a uniformly random datetime between start and end."""
    delta = (end - start).total_seconds()
    offset = rng.integers(0, max(int(delta), 1))
    return start + timedelta(seconds=int(offset))


def random_date_after(rng: np.random.Generator, anchor: datetime, max_days: int = 30) -> datetime:
    """Return a random datetime within max_days after anchor, capped at END_DATE."""
    offset = rng.integers(0, max(max_days * 86400, 1))
    result = anchor + timedelta(seconds=int(offset))
    if result > END_DATE:
        result = END_DATE
    return result


def sha256_file(path: Path) -> str:
    """Return the SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


# ===================================================================
#  MAIN GENERATOR CLASS
# ===================================================================

class TraceabilityDataGenerator:
    """Orchestrates end-to-end generation of the defect traceability dataset."""

    def __init__(self, scale: str, seed: int, output_dir: Path):
        self.scale = scale
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.params = SCALES[scale]
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Stores for generated DataFrames
        self.data: dict[str, pd.DataFrame] = {}
        # Anomaly tracking records
        self.anomalies: list[dict] = []
        # Runtime counters
        self._defect_counter = 0
        self._capa_counter = 0

    # ---------------------------------------------------------------
    #  1. Products & BOM
    # ---------------------------------------------------------------
    def generate_products_and_bom(self):
        """Generate products.csv and bom.csv."""
        n_products = self.params["num_products"]

        # Pool of (category, name)
        pool = []
        for cat in PRODUCT_CATEGORIES:
            for name in PRODUCT_NAMES.get(cat, []):
                pool.append((cat, name))
        self.rng.shuffle(pool)

        products = []
        for i in range(n_products):
            idx = i % len(pool)
            cat, name = pool[idx]
            suffix = f" Mk{i // len(pool) + 2}" if i >= len(pool) else ""
            products.append({
                "sku_id": f"SKU-{i + 1:06d}",
                "product_name": f"{name}{suffix}",
                "category": cat,
                "unit_cost": round(float(self.rng.uniform(10.0, 5000.0)), 2),
                "weight_kg": round(float(self.rng.uniform(0.05, 500.0)), 2),
                "lead_time_days": int(self.rng.integers(1, 91)),
                "active": True,
            })
        df_products = pd.DataFrame(products)

        # BOM components
        bom_rows = []
        bom_counter = 0
        for prod in products:
            # 2 to 6 components per product
            num_components = int(self.rng.integers(2, 7))
            chosen_materials = self.rng.choice(
                RAW_MATERIALS, size=min(num_components, len(RAW_MATERIALS)), replace=False
            )
            for mat in chosen_materials:
                bom_counter += 1
                unit = MATERIAL_UNITS.get(mat, "kg")
                qty_per_unit = round(float(self.rng.uniform(0.05, 5.0)), 3)
                bom_rows.append({
                    "bom_id": f"BOM-{bom_counter:06d}",
                    "sku_id": prod["sku_id"],
                    "material_name": mat,
                    "quantity_per_unit": qty_per_unit,
                    "unit": unit,
                    "critical": bool(self.rng.random() < 0.30),
                })
        df_bom = pd.DataFrame(bom_rows)

        self.data["products"] = df_products
        self.data["bom"] = df_bom
        print(f"  [1/8] Products: {len(df_products):,}  |  BOM entries: {len(df_bom):,}")

    # ---------------------------------------------------------------
    #  2. Suppliers & Machines
    # ---------------------------------------------------------------
    def generate_suppliers_and_machines(self):
        """Generate suppliers.csv and machines.csv."""
        n_sup = self.params["num_suppliers"]
        n_mch = self.params["num_machines"]

        # Suppliers
        chosen_names = list(self.rng.choice(
            SUPPLIER_NAMES, size=min(n_sup, len(SUPPLIER_NAMES)), replace=False
        ))
        suppliers = []
        for i in range(n_sup):
            name = chosen_names[i] if i < len(chosen_names) else f"Supplier Industrial {i+1}"
            clean_email = name.lower().replace(" ", "").replace(".", "").replace(",", "")[:18]
            suppliers.append({
                "supplier_id": f"SUP-{i + 1:06d}",
                "supplier_name": name,
                "country": str(self.rng.choice(SUPPLIER_COUNTRIES)),
                "rating": round(float(self.rng.uniform(1.0, 5.0)), 1),
                "certification": str(self.rng.choice(SUPPLIER_CERTIFICATIONS)),
                "contact_email": f"sales@{clean_email}.com",
                "active": True,
            })
        df_suppliers = pd.DataFrame(suppliers)

        # Machines
        machine_pool = []
        for mtype, names in MACHINE_TYPES.items():
            for mname in names:
                machine_pool.append((mtype, mname))
        self.rng.shuffle(machine_pool)

        machines = []
        for i in range(n_mch):
            idx = i % len(machine_pool)
            mtype, mname = machine_pool[idx]
            suffix = f" #{i // len(machine_pool) + 2}" if i >= len(machine_pool) else ""
            install = random_date(self.rng, datetime(2018, 1, 1), BASE_DATE)
            last_maint = random_date(self.rng, install, END_DATE)
            machines.append({
                "machine_id": f"MCH-{i + 1:06d}",
                "machine_name": f"{mname}{suffix}",
                "machine_type": mtype,
                "location": str(self.rng.choice(MACHINE_LOCATIONS)),
                "status": str(self.rng.choice(
                    ["Operational", "Under Maintenance", "Decommissioned"],
                    p=[0.85, 0.10, 0.05]
                )),
                "install_date": install.strftime("%Y-%m-%d"),
                "last_maintenance_date": last_maint.strftime("%Y-%m-%d"),
            })
        df_machines = pd.DataFrame(machines)

        self.data["suppliers"] = df_suppliers
        self.data["machines"] = df_machines
        print(f"  [2/8] Suppliers: {len(df_suppliers):,}  |  Machines: {len(df_machines):,}")

    # ---------------------------------------------------------------
    #  3. Material Lots
    # ---------------------------------------------------------------
    def generate_material_lots(self):
        """Generate material_lots.csv with supplier linkage and realistic dates."""
        n_lots = self.params["num_material_lots"]
        suppliers = self.data["suppliers"]
        supplier_ids = suppliers["supplier_id"].tolist()
        bom = self.data["bom"]

        # Ensure every raw material in the BOM is supplied by at least 2 suppliers
        bom_materials = sorted(list(bom["material_name"].unique()))
        supplier_materials: dict[str, set[str]] = {sid: set() for sid in supplier_ids}

        for i, mat in enumerate(bom_materials):
            s1 = supplier_ids[i % len(supplier_ids)]
            s2 = supplier_ids[(i + 1) % len(supplier_ids)]
            supplier_materials[s1].add(mat)
            supplier_materials[s2].add(mat)

        for sid in supplier_ids:
            extra = int(self.rng.integers(3, 10))
            for m in self.rng.choice(RAW_MATERIALS, size=min(extra, len(RAW_MATERIALS)), replace=False):
                supplier_materials[sid].add(m)

        lots = []
        sup_lot_counters: dict[str, int] = {s: 0 for s in supplier_ids}

        # Step 3a: Guarantee opening inventory lots at BASE_DATE for each BOM material
        opening_lot_count = 0
        for mat in bom_materials:
            eligible_sups = sorted([sid for sid in supplier_ids if mat in supplier_materials[sid]])
            sid = str(self.rng.choice(eligible_sups)) if eligible_sups else supplier_ids[0]
            sup_lot_counters[sid] += 1
            opening_lot_count += 1

            unit = MATERIAL_UNITS.get(mat, "kg")
            qty = round(float(self.rng.uniform(2000.0, 10000.0)), 1)
            receipt = BASE_DATE + timedelta(days=int(self.rng.integers(0, 3)))
            expiry = (receipt + timedelta(days=int(self.rng.integers(180, 730)))).strftime("%Y-%m-%d")

            sup_num = int(sid.split("-")[1])
            lot_id = f"LOT-SUP-{sup_num:06d}-{YEAR}-{sup_lot_counters[sid]:06d}"

            lots.append({
                "lot_id": lot_id,
                "supplier_id": sid,
                "material_name": mat,
                "quantity": qty,
                "remaining_quantity": qty,
                "unit": unit,
                "receipt_date": receipt.strftime("%Y-%m-%d"),
                "expiry_date": expiry,
                "status": "Available",
                "certificate_of_analysis": True,
            })

        # Step 3b: Restock shipments throughout the year to fill the remaining quota
        remaining_lots_to_create = n_lots - opening_lot_count
        for _ in range(max(0, remaining_lots_to_create)):
            sid = str(self.rng.choice(supplier_ids))
            sup_lot_counters[sid] += 1
            available_mats = sorted(list(supplier_materials[sid]))
            mat = str(self.rng.choice(available_mats)) if available_mats else RAW_MATERIALS[0]

            unit = MATERIAL_UNITS.get(mat, "kg")
            qty = round(float(self.rng.uniform(1000.0, 8000.0)), 1)
            receipt = random_date(self.rng, BASE_DATE + timedelta(days=5), END_DATE - timedelta(days=10))

            expiry = None
            if self.rng.random() < 0.70:
                expiry = (receipt + timedelta(days=int(self.rng.integers(90, 730)))).strftime("%Y-%m-%d")

            sup_num = int(sid.split("-")[1])
            lot_id = f"LOT-SUP-{sup_num:06d}-{YEAR}-{sup_lot_counters[sid]:06d}"

            lots.append({
                "lot_id": lot_id,
                "supplier_id": sid,
                "material_name": mat,
                "quantity": qty,
                "remaining_quantity": qty,
                "unit": unit,
                "receipt_date": receipt.strftime("%Y-%m-%d"),
                "expiry_date": expiry,
                "status": "Available",
                "certificate_of_analysis": bool(self.rng.random() < 0.92),
            })

        df_lots = pd.DataFrame(lots)
        self.data["material_lots"] = df_lots
        self._lot_remaining = {r["lot_id"]: float(r["quantity"]) for r in lots}
        print(f"  [3/8] Material Lots: {len(df_lots):,}")

    # ---------------------------------------------------------------
    #  4. Production Orders + order_lot_consumption
    # ---------------------------------------------------------------
    def generate_production_orders(self):
        """Generate production_orders.csv and order_lot_consumption.csv with FIFO lot reconciliation."""
        n_orders = self.params["num_production_orders"]
        products = self.data["products"]
        bom = self.data["bom"]
        lots = self.data["material_lots"]

        sku_ids = products["sku_id"].tolist()

        bom_by_sku: dict[str, list[dict]] = {}
        for _, row in bom.iterrows():
            bom_by_sku.setdefault(row["sku_id"], []).append(row.to_dict())

        lots_by_material: dict[str, list[dict]] = {}
        for _, row in lots.sort_values("receipt_date").iterrows():
            lots_by_material.setdefault(row["material_name"], []).append({
                "lot_id": row["lot_id"],
                "receipt_date": datetime.strptime(row["receipt_date"], "%Y-%m-%d"),
                "total_quantity": row["quantity"],
            })

        orders = []
        consumption_rows = []
        consumed_materials: set[str] = set()

        raw_starts = [
            random_date(self.rng, BASE_DATE + timedelta(days=5), END_DATE - timedelta(days=15))
            for _ in range(n_orders)
        ]
        raw_starts.sort()

        for i in range(n_orders):
            sku = str(self.rng.choice(sku_ids))
            order_id = f"WO-{YEAR}-{i + 1:06d}"
            qty = int(self.rng.integers(10, 201))

            status = str(self.rng.choice(
                PRODUCTION_ORDER_STATUSES,
                p=PRODUCTION_ORDER_STATUS_WEIGHTS
            ))
            priority = str(self.rng.choice(
                PRODUCTION_ORDER_PRIORITIES,
                p=PRODUCTION_ORDER_PRIORITY_WEIGHTS
            ))

            start = raw_starts[i]
            lead_days = int(self.rng.integers(3, 30))
            end = start + timedelta(days=lead_days)
            if end > END_DATE:
                end = END_DATE

            orders.append({
                "order_id": order_id,
                "sku_id": sku,
                "quantity": qty,
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d"),
                "status": status,
                "priority": priority,
            })

            # Consume BOM materials
            bom_entries = bom_by_sku.get(sku, [])
            for bom_entry in bom_entries:
                mat = bom_entry["material_name"]
                qty_needed = round(bom_entry["quantity_per_unit"] * qty, 3)

                mat_lots = lots_by_material.get(mat, [])
                remaining_needed = qty_needed

                # First pass: FIFO among lots with receipt_date <= start and remaining > 0
                for lot_info in mat_lots:
                    if remaining_needed <= 0:
                        break
                    lot_id = lot_info["lot_id"]
                    if lot_info["receipt_date"] > start:
                        continue
                    avail = self._lot_remaining.get(lot_id, 0.0)
                    if avail <= 0:
                        continue

                    take = min(remaining_needed, avail)
                    take = round(take, 3)
                    if take <= 0:
                        continue

                    self._lot_remaining[lot_id] -= take
                    remaining_needed -= take

                    consumption_rows.append({
                        "order_id": order_id,
                        "lot_id": lot_id,
                        "material_name": mat,
                        "quantity_consumed": take,
                    })
                    consumed_materials.add(mat)

                # Fallback: if lots were exhausted, consume from the earliest lot of this material
                if remaining_needed > 0 and mat_lots:
                    for lot_info in mat_lots:
                        if lot_info["receipt_date"] <= start:
                            lot_id = lot_info["lot_id"]
                            avail = self._lot_remaining.get(lot_id, 0.0)
                            if avail > 0:
                                take = min(remaining_needed, avail)
                                take = round(take, 3)
                                if take > 0:
                                    self._lot_remaining[lot_id] -= take
                                    remaining_needed -= take
                                    consumption_rows.append({
                                        "order_id": order_id,
                                        "lot_id": lot_id,
                                        "material_name": mat,
                                        "quantity_consumed": take,
                                    })
                                    consumed_materials.add(mat)
                                    break

        df_orders = pd.DataFrame(orders)

        df_consumption = pd.DataFrame(consumption_rows)
        if len(df_consumption) > 0:
            df_consumption = (
                df_consumption.groupby(["order_id", "lot_id", "material_name"], as_index=False)["quantity_consumed"]
                .sum()
            )
            df_consumption["quantity_consumed"] = df_consumption["quantity_consumed"].round(3)

        # Update remaining_quantity and status in material_lots
        lots_df = self.data["material_lots"].copy()
        consumed_by_lot = df_consumption.groupby("lot_id")["quantity_consumed"].sum().to_dict()

        for idx, row in lots_df.iterrows():
            lid = row["lot_id"]
            orig = row["quantity"]
            tot_consumed = consumed_by_lot.get(lid, 0.0)
            rem = max(0.0, orig - tot_consumed)
            lots_df.at[idx, "remaining_quantity"] = round(rem, 3)
            if rem <= 0.001:
                lots_df.at[idx, "status"] = "Depleted"
            elif rem < orig - 0.001:
                lots_df.at[idx, "status"] = "In Use"
            else:
                lots_df.at[idx, "status"] = "Available"

        self.data["material_lots"] = lots_df
        self.data["production_orders"] = df_orders
        self.data["order_lot_consumption"] = df_consumption

        print(f"  [4/8] Production Orders: {len(df_orders):,}  |  Consumption records: {len(df_consumption):,}")

    # ---------------------------------------------------------------
    #  5. Process Steps
    # ---------------------------------------------------------------
    def generate_process_steps(self):
        """Generate process_steps.csv linked to orders and machines."""
        orders = self.data["production_orders"]
        products = self.data["products"]
        machines = self.data["machines"]

        sku_category = dict(zip(products["sku_id"], products["category"]))
        operational_machines = machines[machines["status"] == "Operational"]["machine_id"].tolist()
        if not operational_machines:
            operational_machines = machines["machine_id"].tolist()

        steps = []
        for _, order in orders.iterrows():
            oid = order["order_id"]
            sku = order["sku_id"]
            cat = sku_category.get(sku, "Mechanical Component")

            template = PROCESS_STEP_TEMPLATES.get(cat, ["Processing", "Assembly", "Inspection"])
            order_start = datetime.strptime(order["start_date"], "%Y-%m-%d") + timedelta(hours=8)
            order_end = datetime.strptime(order["end_date"], "%Y-%m-%d") + timedelta(hours=17)
            total_seconds = max((order_end - order_start).total_seconds(), 3600.0)
            step_duration = total_seconds / len(template)

            order_num_part = oid.replace("WO-", "")

            for seq, step_name in enumerate(template, start=1):
                step_start = order_start + timedelta(seconds=step_duration * (seq - 1))
                step_end = order_start + timedelta(seconds=step_duration * seq)
                mid = str(self.rng.choice(operational_machines))

                if order["status"] == "Completed":
                    st = "Completed"
                elif order["status"] == "Cancelled":
                    st = "Skipped"
                elif order["status"] == "On Hold":
                    st = str(self.rng.choice(["Completed", "Pending"], p=[0.5, 0.5]))
                else:
                    st = str(self.rng.choice(["Completed", "In Progress", "Pending"], p=[0.65, 0.25, 0.10]))

                yield_rate = round(float(self.rng.uniform(88.0, 100.0)), 1)
                if st == "Failed":
                    yield_rate = round(float(self.rng.uniform(40.0, 84.0)), 1)

                step_id = f"STEP-WO-{order_num_part}-{seq:03d}"

                steps.append({
                    "step_id": step_id,
                    "order_id": oid,
                    "machine_id": mid,
                    "step_name": step_name,
                    "sequence": seq,
                    "start_time": step_start.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": step_end.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": st,
                    "yield_rate": yield_rate,
                    "operator_id": f"EMP-{self.rng.integers(1000, 9999):04d}",
                })

        df_steps = pd.DataFrame(steps)
        self.data["process_steps"] = df_steps
        print(f"  [5/8] Process Steps: {len(df_steps):,}")

    # ---------------------------------------------------------------
    #  6. Inspection Plans & Results
    # ---------------------------------------------------------------
    def generate_inspections(self):
        """Generate inspection_plans.csv and inspection_results.csv."""
        products = self.data["products"]
        orders = self.data["production_orders"]
        n_results = self.params["num_inspection_results"]

        # Plans
        plans = []
        plan_counter = 0
        plans_by_sku: dict[str, list[str]] = {}
        for _, prod in products.iterrows():
            n_plans = int(self.rng.integers(1, 4))
            chosen_types = list(self.rng.choice(
                INSPECTION_TYPES, size=min(n_plans, len(INSPECTION_TYPES)), replace=False
            ))
            for itype in chosen_types:
                plan_counter += 1
                pid = f"PLAN-{plan_counter:06d}"
                plans.append({
                    "plan_id": pid,
                    "sku_id": prod["sku_id"],
                    "inspection_type": str(itype),
                    "criteria": f"Standard {itype} criteria for {prod['product_name']}",
                    "sampling_rate": round(float(self.rng.uniform(5.0, 100.0)), 1),
                    "active": True,
                })
                plans_by_sku.setdefault(prod["sku_id"], []).append(pid)

        df_plans = pd.DataFrame(plans)

        # Results
        order_list = orders.to_dict("records")
        order_sku = dict(zip(orders["order_id"], orders["sku_id"]))

        results = []
        order_insp_counter: dict[str, int] = {}

        for i in range(n_results):
            order = order_list[i % len(order_list)]
            oid = order["order_id"]
            sku = order_sku[oid]
            available_plans = plans_by_sku.get(sku, [])
            if not available_plans:
                continue

            plan_id = str(self.rng.choice(available_plans))
            order_insp_counter[oid] = order_insp_counter.get(oid, 0) + 1
            seq = order_insp_counter[oid]

            order_num_part = oid.replace("WO-", "")
            insp_id = f"INSP-WO-{order_num_part}-{seq:03d}"

            inspected = int(self.rng.integers(5, max(int(order["quantity"]), 6) + 1))
            if self.rng.random() < 0.80:
                failed = 0
            else:
                failed = int(self.rng.integers(1, max(inspected // 2, 2)))
                failed = min(failed, inspected)
            passed = inspected - failed

            if failed == 0:
                result = "Pass"
            elif failed < inspected * 0.30:
                result = str(self.rng.choice(["Fail", "Conditional Pass"], p=[0.60, 0.40]))
            else:
                result = "Fail"

            order_start = datetime.strptime(order["start_date"], "%Y-%m-%d")
            order_end = datetime.strptime(order["end_date"], "%Y-%m-%d")
            insp_date = random_date(self.rng, order_start, max(order_end, order_start + timedelta(days=1)))

            results.append({
                "inspection_id": insp_id,
                "order_id": oid,
                "plan_id": plan_id,
                "inspected_quantity": inspected,
                "passed_quantity": passed,
                "failed_quantity": failed,
                "inspection_date": insp_date.strftime("%Y-%m-%d"),
                "inspector_id": f"EMP-{self.rng.integers(1000, 9999):04d}",
                "result": result,
            })

        df_results = pd.DataFrame(results)
        self.data["inspection_plans"] = df_plans
        self.data["inspection_results"] = df_results
        print(f"  [6/8] Inspection Plans: {len(df_plans):,}  |  Results: {len(df_results):,}")

    # ---------------------------------------------------------------
    #  7. Defects
    # ---------------------------------------------------------------
    def generate_defects(self):
        """Generate defects.csv linked to inspections, orders, steps, and lots."""
        results = self.data["inspection_results"]
        steps = self.data["process_steps"]
        consumption = self.data["order_lot_consumption"]
        lots_all = self.data["material_lots"]["lot_id"].tolist()

        steps_by_order: dict[str, list[str]] = {}
        for _, row in steps.iterrows():
            steps_by_order.setdefault(row["order_id"], []).append(row["step_id"])

        lots_by_order: dict[str, list[str]] = {}
        for _, row in consumption.iterrows():
            lots_by_order.setdefault(row["order_id"], []).append(row["lot_id"])

        failed_inspections = results[results["failed_quantity"] > 0].to_dict("records")
        if not failed_inspections:
            failed_inspections = results.sample(min(100, len(results)), random_state=self.seed).to_dict("records")

        defects = []
        self._defect_counter = 0

        for insp in failed_inspections:
            self._defect_counter += 1
            oid = insp["order_id"]

            order_steps = steps_by_order.get(oid, [])
            order_lots = lots_by_order.get(oid, [])

            step_id = str(self.rng.choice(order_steps)) if order_steps else ""
            if order_lots:
                lot_id = str(self.rng.choice(sorted(list(set(order_lots)))))
            elif lots_all:
                lot_id = str(self.rng.choice(lots_all))
            else:
                lot_id = ""

            defect_qty = int(self.rng.integers(1, max(insp["failed_quantity"], 2)))
            defect_qty = min(defect_qty, insp["failed_quantity"])
            if defect_qty == 0:
                defect_qty = 1

            severity = str(self.rng.choice(DEFECT_SEVERITIES, p=DEFECT_SEVERITY_WEIGHTS))
            defect_type = str(self.rng.choice(DEFECT_TYPES))

            insp_date = datetime.strptime(insp["inspection_date"], "%Y-%m-%d")
            detect_date = random_date_after(self.rng, insp_date, max_days=3)

            root_causes = [
                "Material property variation",
                "Tool wear beyond threshold",
                "Process parameter drift",
                "Operator technique variation",
                "Thermal expansion variance",
                "Supplier incoming batch defect",
                "Calibration offset",
                None,
            ]

            defects.append({
                "defect_id": f"DEF-{YEAR}-{self._defect_counter:06d}",
                "inspection_id": insp["inspection_id"],
                "order_id": oid,
                "lot_id": lot_id,
                "step_id": step_id,
                "defect_type": defect_type,
                "severity": severity,
                "defect_quantity": defect_qty,
                "description": f"{defect_type} identified during inspection {insp['inspection_id']}",
                "detection_date": detect_date.strftime("%Y-%m-%d"),
                "root_cause": self.rng.choice(root_causes),
                "status": str(self.rng.choice(
                    ["Open", "Under Investigation", "Contained", "Resolved"],
                    p=[0.15, 0.20, 0.25, 0.40]
                )),
            })

        df_defects = pd.DataFrame(defects)
        self.data["defects"] = df_defects
        print(f"  [7/8] Defects: {len(df_defects):,}")

    # ---------------------------------------------------------------
    #  8. Corrective Actions (CAPA)
    # ---------------------------------------------------------------
    def generate_corrective_actions(self):
        """Generate corrective_actions.csv linked to defects."""
        defects = self.data["defects"]
        capas = []
        self._capa_counter = 0

        for _, defect in defects.iterrows():
            if self.rng.random() > 0.85:
                continue

            self._capa_counter += 1
            detect_date = datetime.strptime(defect["detection_date"], "%Y-%m-%d")
            action_type = str(self.rng.choice(CAPA_ACTION_TYPES))
            target = detect_date + timedelta(days=int(self.rng.integers(7, 90)))

            status_roll = float(self.rng.random())
            if status_roll < 0.15:
                status = "Open"
                comp_date = None
                verif_date = None
                eff = None
            elif status_roll < 0.35:
                status = "In Progress"
                comp_date = None
                verif_date = None
                eff = None
            elif status_roll < 0.55:
                status = "Pending Verification"
                comp_dt = random_date_after(self.rng, detect_date, 45)
                comp_date = comp_dt.strftime("%Y-%m-%d")
                verif_date = None
                eff = None
            else:
                status = "Closed"
                comp_dt = random_date_after(self.rng, detect_date, 40)
                comp_date = comp_dt.strftime("%Y-%m-%d")
                verif_dt = random_date_after(self.rng, comp_dt, 30)
                verif_date = verif_dt.strftime("%Y-%m-%d")
                eff = str(self.rng.choice(
                    ["Effective", "Partially Effective", "Not Effective"],
                    p=[0.75, 0.18, 0.07]
                ))

            capas.append({
                "capa_id": f"CAPA-{YEAR}-{self._capa_counter:06d}",
                "defect_id": defect["defect_id"],
                "action_type": action_type,
                "description": f"{action_type} addressing {defect['defect_type']} ({defect['severity']})",
                "assigned_to": f"EMP-{self.rng.integers(1000, 9999):04d}",
                "target_date": target.strftime("%Y-%m-%d"),
                "completion_date": comp_date,
                "verification_date": verif_date,
                "status": status,
                "effectiveness": eff,
            })

        df_capas = pd.DataFrame(capas)
        self.data["corrective_actions"] = df_capas
        print(f"  [8/8] Corrective Actions: {len(df_capas):,}")

    # ---------------------------------------------------------------
    #  ANOMALY INJECTION
    # ---------------------------------------------------------------
    def inject_anomalies(self):
        """Inject controlled, labelled anomalies recorded exclusively in ground_truth.csv."""
        n = self.params["anomaly_count_per_type"]
        now_str = datetime(YEAR, 10, 22, 12, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
        anom_idx = 0

        print(f"\n  Injecting anomalies ({n} per type)...")

        # 1. Defect linked to non-existent MaterialLot
        defects = self.data["defects"]
        if len(defects) >= n:
            target_indices = self.rng.choice(defects.index, size=n, replace=False)
            for idx in target_indices:
                anom_idx += 1
                fake_lot = f"LOT-SUP-999999-{YEAR}-{anom_idx:06d}"
                orig_lot = defects.at[idx, "lot_id"]
                defects.at[idx, "lot_id"] = fake_lot
                self.anomalies.append({
                    "anomaly_id": f"ANOM-{anom_idx:04d}",
                    "anomaly_type": AnomalyType.PHANTOM_LOT,
                    "entity_type": "defects",
                    "entity_id": defects.at[idx, "defect_id"],
                    "field_name": "lot_id",
                    "anomalous_value": fake_lot,
                    "expected_behavior": f"lot_id should reference an existing material lot (original: {orig_lot})",
                    "injected_at": now_str,
                })
            self.data["defects"] = defects

        # 2. BOM component that was never consumed in any order
        bom = self.data["bom"]
        if len(bom) >= n:
            target_indices = self.rng.choice(bom.index, size=n, replace=False)
            for idx in target_indices:
                anom_idx += 1
                fake_mat = f"Unconsumed-Alloy-{anom_idx:03d}"
                orig_mat = bom.at[idx, "material_name"]
                bom.at[idx, "material_name"] = fake_mat
                self.anomalies.append({
                    "anomaly_id": f"ANOM-{anom_idx:04d}",
                    "anomaly_type": AnomalyType.UNCONSUMED_BOM,
                    "entity_type": "bom",
                    "entity_id": bom.at[idx, "bom_id"],
                    "field_name": "material_name",
                    "anomalous_value": fake_mat,
                    "expected_behavior": f"BOM component should be consumed in production orders (original: {orig_mat})",
                    "injected_at": now_str,
                })
            self.data["bom"] = bom

        # 3. CAPA closed before verification
        capas = self.data["corrective_actions"]
        non_closed = capas[capas["status"] != "Closed"]
        if len(non_closed) >= n:
            target_indices = self.rng.choice(non_closed.index, size=n, replace=False)
            for idx in target_indices:
                anom_idx += 1
                capas.at[idx, "status"] = "Closed"
                capas.at[idx, "verification_date"] = None
                self.anomalies.append({
                    "anomaly_id": f"ANOM-{anom_idx:04d}",
                    "anomaly_type": AnomalyType.PREMATURE_CAPA_CLOSE,
                    "entity_type": "corrective_actions",
                    "entity_id": capas.at[idx, "capa_id"],
                    "field_name": "status",
                    "anomalous_value": "Closed (verification_date is NULL)",
                    "expected_behavior": "CAPA status can become 'Closed' only after verification_date is populated",
                    "injected_at": now_str,
                })
            self.data["corrective_actions"] = capas

        # 4. Defect quantity > inspected quantity
        defects = self.data["defects"]
        results = self.data["inspection_results"]
        insp_qty_map = dict(zip(results["inspection_id"], results["inspected_quantity"]))

        used_defect_ids = {a["entity_id"] for a in self.anomalies if a["entity_type"] == "defects"}
        available_defects = defects[~defects["defect_id"].isin(used_defect_ids)]

        if len(available_defects) >= n:
            target_indices = self.rng.choice(available_defects.index, size=n, replace=False)
            for idx in target_indices:
                anom_idx += 1
                insp_id = defects.at[idx, "inspection_id"]
                insp_qty = insp_qty_map.get(insp_id, 20)
                excess_qty = int(insp_qty) + int(self.rng.integers(10, 50))
                orig_qty = defects.at[idx, "defect_quantity"]
                defects.at[idx, "defect_quantity"] = excess_qty
                self.anomalies.append({
                    "anomaly_id": f"ANOM-{anom_idx:04d}",
                    "anomaly_type": AnomalyType.EXCESS_DEFECT_QTY,
                    "entity_type": "defects",
                    "entity_id": defects.at[idx, "defect_id"],
                    "field_name": "defect_quantity",
                    "anomalous_value": str(excess_qty),
                    "expected_behavior": f"defect_quantity ({excess_qty}) must be <= inspected_quantity ({insp_qty}, was {orig_qty})",
                    "injected_at": now_str,
                })
            self.data["defects"] = defects

        # 5. Broken traceability chain (missing/invalid process step)
        defects = self.data["defects"]
        used_defect_ids = {a["entity_id"] for a in self.anomalies if a["entity_type"] == "defects"}
        available_defects = defects[~defects["defect_id"].isin(used_defect_ids)]

        if len(available_defects) >= n:
            target_indices = self.rng.choice(available_defects.index, size=n, replace=False)
            for idx in target_indices:
                anom_idx += 1
                broken_step = f"STEP-WO-{YEAR}-999999-999"
                orig_step = defects.at[idx, "step_id"]
                defects.at[idx, "step_id"] = broken_step
                self.anomalies.append({
                    "anomaly_id": f"ANOM-{anom_idx:04d}",
                    "anomaly_type": AnomalyType.BROKEN_CHAIN,
                    "entity_type": "defects",
                    "entity_id": defects.at[idx, "defect_id"],
                    "field_name": "step_id",
                    "anomalous_value": broken_step,
                    "expected_behavior": f"step_id should reference an existing process step (original: {orig_step})",
                    "injected_at": now_str,
                })
            self.data["defects"] = defects

        print(f"  Total anomalies injected: {len(self.anomalies)}")

    # ---------------------------------------------------------------
    #  SAVE ALL DATA
    # ---------------------------------------------------------------
    def save_all(self):
        """Write all 13 DataFrames to CSV in the output directory."""
        print("\n  Saving CSV files...")
        file_map = {
            "products": "products.csv",
            "bom": "bom.csv",
            "suppliers": "suppliers.csv",
            "material_lots": "material_lots.csv",
            "production_orders": "production_orders.csv",
            "order_lot_consumption": "order_lot_consumption.csv",
            "machines": "machines.csv",
            "process_steps": "process_steps.csv",
            "inspection_plans": "inspection_plans.csv",
            "inspection_results": "inspection_results.csv",
            "defects": "defects.csv",
            "corrective_actions": "corrective_actions.csv",
        }
        for key, filename in file_map.items():
            path = self.output_dir / filename
            self.data[key].to_csv(path, index=False)

        df_gt = pd.DataFrame(self.anomalies)
        df_gt.to_csv(self.output_dir / "ground_truth.csv", index=False)
        self.data["ground_truth"] = df_gt
        print(f"  Saved {len(file_map) + 1} CSV files to {self.output_dir}/")

    # ---------------------------------------------------------------
    #  VALIDATION
    # ---------------------------------------------------------------
    def validate(self) -> list[dict]:
        """Run comprehensive validation and return results."""
        print("\n" + "=" * 60)
        print("  AUTOMATED VALIDATION SUITE")
        print("=" * 60)
        results = []

        # 1. Primary Key Uniqueness
        pk_map = {
            "products": "sku_id",
            "bom": "bom_id",
            "suppliers": "supplier_id",
            "material_lots": "lot_id",
            "production_orders": "order_id",
            "machines": "machine_id",
            "process_steps": "step_id",
            "inspection_plans": "plan_id",
            "inspection_results": "inspection_id",
            "defects": "defect_id",
            "corrective_actions": "capa_id",
            "ground_truth": "anomaly_id",
        }
        for table, pk in pk_map.items():
            df = self.data[table]
            is_unique = df[pk].is_unique
            results.append({
                "check": f"PK uniqueness: {table}.{pk}",
                "status": "PASS" if is_unique else "FAIL",
                "detail": f"{len(df):,} rows, {df[pk].nunique():,} unique"
            })

        # Bridge table composite key uniqueness
        cons = self.data["order_lot_consumption"]
        comp_unique = not cons.duplicated(subset=["order_id", "lot_id", "material_name"]).any()
        results.append({
            "check": "Composite key: order_lot_consumption.(order_id, lot_id, material_name)",
            "status": "PASS" if comp_unique else "FAIL",
            "detail": f"{len(cons):,} rows, {len(cons.drop_duplicates(subset=['order_id', 'lot_id', 'material_name'])):,} unique"
        })

        # 2. Foreign Key Integrity
        anomaly_defect_ids = {a["entity_id"] for a in self.anomalies if a["entity_type"] == "defects"}
        anomaly_bom_ids = {a["entity_id"] for a in self.anomalies if a["entity_type"] == "bom"}

        standard_fks = [
            ("bom", "sku_id", "products", "sku_id", anomaly_bom_ids, "bom_id"),
            ("material_lots", "supplier_id", "suppliers", "supplier_id", set(), None),
            ("production_orders", "sku_id", "products", "sku_id", set(), None),
            ("order_lot_consumption", "order_id", "production_orders", "order_id", set(), None),
            ("order_lot_consumption", "lot_id", "material_lots", "lot_id", set(), None),
            ("process_steps", "order_id", "production_orders", "order_id", set(), None),
            ("process_steps", "machine_id", "machines", "machine_id", set(), None),
            ("inspection_plans", "sku_id", "products", "sku_id", set(), None),
            ("inspection_results", "order_id", "production_orders", "order_id", set(), None),
            ("inspection_results", "plan_id", "inspection_plans", "plan_id", set(), None),
            ("corrective_actions", "defect_id", "defects", "defect_id", set(), None),
        ]

        for child_tbl, child_col, parent_tbl, parent_col, excl_ids, excl_pk in standard_fks:
            child_df = self.data[child_tbl]
            parent_df = self.data[parent_tbl]
            if excl_ids and excl_pk:
                child_df = child_df[~child_df[excl_pk].isin(excl_ids)]

            child_vals = set(child_df[child_col].dropna().unique())
            parent_vals = set(parent_df[parent_col].unique())
            orphans = child_vals - parent_vals

            results.append({
                "check": f"FK integrity: {child_tbl}.{child_col} -> {parent_tbl}.{parent_col}",
                "status": "PASS" if len(orphans) == 0 else "FAIL",
                "detail": f"{len(orphans)} orphan(s)"
            })

        # Defect FKs (excluding labelled anomalies)
        clean_defects = self.data["defects"][~self.data["defects"]["defect_id"].isin(anomaly_defect_ids)]

        for child_col, parent_tbl, parent_col in [
            ("inspection_id", "inspection_results", "inspection_id"),
            ("order_id", "production_orders", "order_id"),
        ]:
            child_vals = set(clean_defects[child_col].dropna().unique())
            parent_vals = set(self.data[parent_tbl][parent_col].unique())
            orphans = child_vals - parent_vals
            results.append({
                "check": f"FK integrity: defects.{child_col} -> {parent_tbl}.{parent_col} (clean)",
                "status": "PASS" if len(orphans) == 0 else "FAIL",
                "detail": f"{len(orphans)} orphan(s)"
            })

        # Defect lot_id FK (excluding phantom lot anomalies)
        phantom_ids = {a["entity_id"] for a in self.anomalies if a["anomaly_type"] == AnomalyType.PHANTOM_LOT}
        defects_no_phantom = self.data["defects"][~self.data["defects"]["defect_id"].isin(phantom_ids)]
        lot_vals = set(defects_no_phantom["lot_id"].dropna()[defects_no_phantom["lot_id"].dropna() != ""].unique())
        lot_parent_vals = set(self.data["material_lots"]["lot_id"].unique())
        lot_orphans = lot_vals - lot_parent_vals
        results.append({
            "check": "FK integrity: defects.lot_id -> material_lots.lot_id (excl phantom anomalies)",
            "status": "PASS" if len(lot_orphans) == 0 else "FAIL",
            "detail": f"{len(lot_orphans)} orphan(s)"
        })

        # Defect step_id FK (excluding broken chain anomalies)
        broken_ids = {a["entity_id"] for a in self.anomalies if a["anomaly_type"] == AnomalyType.BROKEN_CHAIN}
        defects_no_broken = self.data["defects"][~self.data["defects"]["defect_id"].isin(broken_ids)]
        step_vals = set(defects_no_broken["step_id"].dropna()[defects_no_broken["step_id"].dropna() != ""].unique())
        step_parent_vals = set(self.data["process_steps"]["step_id"].unique())
        step_orphans = step_vals - step_parent_vals
        results.append({
            "check": "FK integrity: defects.step_id -> process_steps.step_id (excl broken chain)",
            "status": "PASS" if len(step_orphans) == 0 else "FAIL",
            "detail": f"{len(step_orphans)} orphan(s)"
        })

        # 3. Quantity Reconciliation
        lots = self.data["material_lots"]
        consumed_totals = cons.groupby("lot_id")["quantity_consumed"].sum().to_dict()
        qty_violations = 0
        rem_violations = 0
        for _, row in lots.iterrows():
            lid = row["lot_id"]
            orig = row["quantity"]
            tot_consumed = consumed_totals.get(lid, 0.0)
            if tot_consumed > orig + 0.01:
                qty_violations += 1
            expected_rem = round(max(0.0, orig - tot_consumed), 3)
            if abs(row["remaining_quantity"] - expected_rem) > 0.01:
                rem_violations += 1

        results.append({
            "check": "Quantity reconciliation: consumed <= lot original quantity",
            "status": "PASS" if qty_violations == 0 else "FAIL",
            "detail": f"{qty_violations} lot(s) over-consumed"
        })
        results.append({
            "check": "Quantity reconciliation: remaining_quantity = original - consumed",
            "status": "PASS" if rem_violations == 0 else "FAIL",
            "detail": f"{rem_violations} mismatch(es)"
        })

        # 4. Date Ordering
        orders = self.data["production_orders"]
        ord_date_violations = (pd.to_datetime(orders["start_date"]) > pd.to_datetime(orders["end_date"])).sum()
        results.append({
            "check": "Date ordering: order start <= end",
            "status": "PASS" if ord_date_violations == 0 else "FAIL",
            "detail": f"{ord_date_violations} violation(s)"
        })

        steps = self.data["process_steps"]
        step_date_violations = (pd.to_datetime(steps["start_time"]) > pd.to_datetime(steps["end_time"])).sum()
        results.append({
            "check": "Date ordering: step start <= end",
            "status": "PASS" if step_date_violations == 0 else "FAIL",
            "detail": f"{step_date_violations} violation(s)"
        })

        results_df = self.data["inspection_results"]
        order_dates = dict(zip(orders["order_id"], zip(pd.to_datetime(orders["start_date"]), pd.to_datetime(orders["end_date"]))))
        insp_violations = 0
        for _, row in results_df.iterrows():
            dates = order_dates.get(row["order_id"])
            if dates:
                idate = pd.to_datetime(row["inspection_date"])
                if idate < dates[0] or idate > dates[1] + timedelta(days=1):
                    insp_violations += 1
        results.append({
            "check": "Date ordering: inspection_date within order start/end range",
            "status": "PASS" if insp_violations == 0 else "FAIL",
            "detail": f"{insp_violations} violation(s)"
        })

        defects_df = self.data["defects"]
        insp_dates = dict(zip(results_df["inspection_id"], pd.to_datetime(results_df["inspection_date"])))
        defect_date_violations = 0
        for _, row in defects_df.iterrows():
            idate = insp_dates.get(row["inspection_id"])
            if idate and pd.to_datetime(row["detection_date"]) < idate:
                defect_date_violations += 1
        results.append({
            "check": "Date ordering: defect detection_date >= inspection_date",
            "status": "PASS" if defect_date_violations == 0 else "FAIL",
            "detail": f"{defect_date_violations} violation(s)"
        })

        capas_df = self.data["corrective_actions"]
        both_dates = capas_df.dropna(subset=["completion_date", "verification_date"])
        capa_date_violations = (pd.to_datetime(both_dates["completion_date"]) > pd.to_datetime(both_dates["verification_date"])).sum()
        results.append({
            "check": "Date ordering: CAPA completion_date <= verification_date",
            "status": "PASS" if capa_date_violations == 0 else "FAIL",
            "detail": f"{capa_date_violations} violation(s)"
        })

        # 5. Lifecycle Rules
        premature_capa_ids = {a["entity_id"] for a in self.anomalies if a["anomaly_type"] == AnomalyType.PREMATURE_CAPA_CLOSE}
        clean_capas = capas_df[~capas_df["capa_id"].isin(premature_capa_ids)]
        closed_no_verif = clean_capas[
            (clean_capas["status"] == "Closed") &
            (clean_capas["verification_date"].isna() | (clean_capas["verification_date"] == ""))
        ]
        results.append({
            "check": "Lifecycle: Closed CAPA has verification_date (clean records)",
            "status": "PASS" if len(closed_no_verif) == 0 else "FAIL",
            "detail": f"{len(closed_no_verif)} violation(s)"
        })

        excess_defect_ids = {a["entity_id"] for a in self.anomalies if a["anomaly_type"] == AnomalyType.EXCESS_DEFECT_QTY}
        clean_defects_qty = defects_df[~defects_df["defect_id"].isin(excess_defect_ids)]
        insp_qty_lookup = dict(zip(results_df["inspection_id"], results_df["inspected_quantity"]))
        defect_qty_violations = 0
        for _, row in clean_defects_qty.iterrows():
            iqty = insp_qty_lookup.get(row["inspection_id"], float("inf"))
            if row["defect_quantity"] > iqty:
                defect_qty_violations += 1
        results.append({
            "check": "Lifecycle: defect_quantity <= inspected_quantity (clean records)",
            "status": "PASS" if defect_qty_violations == 0 else "FAIL",
            "detail": f"{defect_qty_violations} violation(s)"
        })

        # 6. Anomaly Verification
        gt = self.data["ground_truth"]
        expected_types = [
            AnomalyType.PHANTOM_LOT,
            AnomalyType.UNCONSUMED_BOM,
            AnomalyType.PREMATURE_CAPA_CLOSE,
            AnomalyType.EXCESS_DEFECT_QTY,
            AnomalyType.BROKEN_CHAIN,
        ]
        for atype in expected_types:
            count = len(gt[gt["anomaly_type"] == atype])
            results.append({
                "check": f"Anomaly inventory: {atype}",
                "status": "PASS" if count == self.params["anomaly_count_per_type"] else "FAIL",
                "detail": f"{count} injected (expected {self.params['anomaly_count_per_type']})"
            })

        pass_count = sum(1 for r in results if r["status"] == "PASS")
        fail_count = sum(1 for r in results if r["status"] == "FAIL")

        for r in results:
            tag = "[PASS]" if r["status"] == "PASS" else "[FAIL]"
            print(f"  {tag} {r['check']} -- {r['detail']}")

        print(f"\n  Validation Results: {pass_count} passed, {fail_count} failed out of {len(results)} checks.")
        self._validation_results = results
        return results

    # ---------------------------------------------------------------
    #  WRITE VALIDATION REPORT
    # ---------------------------------------------------------------
    def write_validation_report(self, validation_dir: Path):
        """Write validation/validation_report.md markdown file."""
        validation_dir.mkdir(parents=True, exist_ok=True)
        report_path = validation_dir / "validation_report.md"

        pass_count = sum(1 for r in self._validation_results if r["status"] == "PASS")
        total = len(self._validation_results)
        verdict = "ALL CHECKS PASSED" if pass_count == total else f"{total - pass_count} CHECKS FAILED"

        lines = [
            "# Manufacturing Defect Traceability - Validation Report",
            "",
            f"- **Execution Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **Scale Configuration:** `{self.scale}`",
            f"- **Random Seed:** `{self.seed}`",
            f"- **Overall Verdict:** **{verdict}** ({pass_count}/{total} checks passed)",
            "",
            "---",
            "",
            "## 1. Table Volume and Entity Counts",
            "",
            "| Entity / Table | Primary Key | Total Records | File Size (Bytes) |",
            "|----------------|-------------|---------------|-------------------|",
        ]

        file_keys = [
            ("products", "products.csv", "sku_id"),
            ("bom", "bom.csv", "bom_id"),
            ("suppliers", "suppliers.csv", "supplier_id"),
            ("material_lots", "material_lots.csv", "lot_id"),
            ("production_orders", "production_orders.csv", "order_id"),
            ("order_lot_consumption", "order_lot_consumption.csv", "(order_id, lot_id, material_name)"),
            ("machines", "machines.csv", "machine_id"),
            ("process_steps", "process_steps.csv", "step_id"),
            ("inspection_plans", "inspection_plans.csv", "plan_id"),
            ("inspection_results", "inspection_results.csv", "inspection_id"),
            ("defects", "defects.csv", "defect_id"),
            ("corrective_actions", "corrective_actions.csv", "capa_id"),
            ("ground_truth", "ground_truth.csv", "anomaly_id"),
        ]

        for entity, filename, pk in file_keys:
            df = self.data[entity]
            fpath = self.output_dir / filename
            fsize = fpath.stat().st_size if fpath.exists() else 0
            lines.append(f"| `{filename}` | `{pk}` | {len(df):,} | {fsize:,} |")

        lines += [
            "",
            "---",
            "",
            "## 2. Primary Key Uniqueness",
            "",
            "| Check | Status | Verification Detail |",
            "|-------|--------|---------------------|",
        ]
        for r in self._validation_results:
            if "PK uniqueness" in r["check"] or "Composite key" in r["check"]:
                lines.append(f"| {r['check']} | **{r['status']}** | {r['detail']} |")

        lines += [
            "",
            "---",
            "",
            "## 3. Foreign Key Integrity",
            "",
            "| Relationship | Status | Orphans Detected |",
            "|-------------|--------|------------------|",
        ]
        for r in self._validation_results:
            if "FK integrity" in r["check"]:
                clean_name = r["check"].replace("FK integrity: ", "")
                lines.append(f"| {clean_name} | **{r['status']}** | {r['detail']} |")

        lines += [
            "",
            "---",
            "",
            "## 4. Quantity Reconciliation",
            "",
            "| Check | Status | Detail |",
            "|-------|--------|--------|",
        ]
        for r in self._validation_results:
            if "Quantity reconciliation" in r["check"]:
                clean_name = r["check"].replace("Quantity reconciliation: ", "")
                lines.append(f"| {clean_name} | **{r['status']}** | {r['detail']} |")

        lines += [
            "",
            "---",
            "",
            "## 5. Chronological Date Ordering",
            "",
            "| Chronological Constraint | Status | Violations |",
            "|-------------------------|--------|------------|",
        ]
        for r in self._validation_results:
            if "Date ordering" in r["check"]:
                clean_name = r["check"].replace("Date ordering: ", "")
                lines.append(f"| {clean_name} | **{r['status']}** | {r['detail']} |")

        lines += [
            "",
            "---",
            "",
            "## 6. Business Lifecycle Rules",
            "",
            "| Rule | Status | Detail |",
            "|------|--------|--------|",
        ]
        for r in self._validation_results:
            if "Lifecycle" in r["check"]:
                clean_name = r["check"].replace("Lifecycle: ", "")
                lines.append(f"| {clean_name} | **{r['status']}** | {r['detail']} |")

        lines += [
            "",
            "---",
            "",
            "## 7. Anomaly Inventory (Ground Truth Audit)",
            "",
            "| Anomaly Type | Injected Count | Status |",
            "|--------------|----------------|--------|",
        ]
        for r in self._validation_results:
            if "Anomaly inventory" in r["check"]:
                clean_name = r["check"].replace("Anomaly inventory: ", "")
                lines.append(f"| `{clean_name}` | {r['detail']} | **{r['status']}** |")

        lines += [
            "",
            "---",
            "",
            "## 8. Cryptographic File Checksums (SHA-256)",
            "",
            "| File Name | SHA-256 Checksum |",
            "|-----------|------------------|",
        ]
        for f in sorted(self.output_dir.glob("*.csv")):
            h = sha256_file(f)
            lines.append(f"| `{f.name}` | `{h}` |")

        report_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"\n  Validation report generated at: {report_path}")

    # ---------------------------------------------------------------
    #  SUMMARY PRINT
    # ---------------------------------------------------------------
    def print_summary(self):
        """Print final summary with row counts, checksums, and validation status."""
        print("\n" + "=" * 60)
        print("  GENERATION COMPLETE - SUMMARY REPORT")
        print("=" * 60)
        print(f"  Scale: {self.scale}  |  Seed: {self.seed}")
        print()

        print("  Table Row Counts:")
        print("  " + "-" * 50)
        for name, df in self.data.items():
            print(f"    {name + '.csv':<30s} : {len(df):>8,} rows")

        print()
        print("  File SHA-256 Checksums:")
        print("  " + "-" * 50)
        for f in sorted(self.output_dir.glob("*.csv")):
            h = sha256_file(f)
            print(f"    {f.name:<26s} : {h[:24]}...{h[-8:]}")

        pass_count = sum(1 for r in self._validation_results if r["status"] == "PASS")
        total = len(self._validation_results)
        print()
        if pass_count == total:
            print(f"  >> VALIDATION RESULT: [PASS] All {total} checks passed successfully.")
        else:
            print(f"  >> VALIDATION RESULT: [FAIL] {total - pass_count}/{total} checks failed.")
        print("=" * 60)

    # ---------------------------------------------------------------
    #  RUN ORCHESTRATOR
    # ---------------------------------------------------------------
    def run(self):
        """Run the full data generation and validation pipeline."""
        print("=" * 60)
        print("  Manufacturing Defect Traceability Synthetic Data Generator")
        print(f"  Configuration: scale={self.scale}, seed={self.seed}")
        print("=" * 60)
        print("\n  Executing generation sequence (parent -> child)...")

        # 1. Products & BOM
        self.generate_products_and_bom()
        # 2. Suppliers & Machines
        self.generate_suppliers_and_machines()
        # 3. Material Lots
        self.generate_material_lots()
        # 4. Production Orders + Consumption
        self.generate_production_orders()
        # 5. Process Steps
        self.generate_process_steps()
        # 6. Inspections
        self.generate_inspections()
        # 7. Defects
        self.generate_defects()
        # 8. Corrective Actions
        self.generate_corrective_actions()

        # Controlled anomaly injection
        self.inject_anomalies()

        # Save all generated files
        self.save_all()

        # Run automated validation suite
        self.validate()

        # Generate validation report
        project_root = self.output_dir.parent
        self.write_validation_report(project_root / "validation")

        # Print final console summary
        self.print_summary()


# ===================================================================
#  CLI ENTRY POINT
# ===================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic manufacturing defect traceability data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python generate_data.py --scale full  --seed 20261022
              python generate_data.py --scale small --seed 20261022
              python generate_data.py
        """),
    )
    parser.add_argument(
        "--scale",
        choices=["full", "small"],
        default="full",
        help="Data volume scale preset (default: full)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"Random seed for deterministic reproducibility (default: {DEFAULT_SEED})",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Custom output directory for CSV files (default: ./data)",
    )

    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = script_dir / "data"

    generator = TraceabilityDataGenerator(
        scale=args.scale,
        seed=args.seed,
        output_dir=output_dir,
    )
    generator.run()


if __name__ == "__main__":
    main()
