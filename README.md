# Odoo Mobile Money Statement Import (Wave)

[![Odoo 18](https://img.shields.io/badge/Odoo-18.0-714B67)](https://www.odoo.com)
[![tests](https://github.com/Junmodeste/odoo-mobile-money-statement-import/actions/workflows/tests.yml/badge.svg)](https://github.com/Junmodeste/odoo-mobile-money-statement-import/actions/workflows/tests.yml)
[![License: AGPL-3](https://img.shields.io/badge/License-AGPL--3-blue.svg)](LICENSE)

🇫🇷 [Français](#français) · 🇬🇧 [English](#english)

## Français

Le module `account_statement_import_wave` fournit un modèle d'import prêt à l'emploi pour charger un export CSV de compte Wave (mobile money) comme relevé bancaire dans Odoo.
Il s'appuie sur le module OCA `account_statement_import_sheet_file` : les lignes importées se rapprochent ensuite comme n'importe quel relevé bancaire.

### Fonctionnement

- Un modèle d'import **Wave (CSV)** est créé dans *Comptabilité > Configuration > Statement Sheet Mappings* (libellé du module OCA, selon votre traduction).
- Le montant importé est le **montant net** (après frais Wave) : c'est ce qui bouge réellement sur le compte, donc le solde du relevé correspond au solde Wave.
- Les frais sont repris dans les notes de la ligne. L'identifiant de transaction Wave rend chaque ligne unique : réimporter le même fichier ne crée pas de doublon.
- Variante **Wave (CSV, separate fees)** : chaque ligne avec frais devient deux lignes, le **montant brut** (net + frais) et une ligne **« Frais : … »** négative, à rapprocher avec un compte de charges (frais bancaires). Le total et le solde du relevé restent identiques. Pour un autre modèle d'import, renseignez le champ **Colonne des frais** (en 18.0, le modèle doit aussi avoir une colonne d'identifiant de transaction).

### Colonnes attendues (à vérifier)

Wave ne publie pas de format officiel d'export. Les noms de colonnes ci-dessous sont une hypothèse, à comparer avec un export réel :

| Colonne | Exemple | Usage |
|---|---|---|
| `Date` | `2026-11-02 09:15:00` | date de la ligne (format `%Y-%m-%d %H:%M:%S`) |
| `Identifiant` | `T_DEMO_0001` | identifiant unique de transaction |
| `Description` | `Paiement reçu` | libellé |
| `Contrepartie` | `Client Fictif A` | nom du partenaire |
| `Frais` | `500` | repris dans les notes |
| `Montant net` | `49500` | montant de la ligne (négatif pour une sortie) |

Si votre export diffère, modifiez le modèle **Wave (CSV)** dans Odoo : vos changements sont conservés lors des mises à jour du module. Un fichier d'exemple fictif se trouve dans [`tests/fixtures/wave_sample.csv`](account_statement_import_wave/tests/fixtures/wave_sample.csv).

### Prérequis

- Odoo 18 (Community ou Enterprise), module `account`
- Modules OCA [`account_statement_import_sheet_file`](https://github.com/OCA/bank-statement-import/tree/18.0) (dépôt `OCA/bank-statement-import`) et `account_statement_base` (dépôt [`OCA/account-reconcile`](https://github.com/OCA/account-reconcile/tree/18.0)), branche `18.0`

### Installation

1. Ajoutez à votre chemin d'addons les dépôts OCA ci-dessus et le dossier `account_statement_import_wave`.
2. Redémarrez Odoo et mettez à jour la liste des applications.
3. Installez **Wave Mobile Money Statement Import**, puis importez votre CSV depuis le journal Wave (type banque, devise XOF) en choisissant le modèle **Wave (CSV)**.

### Version supportée

Odoo 18, branche [`18.0`](https://github.com/Junmodeste/odoo-mobile-money-statement-import/tree/18.0). Tests automatisés (GitHub Actions) sur Odoo 18 Community (image `odoo:18`) + PostgreSQL 16, avec les dépendances OCA, à chaque push. Autre branche : [`19.0`](https://github.com/Junmodeste/odoo-mobile-money-statement-import/tree/19.0) (Odoo 19).

### Licence

[AGPL-3](LICENSE), comme le module OCA dont il dépend.

### Auteur

Koffi Modeste Junior — [@Junmodeste](https://github.com/Junmodeste)

## English

The `account_statement_import_wave` module provides a ready-made import mapping to load a CSV export of a Wave (mobile money) account as a bank statement in Odoo.
It builds on the OCA module `account_statement_import_sheet_file`: imported lines are then reconciled like any bank statement.

### Behavior

- A **Wave (CSV)** import mapping is created in *Accounting > Configuration > Statement Sheet Mappings*.
- The imported amount is the **net amount** (after Wave fees): it is what actually moves on the wallet, so the statement balance matches the Wave balance.
- Fees are kept in the line notes. The Wave transaction id makes each line unique: importing the same file again creates no duplicate.
- **Wave (CSV, separate fees)** variant: each line with fees becomes two lines, the **gross amount** (net + fees) and a negative **"Fees: …"** line, to reconcile with an expense account (bank charges). The statement total and balance stay the same. For another import mapping, fill in the **Fee Column** field (in 18.0, the mapping also needs a transaction ID column).

### Expected columns (to be checked)

Wave does not publish an official export format. The column names are an assumption, to compare with a real export: `Date` (`%Y-%m-%d %H:%M:%S`), `Identifiant` (transaction id), `Description`, `Contrepartie` (partner name), `Frais` (fees, kept in notes), `Montant net` (line amount, negative for outgoing money).

If your export differs, edit the **Wave (CSV)** mapping in Odoo: your changes are kept when the module is updated. A fictitious sample file is in [`tests/fixtures/wave_sample.csv`](account_statement_import_wave/tests/fixtures/wave_sample.csv).

### Requirements

- Odoo 18 (Community or Enterprise), `account` module
- OCA modules `account_statement_import_sheet_file` (`OCA/bank-statement-import`) and `account_statement_base` (`OCA/account-reconcile`), branch `18.0`

### Installation

1. Add the OCA repositories above and the `account_statement_import_wave` folder to your addons path.
2. Restart Odoo and update the apps list.
3. Install **Wave Mobile Money Statement Import**, then import your CSV from the Wave journal (bank type, XOF currency) with the **Wave (CSV)** mapping.

### Supported version

Odoo 18, branch [`18.0`](https://github.com/Junmodeste/odoo-mobile-money-statement-import/tree/18.0). Automated tests (GitHub Actions) on Odoo 18 Community (`odoo:18` image) + PostgreSQL 16, with the OCA dependencies, on every push. Other branch: [`19.0`](https://github.com/Junmodeste/odoo-mobile-money-statement-import/tree/19.0) (Odoo 19).

### License

[AGPL-3](LICENSE), like the OCA module it depends on.

### Author

Koffi Modeste Junior — [@Junmodeste](https://github.com/Junmodeste)
