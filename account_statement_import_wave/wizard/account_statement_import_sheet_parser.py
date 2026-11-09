# Copyright 2026 Koffi Modeste Junior
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class AccountStatementImportSheetParser(models.TransientModel):
    _inherit = "account.statement.import.sheet.parser"

    def _get_column_names(self):
        return super()._get_column_names() + ["fee_column"]

    def _parse_one_line(self, mapping, currency_code, values, columns):
        line = super()._parse_one_line(mapping, currency_code, values, columns)
        raw_fee = self._get_values_from_column(values, columns, "fee_column")
        if line and raw_fee:
            # Fees are always a cost, whatever sign the export uses.
            line["fee"] = abs(self._parse_decimal(raw_fee, mapping))
        return line

    @api.model
    def _convert_line_to_transactions(self, line):
        transactions = super()._convert_line_to_transactions(line)
        fee = line.get("fee")
        if not fee:
            return transactions
        main = transactions[0]
        # The amount column is net of fees: book the gross amount and the fees
        # on two lines so the statement total (and balance) stays the same.
        main["amount"] = str(line["amount"] + fee)
        fee_transaction = {
            "date": main["date"],
            "amount": str(-fee),
            "payment_ref": self.env._("Fees: %s", main["payment_ref"]),
        }
        for key in ("currency_id", "ref"):
            if key in main:
                fee_transaction[key] = main[key]
        if "unique_import_id" in main:
            fee_transaction["unique_import_id"] = f"{main['unique_import_id']}-fee"
        transactions.append(fee_transaction)
        return transactions
