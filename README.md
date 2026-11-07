# BizGuard AI — Autonomous Business Reliability & Recovery Platform
### *Specialized for Premium Clothing E-Commerce*

BizGuard AI is an autonomous business reliability and self-healing platform engineered for modern clothing e-commerce brands. It monitors end-to-end commerce sagas, detects invariant violations, conducts multi-agent forensic investigations, formulates atomic compensating recovery plans, runs automated pre-checks, and securely executes approved fixes with mandatory human supervisor oversight.

---

## 🌟 The Core Problem & Primary Demo Scenario

In apparel e-commerce, **inventory isolation across size and color variants is critical**. A customer buying a **Black Kurti in Size M** must never receive Size L. 

### The Real-World Bug:
1. **Customer Order**: Priya Sharma orders an *Anarkali Embroidered Black Kurti* in **Size M** (Value: ₹2,500).
2. **Payment Captured**: Payment is successfully captured via Razorpay Mock.
3. **Inventory Misallocation**: A warehouse bin scan anomaly mistakenly reserves **Size L** (`BG-KRT-BLK-L`) instead of **Size M** (`BG-KRT-BLK-M`).
4. **Order Stalled**: The fulfillment workflow halts at `STALLED_INCONSISTENT` — customer is charged, but packing is blocked.

### Switch AI & Multi-Agent Intelligence

BizGuard AI uses **Switch AI** to power intelligent workflows through multiple specialised AI agents. Each agent handles a dedicated business task, collaborating to analyse problems, generate insights, and support smarter decisions.

**What makes it unique?** Instead of relying on a single AI assistant, BizGuard AI brings multiple agents together in one unified platform, combining automation, business intelligence, and a distinctive, interactive UI/UX to deliver a more intelligent business management experience.

### The BizGuard AI 12-Step Autonomous Recovery Solution:
1. **Detection**: `InvariantDetector` flags `RULE_VARIANT_INVENTORY_MISMATCH`.
2. **Incident Creation**: Creates incident `INC-2026-XXXX` with forensic blast-radius analysis.
3. **Monitor Agent**: Confirms live database invariant violation.
4. **Investigator Agent**: Gathers order, line item, and inventory evidence; analyzes root cause.
5. **Developer Agent**: Formulates a safe, atomic compensating transaction with rollback steps.
6. **Tester Agent**: Executes automated pre-condition checks directly against the database.
7. **Auditor Agent**: Delivers an independent risk assessment and compliance review.
8. **Approval Center**: Presents before-and-after comparison to the human business manager.
9. **Supervisor Approval**: Human supervisor approves and signs the proposal with a SHA-256 cryptographic digest.
10. **Compensating Execution**: Atomic swap releases Size L reservation and secures Size M reservation.
11. **Independent Post-Verification**: Engine verifies final database state directly before closing.
12. **Incident Closure**: Workflow resumes to `INVOICED`, and incident is marked `VERIFIED_RESOLVED`.

---

## 🏗️ Architecture & Specialized AI Agents

