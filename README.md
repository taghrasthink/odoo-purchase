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
- 14 automated tests covering all decision rules and edge cases
- Compatible with Odoo 18 (CE & EE)

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
