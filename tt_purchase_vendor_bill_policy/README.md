# Purchase Vendor Bill Policy

Adds a third configuration level for the purchase bill control policy in Odoo 17:
**Vendor (res.partner)** → **Purchase Order** → **Product** → Global setting.

## Why

Odoo 17 natively lets you define the bill control policy (`purchase_method`) on
the product or globally. In practice the policy depends mostly on the
**relationship with the vendor** — trust, commercial terms, payment cycle —
not on the product. This module fills that gap.

## What it does

* Adds a **Bill Control Policy** field on the vendor's contact card with three
  values: *Product Policy (default)*, *On Ordered Quantities*, *On Received
  Quantities*. Editable only by purchase managers. Per-company (a single vendor
  can have a different policy in subsidiary A and subsidiary B).
* The same field appears in the purchase order header, auto-filled from the
  selected vendor and re-resolved each time the vendor changes.
* Any purchase user can override the policy on a draft / sent / to-approve PO.
  The field becomes read-only once the PO is confirmed.
* The policy chosen on the PO is applied to every line. If the PO policy is
  *Product Policy*, each line falls back to its own product's `purchase_method`
  (native behavior).

## Decision priority

| Level | Source | Wins when |
|------|--------|-----------|
| 1 | Purchase Order (manual edit) | Set to `purchase` or `receive` |
| 2 | Vendor | Stamped on PO at creation / vendor change |
| 3 | Product | When PO policy is *Product Policy* |
| 4 | Global setting | Default for new products |

A vendor change on a PO **always** overrides any manual edit — the latest
vendor wins.

## Install

Plain `purchase` is the only dependency. No data migration. Existing POs keep
their native behavior until you edit them (the policy on existing POs resolves
to `product` on first read, preserving the native fallback).

```bash
# v17 EE
cd "C:/Antigravity Projects/Odoo_Projects/odoo_17.0+e.20260227"
venv/Scripts/python.exe -m odoo -c odoo.conf -d odoo17 -i tt_purchase_vendor_bill_policy --stop-after-init
```

## Tests

```bash
venv/Scripts/python.exe -m odoo -c odoo.conf -d odoo17 -u tt_purchase_vendor_bill_policy --test-enable --test-tags=/tt_purchase_vendor_bill_policy --stop-after-init
```

The suite covers: default values, partner→PO inheritance, manual override,
vendor-change override, product fallback, qty_to_invoice for all three policies,
copy semantics, and per-company independence.

## Permissions

* `purchase.group_purchase_manager` — edit the policy on the vendor contact
  **and** on any non-confirmed purchase order.
* `purchase.group_purchase_user` — see the policy on the vendor contact
  (read-only) and on every PO; edit it on a non-confirmed PO. Cannot edit the
  vendor's default policy.

The vendor field appears under **Sales & Purchase → Purchase** on the contact
form — visible to every purchase user, editable by managers only. The PO field
sits next to the *Vendor Reference* in the header and is read-only once the
order is confirmed (Purchase Order or Cancelled).

## How it compares to OCA's `purchase_invoice_method`

OCA's [`purchase_invoice_method`](https://github.com/OCA/purchase-workflow/tree/18.0/purchase_invoice_method)
solves a narrow slice of the same problem: it adds a single `invoice_method`
field on `purchase.order` that lets the user override the per-product policy
on a per-order basis. It's lightweight (~16 lines of model code) and useful
when all you need is the manual override.

This module covers a broader scope — the bill control policy is **driven by
the vendor relationship**, not just decided on each order. Side-by-side:

| Capability | OCA `purchase_invoice_method` | `tt_purchase_vendor_bill_policy` |
|------------|:-----------------------------:|:--------------------------------:|
| Override the policy on a single PO | ✅ | ✅ |
| Define a **default policy on the vendor record** | ❌ | ✅ |
| Auto-fill the PO from the vendor's default | ❌ | ✅ |
| Vendor change on a PO overrides any manual edit (RG-06) | ❌ | ✅ |
| Explicit "Product Policy" fallback option on the PO | ❌ | ✅ |
| Multi-company (per-company policy on the same vendor) | ❌ | ✅ |
| Manager-vs-User permission split on the vendor field | ❌ | ✅ |
| Read-only lockdown after PO confirmation | ❌ | ✅ |
| Translations (French, Arabic) | ❌ | ✅ |
| Automated test suite | ❌ | ✅ (14 tests) |
| Status | Beta | Production-ready |

Pick OCA's module if you only need the one-off override on a PO. Pick this
one if your billing policy actually depends on **which vendor** you're
purchasing from — which is the most common real-world case.

## Compatibility

* Odoo 17 Enterprise (tested) and Community (compatible — no EE-specific code).
* v18 / v19 also available in the respective branches of this repository.

## License

LGPL-3.

## Author

TaghrasThink — <https://github.com/taghrasthink>