```
                        ┌─────────────────────────────────────┐
                        │      Customer Storefront / API      │
                        └──────────────────┬──────────────────┘
                                           │
                        ┌──────────────────▼──────────────────┐
                        │     PostgreSQL / SQLite Engine      │
                        │    (19 Normalized Data Models)      │
                        └──────────────────┬──────────────────┘
                                           │
                        ┌──────────────────▼──────────────────┐
                        │      Rule-Based Invariant Engine    │
                        │  (6 Core E-Commerce Failure Rules)  │
                        └──────────────────┬──────────────────┘
                                           │
 ┌─────────────────────────────────────────┴─────────────────────────────────────────┐
 │                                   AI WAR ROOM                                     │
 │  ┌───────────────────┐  ┌──────────────────────┐  ┌─────────────────────────────┐ │
 │  │   @monitor-agent  │  │ @investigator-agent  │  │      @developer-agent       │ │
 │  │ Scans invariants &│  │ Forensic evidence    │  │ Creates atomic compensating │ │
 │  │ creates incidents │  │ & root cause analysis│  │ actions & rollback plan     │ │
 │  └───────────────────┘  └──────────────────────┘  └─────────────────────────────┘ │
 │                 ▲                                                 │               │
 │                 │               Switch Protocol                   │               │
 │                 │          (ws://127.0.0.1:8765/switch-bus)       ▼               │
 │  ┌──────────────┴────┐                               ┌──────────────────────────┐ │
 │  │   @auditor-agent  │                               │       @tester-agent      │ │
 │  │ Compliance audit &│◄──────────────────────────────┤ Runs DB pre-check queries│ │
 │  │ safety score (98) │                               │ to validate preconditions│ │
 │  └─────────┬─────────┘                               └──────────────────────────┘ │
 └────────────┼──────────────────────────────────────────────────────────────────────┘
              │
              ▼
 ┌─────────────────────────┐         ┌─────────────────────────┐
 │     APPROVAL CENTER     │────────►│  RECOVERY EXECUTION &   │
 │ Human Manager Sign-off  │         │ INDEPENDENT VERIFY (DB) │
 └─────────────────────────┘         └─────────────────────────┘
```

---

## 🛡️ Backend Safety Principles

- **No Execution Without Human Approval**: `RecoveryService.execute_approved_proposal` rejects any unapproved proposal.
- **Automated Testing Gate**: Human managers cannot approve proposals if automated pre-checks have not passed.
- **Rejection Safety**: If a proposal is rejected, all automated actions are permanently blocked.
- **Tamper-Proof Signatures**: Every decision is bound to the proposal version with a SHA-256 digest (`proposal_id + code + decision + approver + timestamp`).
- **Idempotency & Replay Protection**: Proposals cannot be executed more than once.
- **Independent Verification**: After the atomic compensating swap, stock levels and order states are re-queried to confirm consistency before marking incidents resolved.

---

## 🚨 11 Failure Simulation Scenarios

BizGuard AI includes a dedicated demo failure panel on `/bugs` with 1-click injection:

| Category | Scenario | Rule Triggered |
|---|---|---|
| **Business Logic** | Black Kurti Size M vs L Mismatch | `RULE_VARIANT_INVENTORY_MISMATCH` |
| **Business Logic** | Wrong Color Stock Reservation | `RULE_COLOR_INVENTORY_MISMATCH` |
| **Business Logic** | Negative Available Inventory | `RULE_NEGATIVE_INVENTORY` |
| **Business Logic** | Duplicate Payment (Charged Twice) | `RULE_DUPLICATE_PAYMENT` |
| **Business Logic** | Order Shipped Without Payment | `RULE_SHIPPED_WITHOUT_PAYMENT` |
| **Business Logic** | Out-of-Stock Variant Sold | `RULE_OUT_OF_STOCK_SOLD` |
| **Business Logic** | Invoice Amount Discrepancy | `RULE_INVOICE_AMOUNT_MISMATCH` |
| **Technical** | Inventory API Reservation Timeout | `RULE_PAYMENT_WITHOUT_INVENTORY` |
| **Technical** | Payment Gateway Webhook Sync Failure | `RULE_PAYMENT_SYNC_FAILURE` |
| **Technical** | Invoice Microservice Crash (OOM) | `RULE_INVENTORY_ALLOCATED_NO_INVOICE` |
| **Workflow** | Refund Not Synchronized on Approved Return | `RULE_REFUND_NOT_SYNCED` |

---

## 💻 Modules Overview

