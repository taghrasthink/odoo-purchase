from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _tt_effective_purchase_method(self):
        """Return the effective purchase_method for this line.

        Priority order:
        1. Purchase order's tt_purchase_bill_policy when set to 'purchase' or 'receive'
        2. Product's own purchase_method (native fallback when PO policy is 'product')

        Returns falsy ('' / False) for display-type lines (sections, notes) with
        no product — caller code must tolerate this (the native compute does).
        """
        self.ensure_one()
        po_policy = self.order_id.tt_purchase_bill_policy
        if po_policy in ('purchase', 'receive'):
            return po_policy
        return self.product_id.purchase_method

    @api.depends('order_id.tt_purchase_bill_policy')
    def _compute_qty_invoiced(self):
        """Re-resolve qty_to_invoice based on the effective bill control policy.

        Strategy: delegate the full qty_invoiced + qty_to_invoice computation
        to super(), then re-adjust qty_to_invoice using the PO-level policy
        when applicable. This keeps us in sync with future native logic changes
        (e.g. handling of refunds, in_invoice / in_refund splits, currency
        conversions) — we only override the final policy decision.

        Native reference: odoo/addons/purchase/models/purchase_order_line.py
        _compute_qty_invoiced (Odoo 19 — lines 163-176).

        v19 change vs v18: the 'done' state was removed from purchase.order
        (replaced by the 'locked' boolean field). Native v19 only checks
        `state == 'purchase'` here, so our gate matches.
        """
        super()._compute_qty_invoiced()
        for line in self:
            if line.order_id.state != 'purchase':
                continue
            effective = line._tt_effective_purchase_method()
            if effective == 'purchase':
                line.qty_to_invoice = line.product_qty - line.qty_invoiced
            elif effective == 'receive':
                line.qty_to_invoice = line.qty_received - line.qty_invoiced
            # else: display-type / no product → leave whatever super() set
