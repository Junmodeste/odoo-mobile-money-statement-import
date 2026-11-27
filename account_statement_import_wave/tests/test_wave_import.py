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

    def _import(self, filename, mapping=None, **context):
        data = (Path(__file__).parent / "fixtures" / filename).read_bytes()
        mapping = mapping or self.mapping
        wizard = (
            self.env["account.statement.import"]
            .with_context(
                journal_id=self.journal.id,
                account_statement_import_sheet_file_test=True,
                **context,
            )
            .create(
                {
                    "statement_filename": filename,
                    "statement_file": b64encode(data),
                    "sheet_mapping_id": mapping.id,
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

    def test_import_separate_fees(self):
        mapping = self.env.ref(
            "account_statement_import_wave.mapping_wave_csv_separate_fees"
        )
        statement = self._import("wave_sample.csv", mapping)
        lines = statement.line_ids
        # Two lines with fees -> gross + fee line each; no fee line when fees = 0.
        self.assertEqual(len(lines), 5)
        self.assertEqual(
            sorted(lines.mapped("amount")), [-20000, -500, -120, 12000, 50000]
        )
        # Same total as the net import: the wallet balance still matches.
        self.assertEqual(sum(lines.mapped("amount")), 41380)
        fee = lines.filtered(lambda line: line.amount == -500)
        self.assertIn("Paiement reçu", fee.payment_ref)
        self.assertFalse(fee.partner_name)
        self.assertTrue(fee.unique_import_id.endswith("-fee"))
        self.assertIn("T_DEMO_0001", fee.unique_import_id)

    def test_reimport_separate_fees_no_duplicate(self):
        mapping = self.env.ref(
            "account_statement_import_wave.mapping_wave_csv_separate_fees"
        )
        self._import("wave_sample.csv", mapping)
        with suppress(UserError):
            self._import("wave_sample.csv", mapping)
        statements = self.env["account.bank.statement"].search(
            [("journal_id", "=", self.journal.id)]
        )
        self.assertEqual(len(statements.line_ids), 5)

    def _load_french(self):
        self.env["res.lang"]._activate_lang("fr_FR")
        self.env["ir.module.module"]._load_module_terms(
            ["account_statement_import_wave"], ["fr_FR"]
        )

    def test_french_field_labels(self):
        # Every field added by the module must have its label in i18n/fr.po.
        self._load_french()
        self.env.cr.execute(
            """
            SELECT f.model || '.' || f.name
              FROM ir_model_fields f
              JOIN ir_model_data d ON d.model = 'ir.model.fields' AND d.res_id = f.id
             WHERE d.module = 'account_statement_import_wave'
               AND f.field_description->>'fr_FR' IS NULL
            """
        )
        self.assertEqual([row[0] for row in self.env.cr.fetchall()], [])

    def test_french_fee_line_label(self):
        # The fee line label comes from the code (self.env._): it follows the
        # language of the user who imports the file.
        self._load_french()
        mapping = self.env.ref(
            "account_statement_import_wave.mapping_wave_csv_separate_fees"
        )
        statement = self._import("wave_sample.csv", mapping, lang="fr_FR")
        fee = statement.line_ids.filtered(lambda line: line.amount == -500)
        self.assertTrue(fee.payment_ref.startswith("Frais : "), fee.payment_ref)
