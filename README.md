# additional_contacts_v1_001

This zip contains a first-pass Odoo 18 Community addon bundle for shared **Additional Contacts** lists.

## Included addons

- `additional_contacts` — base models, roles, shared lists, generic links, settings.
- `additional_contacts_crm` — adds an Additional Contacts tab to CRM leads/opportunities.
- `additional_contacts_sale` — adds an Additional Contacts tab to Sales Orders.
- `additional_contacts_project` — adds an Additional Contacts tab to Projects and task-selected contacts.
- `additional_contacts_crm_sale` — bridge: propagates CRM/opportunity contact list to quotations/sales orders.
- `additional_contacts_sale_project` — bridge: propagates sales order contact list to generated projects.
- `additional_contacts_partner` — adds a read-only **Involved In** tab to Contacts.
- `additional_contacts_hr` — adds a read-only **Involved In** tab to Employees using the linked contact.
- `additional_contacts_full` — convenience/meta addon depending on the full bundle.

## First test recommendation

1. Copy all directories into an Odoo 18 `addons_path` directory.
2. Restart Odoo.
3. Update Apps List.
4. Install `additional_contacts_full` on the demo database.
5. Test in this order:
   - Contact roles under **Contacts → Configuration → Additional Contacts → Roles**.
   - Create/open an opportunity with a customer; check **Additional Contacts** tab.
   - Add an adjuster/subcontractor line.
   - Create a quotation from the opportunity; verify the Sales Order shares the same list.
   - Confirm the order with a service product that creates a project; verify the Project shares the same list.
   - Open a Contact from the list; check **Involved In**.
   - On a Task, add selected Additional Contacts from the project list.

## Intentional v1 omissions

- No follower checkbox.
- No split/diverge list button.
- No inline editing of core contact phone/email/name.
- No replacement of Odoo's built-in Contacts & Addresses.
- No complex record-rule enforcement beyond normal parent record UI and existing contact permissions.

## Notes

The bridge modules are intentionally separate so CRM, Sales, Project, and Sale Project are not hard-coupled in the base addon.

`additional_contacts_crm` depends only on `crm`. The CRM → Sales bridge uses Odoo's `sale_crm` module because that is where the standard opportunity/quotation link normally lives.
