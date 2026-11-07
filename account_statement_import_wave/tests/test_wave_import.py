# Copyright 2026 Koffi Modeste Junior
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from base64 import b64encode
from contextlib import suppress
from pathlib import Path

from odoo.exceptions import UserError
from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestWaveImport(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.xof = cls.env.ref("base.XOF")
        cls.xof.active = True
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Wave",
                "type": "bank",
                "code": "WAVE",
                "currency_id": cls.xof.id,
            }
        )
        cls.mapping = cls.env.ref("account_statement_import_wave.mapping_wave_csv")

    def _import(self, filename):
        data = (Path(__file__).parent / "fixtures" / filename).read_bytes()
        wizard = (
            self.env["account.statement.import"]
            .with_context(
                journal_id=self.journal.id,
                account_statement_import_sheet_file_test=True,
            )
            .create(
                {
                    "statement_filename": filename,
                    "statement_file": b64encode(data),
                    "sheet_mapping_id": self.mapping.id,
                }
            )
        )
        wizard.import_file_button()
        return self.env["account.bank.statement"].search(
            [("journal_id", "=", self.journal.id)]
        )

    def test_import_sample(self):
        statement = self._import("wave_sample.csv")
        self.assertEqual(len(statement), 1)
        lines = statement.line_ids.sorted("date")
        self.assertEqual(len(lines), 3)
        # Net amounts: fees are already deducted by Wave.
        self.assertEqual(sorted(lines.mapped("amount")), [-20000, 11880, 49500])
        self.assertEqual(sum(lines.mapped("amount")), 41380)
        first = lines.filtered(lambda line: line.amount == 49500)
        self.assertEqual(first.partner_name, "Client Fictif A")
        self.assertIn("Paiement reçu", first.payment_ref)
        self.assertEqual(str(first.date), "2026-11-02")
        self.assertIn("T_DEMO_0001", first.unique_import_id)
        # Wave fees are kept in the line notes.
        self.assertIn("500", str(first.narration))

    def test_reimport_no_duplicate(self):
        self._import("wave_sample.csv")
        # The Wave transaction id makes each line unique: a second import of
        # the same file must not create new lines (OCA may raise a UserError).
        with suppress(UserError):
            self._import("wave_sample.csv")
        statements = self.env["account.bank.statement"].search(
            [("journal_id", "=", self.journal.id)]
        )
        self.assertEqual(len(statements.line_ids), 3)
