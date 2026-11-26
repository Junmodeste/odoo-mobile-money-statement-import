# Copyright 2026 Koffi Modeste Junior
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Wave Mobile Money Statement Import",
    "summary": "Ready-made CSV mapping to import Wave mobile money statements",
    "version": "18.0.1.1.0",
    "category": "Accounting",
    "website": "https://github.com/Junmodeste/odoo-mobile-money-statement-import",
    "author": "Koffi Modeste Junior",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["account_statement_import_sheet_file"],
    "data": [
        "data/account_statement_import_sheet_mapping.xml",
        "views/account_statement_import_sheet_mapping_views.xml",
    ],
}
