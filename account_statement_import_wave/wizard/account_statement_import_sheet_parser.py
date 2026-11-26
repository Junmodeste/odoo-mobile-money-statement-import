# Copyright 2026 Koffi Modeste Junior
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.exceptions import UserError


class AccountStatementImportSheetParser(models.TransientModel):
    _inherit = "account.statement.import.sheet.parser"

    def _get_column_names(self):
        return super()._get_column_names() + ["fee_column"]

    def _parse_rows(self, mapping, currency_code, data, columns):
        if not columns.get("fee_column"):
            return super()._parse_rows(mapping, currency_code, data, columns)
        if not columns.get("transaction_id_column"):
            raise UserError(
                self.env._("A fee column needs a transaction ID column in the mapping.")
            )
        # OCA 18.0 has no per-line hook: collect each row's raw fee by
        # transaction ID while the rows are read, then attach it to the lines.
        raw_fees = {}
        parser = self.with_context(wave_raw_fees=raw_fees)
        lines = super(AccountStatementImportSheetParser, parser)._parse_rows(
            mapping, currency_code, data, columns
        )
        for line in lines:
            raw_fee = raw_fees.get(line.get("transaction_id"))
            if raw_fee:
                # Fees are always a cost, whatever sign the export uses.
                line["fee"] = abs(self._parse_decimal(raw_fee, mapping))
        return lines

    def _get_values_from_column(self, values, columns, column_name):
        value = super()._get_values_from_column(values, columns, column_name)
        raw_fees = self.env.context.get("wave_raw_fees")
        if raw_fees is not None and column_name == "transaction_id_column":
            raw_fees[value] = super()._get_values_from_column(
                values, columns, "fee_column"
            )
        return value

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
