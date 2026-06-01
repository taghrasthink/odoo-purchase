from odoo import api, fields, models

from .res_partner import BILL_POLICY_SELECTION


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    tt_purchase_bill_policy = fields.Selection(
        selection=BILL_POLICY_SELECTION,
        string='Bill Control Policy',
        compute='_compute_tt_purchase_bill_policy',
        store=True,
        readonly=False,
        precompute=True,
        copy=True,
        help="Bill control policy applied to all lines of this purchase order.\n"
             "Inherited from the vendor's policy. Can be overridden manually while the "
             "order is in Draft, Sent or To Approve state. Becomes read-only once the "
             "order is confirmed (Purchase Order or Cancelled).\n"
             "Changing the vendor overrides any manual edit with the new vendor's policy.",
    )

    @api.depends('partner_id', 'company_id')
    def _compute_tt_purchase_bill_policy(self):
        """Pull the policy from the selected vendor, in the PO's company context.

        Stored compute with readonly=False allows manual override while still
        being recomputed whenever partner_id or company_id changes (satisfies
        RG-05 and RG-06: a vendor change always wins over a manual edit).

        Security note: the partner field is gated by purchase.group_purchase_user
        at the model level (read access for any purchase user). The .sudo() here
        is a defensive measure for edge cases — automated actions, scheduled
        jobs or system users that may not be in the purchase group when triggering
        a recompute. It does not weaken the user-facing access control.

        with_company() ensures the company-dependent partner field is read in
        the PO's company context, not the env user's current company.
        """
        for order in self:
            if order.partner_id:
                company = order.company_id or self.env.company
                partner_in_company = order.partner_id.with_company(company).sudo()
                order.tt_purchase_bill_policy = partner_in_company.tt_purchase_bill_policy or 'product'
            else:
                order.tt_purchase_bill_policy = 'product'