1. **Maison Vell Runway** (`/`): Immersive 3D runway depth lookbook with real-time model interpolation.
2. **Try the Look Runway** (`/runway`): Perspective streetwear outfit carousel with styling bag shortlist.
3. **Business Operations** (`/operations`): Product, Inventory, Orders, Payments, Invoices, Shipments, Returns overview.
4. **Product Management** (`/products`): 30 luxury clothing products across 5 categories.
5. **Inventory Center** (`/inventory`): Per-variant stock levels, bin tracking, low-stock alerts.
6. **Orders & Payments** (`/orders`, `/payments`): Real-time checkout sagas, transaction digests, status tracking.
7. **Workflow Monitor** (`/workflows`): Visual DAG node execution tracking from placement to delivery.
8. **Bug Detection** (`/bugs`): Invariant scanner & demo failure injection panel.
9. **AI War Room** (`/war-room`): 5-agent communication feed, task monitoring, and proposal handoff.
10. **Approval Center** (`/approvals`): Supervisor review, before-and-after comparison, cryptographic audit log.
11. **Reliability Analytics** (`/analytics`): Live MTTR, recovery success rates, and business impact charts.
12. **Settings** (`/settings`): Store configuration, agent parameters, Switch connection status.

---

## 🚀 Setup & Execution Guide

### Prerequisites
- Python 3.12+ (Virtual environment in `backend/.venv`)
- Node.js 20+ (Frontend in `frontend/`)
- (Optional) Docker & Docker Compose

### Option A: Local Development (Fastest)

1. **Seed Demo Dataset (30 Products, 119 Variants, Orders & Shipments)**:
   ```powershell
   .\backend\.venv\Scripts\python.exe scripts/seed_expanded_clothing_data.py
   ```

2. **Start Backend API (Port 8000)**:
   ```powershell
   $env:PYTHONPATH="backend"
   .\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000 --reload
   ```
   *Swagger Docs: `http://localhost:8000/docs`*

3. **Start Frontend (Port 3000)**:
   ```powershell
   cd frontend
   npm run dev
   ```
   *Maison Vell Storefront: `http://localhost:3000/`*  
   *Operations Console: `http://localhost:3000/operations`*

### Option B: Docker Compose

```bash
docker-compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

---

## 🧪 Comprehensive Quality Assurance (Test Report)

All 14 backend test suites and TypeScript checks pass with **100% success rate**:

```powershell
.\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_phase1.py backend/tests/test_phase2.py backend/tests/test_failure_scenarios.py backend/tests/test_full_recovery_lifecycle.py backend/tests/test_full_system_qa.py -v
```

```
============================= test session starts =============================
backend/tests/test_phase1.py::test_catalog_and_variants_loaded PASSED    [  7%]
backend/tests/test_phase1.py::test_variant_isolated_inventory PASSED     [ 14%]
backend/tests/test_phase1.py::test_clean_order_checkout_lifecycle PASSED [ 21%]
backend/tests/test_phase2.py::test_invariant_detection_finds_bug PASSED  [ 28%]
backend/tests/test_phase2.py::test_simulation_inject_and_reset PASSED    [ 35%]
backend/tests/test_phase2.py::test_recovery_proposal_created PASSED      [ 42%]
backend/tests/test_phase2.py::test_analytics_dashboard_returns_live_data PASSED [ 50%]
backend/tests/test_failure_scenarios.py::test_failure_scenarios_and_invariant_detection PASSED [ 57%]
backend/tests/test_full_recovery_lifecycle.py::test_complete_recovery_and_approval_flow PASSED [ 64%]
backend/tests/test_full_system_qa.py::test_catalog_and_inventory_isolation PASSED [ 71%]
backend/tests/test_full_system_qa.py::test_order_creation_and_inventory_reservation PASSED [ 78%]
backend/tests/test_full_system_qa.py::test_failure_simulation_scenarios PASSED [ 85%]
backend/tests/test_full_system_qa.py::test_invariant_detector_catches_all_anomalies PASSED [ 92%]
backend/tests/test_full_system_qa.py::test_ai_agent_orchestration_and_safety_pipeline PASSED [100%]
============================= 14 passed in 3.64s ==============================
```

- **Frontend Type Safety**: `npx tsc --noEmit` exited with **0 errors**.
- **REST Endpoints**: 49 validated API routes across all business and recovery modules.
