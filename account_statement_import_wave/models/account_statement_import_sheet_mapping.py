# Copyright 2026 Koffi Modeste Junior
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountStatementImportSheetMapping(models.Model):
    _inherit = "account.statement.import.sheet.mapping"

    fee_column = fields.Char(
        help="Column holding the fees already deducted from the amount column. "
        "When set, each line with fees is imported as two lines: the gross "
        "amount (amount + fees) and a separate negative fee line, so fees can "
        "be reconciled with a dedicated expense account.",
    )
