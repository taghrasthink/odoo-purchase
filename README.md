# Odoo Purchase Modules

Open-source Odoo modules developed by **[TaghrasThink](https://github.com/taghrasthink)**.

---

## Modules

### [`tt_purchase_vendor_bill_policy`](tt_purchase_vendor_bill_policy/) — Purchase Vendor Bill Policy

Define the purchase bill control policy at the **vendor level** with override on each purchase order.

- Adds a third configuration level: Vendor → Purchase Order → Product → Global setting
- Auto-fills the policy on each PO from the vendor profile
- Allows ad-hoc override on each PO (editable while draft, sent, or to approve)
- Multi-company aware (per-company policy on the same vendor)
- Manager-vs-user permission split on the vendor record
- 14 automated tests covering all decision rules and edge cases
- French & Arabic translations
- Compatible with Odoo 18 (CE & EE)

Compared to OCA's [`purchase_invoice_method`](https://github.com/OCA/purchase-workflow/tree/18.0/purchase_invoice_method) — which only adds a single override field on the PO — this module models the bill control policy as a **vendor relationship attribute** with auto-inheritance and full hierarchy. See the [module README](tt_purchase_vendor_bill_policy/#how-it-compares-to-ocas-purchase_invoice_method) for the side-by-side comparison.

→ [View on Odoo Apps](https://apps.odoo.com/apps/modules/18.0/tt_purchase_vendor_bill_policy) *(pending publication)*

---

## Compatibility

| Module | Odoo 18 |
|--------|:-------:|
| `tt_purchase_vendor_bill_policy` | ✅ |

Backports for Odoo 17 and 19 are maintained in their respective branches once released.

---

## Installation

Clone the branch matching your Odoo version:

```bash
git clone -b 18.0 https://github.com/taghrasthink/odoo-purchase.git
```

Then add the cloned folder to your `addons_path` in `odoo.conf` and install the module from the **Apps** menu.

---
