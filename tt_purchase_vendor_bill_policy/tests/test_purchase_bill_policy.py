from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestPurchaseVendorBillPolicy(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Partner = cls.env['res.partner']
        Product = cls.env['product.product']

        cls.vendor_default = Partner.create({
            'name': 'Vendor Default',
            'supplier_rank': 1,
        })
        cls.vendor_receive = Partner.create({
            'name': 'Vendor Receive',
            'supplier_rank': 1,
            'tt_purchase_bill_policy': 'receive',
        })
        cls.vendor_purchase = Partner.create({
            'name': 'Vendor Purchase',
            'supplier_rank': 1,
            'tt_purchase_bill_policy': 'purchase',
        })

        cls.product_purchase = Product.create({
            'name': 'Product with ordered policy',
            'purchase_method': 'purchase',
            'type': 'consu',
        })
        cls.product_receive = Product.create({
            'name': 'Product with received policy',
            'purchase_method': 'receive',
            'type': 'consu',
        })

    # -------- Partner field --------

    def test_partner_default_is_product(self):
        """RG-01: default policy on a new vendor is 'product'."""
        self.assertEqual(self.vendor_default.tt_purchase_bill_policy, 'product')

    def test_partner_explicit_value(self):
        """Vendor configured with a specific policy keeps it."""
        self.assertEqual(self.vendor_receive.tt_purchase_bill_policy, 'receive')
        self.assertEqual(self.vendor_purchase.tt_purchase_bill_policy, 'purchase')

    # -------- PO inheritance from partner (B2 / RG-05) --------

    def test_po_inherits_policy_from_partner(self):
        """B2: PO created for a vendor inherits the vendor's policy."""
        po = self.env['purchase.order'].create({'partner_id': self.vendor_receive.id})
        self.assertEqual(po.tt_purchase_bill_policy, 'receive')

    def test_po_default_partner_policy_resolves_to_product(self):
        """A vendor with no specific policy gives a PO with 'product'."""
        po = self.env['purchase.order'].create({'partner_id': self.vendor_default.id})
        self.assertEqual(po.tt_purchase_bill_policy, 'product')

    # -------- Manual override on PO (B3 / RG-06) --------

    def test_po_manual_override_persists(self):
        """B3: manual edit on PO is preserved (no auto-recompute)."""
        po = self.env['purchase.order'].create({'partner_id': self.vendor_default.id})
        po.tt_purchase_bill_policy = 'receive'
        self.assertEqual(po.tt_purchase_bill_policy, 'receive')

    def test_partner_change_overrides_manual_edit(self):
        """RG-06: changing the vendor overrides any manual edit on the PO."""
        po = self.env['purchase.order'].create({'partner_id': self.vendor_default.id})
        po.tt_purchase_bill_policy = 'purchase'  # manual edit
        po.partner_id = self.vendor_receive.id  # vendor change
        self.assertEqual(
            po.tt_purchase_bill_policy, 'receive',
            "Vendor change must override the manual edit on the PO field",
        )

    def test_partner_policy_change_does_not_propagate_to_existing_po(self):
        """RG-02: changing vendor policy does not retroactively touch existing POs."""
        po = self.env['purchase.order'].create({'partner_id': self.vendor_default.id})
        self.assertEqual(po.tt_purchase_bill_policy, 'product')
        self.vendor_default.tt_purchase_bill_policy = 'receive'
        # The existing PO is untouched
        self.assertEqual(po.tt_purchase_bill_policy, 'product')

    # -------- _tt_effective_purchase_method helper (B5) --------

    def _make_line(self, po, product, qty=10):
        return self.env['purchase.order.line'].create({
            'order_id': po.id,
            'product_id': product.id,
            'product_qty': qty,
            'price_unit': 100.0,
            'name': product.name,
        })

    def test_helper_po_override_wins(self):
        """B5: when PO policy is set, it overrides the product."""
        po = self.env['purchase.order'].create({
            'partner_id': self.vendor_default.id,
            'tt_purchase_bill_policy': 'receive',
        })
        line = self._make_line(po, self.product_purchase)
        self.assertEqual(line._tt_effective_purchase_method(), 'receive')

    def test_helper_product_fallback(self):
        """B5: when PO policy is 'product', the product's purchase_method applies."""
        po = self.env['purchase.order'].create({'partner_id': self.vendor_default.id})
        self.assertEqual(po.tt_purchase_bill_policy, 'product')
        line_p = self._make_line(po, self.product_purchase)
        line_r = self._make_line(po, self.product_receive)
        self.assertEqual(line_p._tt_effective_purchase_method(), 'purchase')
        self.assertEqual(line_r._tt_effective_purchase_method(), 'receive')

    # -------- qty_to_invoice computation (B4) --------

    def test_qty_to_invoice_with_receive_policy_unreceived(self):
        """B4: 'receive' policy + no reception → qty_to_invoice = 0."""
        po = self.env['purchase.order'].create({
            'partner_id': self.vendor_receive.id,
            'order_line': [(0, 0, {
                'product_id': self.product_purchase.id,
                'product_qty': 10,
                'price_unit': 100.0,
                'name': self.product_purchase.name,
            })],
        })
        po.button_confirm()
        line = po.order_line
        self.assertEqual(line._tt_effective_purchase_method(), 'receive')
        self.assertEqual(
            line.qty_to_invoice, 0,
            "With 'receive' policy and no reception, qty_to_invoice must be 0",
        )

    def test_qty_to_invoice_with_ordered_policy(self):
        """B4: 'purchase' policy → qty_to_invoice = product_qty even without reception."""
        po = self.env['purchase.order'].create({
            'partner_id': self.vendor_purchase.id,
            'order_line': [(0, 0, {
                'product_id': self.product_receive.id,  # product says receive
                'product_qty': 10,
                'price_unit': 100.0,
                'name': self.product_receive.name,
            })],
        })
        po.button_confirm()
        line = po.order_line
        self.assertEqual(line._tt_effective_purchase_method(), 'purchase',
                         "PO policy 'purchase' wins over product policy 'receive'")
        self.assertEqual(
            line.qty_to_invoice, 10,
            "With 'purchase' policy, qty_to_invoice = product_qty regardless of reception",
        )

    def test_qty_to_invoice_with_product_fallback(self):
        """B4: 'product' policy → uses each product's own purchase_method."""
        po = self.env['purchase.order'].create({
            'partner_id': self.vendor_default.id,  # policy = product
            'order_line': [
                (0, 0, {
                    'product_id': self.product_purchase.id,
                    'product_qty': 5,
                    'price_unit': 100.0,
                    'name': self.product_purchase.name,
                }),
                (0, 0, {
                    'product_id': self.product_receive.id,
                    'product_qty': 7,
                    'price_unit': 100.0,
                    'name': self.product_receive.name,
                }),
            ],
        })
        po.button_confirm()
        line_purchase = po.order_line.filtered(lambda l: l.product_id == self.product_purchase)
        line_receive = po.order_line.filtered(lambda l: l.product_id == self.product_receive)
        self.assertEqual(line_purchase.qty_to_invoice, 5,
                         "'purchase' product → bill ordered qty")
        self.assertEqual(line_receive.qty_to_invoice, 0,
                         "'receive' product without reception → 0 to invoice")

    # -------- Copy semantics (V2) --------

    def test_po_copy_preserves_policy_when_same_vendor(self):
        """Duplicating a PO with the same vendor preserves the policy."""
        po = self.env['purchase.order'].create({
            'partner_id': self.vendor_default.id,
            'tt_purchase_bill_policy': 'purchase',
        })
        po_copy = po.copy()
        self.assertEqual(po_copy.tt_purchase_bill_policy, 'purchase')

    # -------- Multi-company (V1) --------

    def test_partner_policy_is_company_dependent(self):
        """V1: same vendor can have different policies per company."""
        # Create a second company for the test
        company_a = self.env.company
        company_b = self.env['res.company'].create({'name': 'Company B'})

        # Make admin user member of company_b too
        self.env.user.company_ids = [(4, company_b.id)]

        partner = self.env['res.partner'].create({
            'name': 'Multi-company Vendor',
            'supplier_rank': 1,
        })

        # Set 'receive' in company A
        partner.with_company(company_a).tt_purchase_bill_policy = 'receive'
        # Set 'purchase' in company B
        partner.with_company(company_b).tt_purchase_bill_policy = 'purchase'

        self.assertEqual(
            partner.with_company(company_a).tt_purchase_bill_policy, 'receive',
            "Company A keeps its own policy",
        )
        self.assertEqual(
            partner.with_company(company_b).tt_purchase_bill_policy, 'purchase',
            "Company B has an independent policy",
        )
