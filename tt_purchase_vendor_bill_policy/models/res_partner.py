from odoo import fields, models


BILL_POLICY_SELECTION = [
    ('product', 'Product Policy (default)'),
    ('purchase', 'On Ordered Quantities'),
    ('receive', 'On Received Quantities'),
]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # company_dependent=True: the policy can differ per company for the same
    # partner record (RG-V1 from audit — supports multi-company setups where
    # subsidiary A wants 'receive' but subsidiary B wants 'purchase' for the
    # same vendor).
    tt_purchase_bill_policy = fields.Selection(
        selection=BILL_POLICY_SELECTION,
        string='Bill Control Policy',
        default='product',
        company_dependent=True,
        # group_purchase_user is the lower threshold (manager implies user).
        # Read access for all purchase users; write access is enforced at the
        # view level via two conditional field declarations (editable for
        # managers, readonly for users-only). See views/res_partner_views.xml.
        groups='purchase.group_purchase_user',
        help="Default bill control policy applied to purchase orders for this vendor.\n"
             "* Product Policy: each PO line uses the policy defined on its own product.\n"
             "* On Ordered Quantities: bills can be generated as soon as the PO is confirmed.\n"
             "* On Received Quantities: bills can only be generated after goods are received.\n"
             "This is the default — it can be overridden manually on each draft purchase order.\n"
             "Value is per-company: each company can set its own policy for the same vendor.",
    )
