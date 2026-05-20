import logging

from lxml import etree

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class DmsFile(models.Model):
    _inherit = "dms.file"

    description = fields.Text(
        string="Description",
        help="Notes about the file, source, purpose, revision status, or review context.",
        tracking=True,
    )
    description_short = fields.Char(
        string="Short Description",
        compute="_compute_description_short",
        help="Short version of the description used on DMS kanban cards.",
    )

    def _compute_description_short(self):
        limit = 35
        for record in self:
            text = (record.description or "").strip().replace("\r", " ").replace("\n", " ")
            text = " ".join(text.split())
            if len(text) > limit:
                record.description_short = text[:limit].rstrip() + "..."
            else:
                record.description_short = text

    @classmethod
    def _has_description_field(cls, arch):
        return bool(arch.xpath(".//field[@name='description']"))

    @classmethod
    def _has_description_short_field(cls, arch):
        return bool(arch.xpath(".//field[@name='description_short']"))

    @classmethod
    def _insert_after_first_field(cls, arch, target_names, node):
        """Insert node after the first matching field, returning True if inserted."""
        for name in target_names:
            targets = arch.xpath(".//field[@name=%r]" % name)
            if targets:
                targets[0].addnext(node)
                return True
        return False

    @classmethod
    def _add_description_to_form(cls, arch):
        if cls._has_description_field(arch):
            return

        node = etree.Element(
            "field",
            name="description",
            placeholder="Describe the file, source, purpose, revision notes, review status, etc.",
        )

        # Prefer to place it near normal metadata. Fall back safely if the DMS form changes.
        if cls._insert_after_first_field(arch, ["name", "tag_ids", "category_id"], node):
            return

        groups = arch.xpath(".//group")
        if groups:
            groups[0].append(node)
            return

        sheets = arch.xpath(".//sheet")
        if sheets:
            sheets[0].append(node)
            return

        arch.append(node)

    @classmethod
    def _add_description_to_list(cls, arch):
        if cls._has_description_field(arch):
            return

        node = etree.Element("field", name="description", optional="show")

        if cls._insert_after_first_field(arch, ["name", "tag_ids", "category_id"], node):
            return

        # list/tree root supports field children directly.
        arch.insert(0, node)

    @classmethod
    def _add_description_to_search(cls, arch):
        if not cls._has_description_field(arch):
            field_node = etree.Element("field", name="description", string="Description")
            if not cls._insert_after_first_field(arch, ["name", "tag_ids", "category_id"], field_node):
                arch.insert(0, field_node)

        if arch.xpath(".//filter[@name='has_description']"):
            return

        separator = etree.Element("separator")
        has_filter = etree.Element(
            "filter",
            name="has_description",
            string="Has Description",
            domain="[('description', '!=', False)]",
        )
        missing_filter = etree.Element(
            "filter",
            name="missing_description",
            string="Missing Description",
            domain="[('description', '=', False)]",
        )

        arch.append(separator)
        arch.append(has_filter)
        arch.append(missing_filter)

    @classmethod
    def _ensure_kanban_field(cls, arch, name):
        if arch.xpath("./field[@name=%r]" % name):
            return
        field_node = etree.Element("field", name=name)
        templates = arch.xpath("./templates")
        if templates:
            arch.insert(arch.index(templates[0]), field_node)
        else:
            arch.insert(0, field_node)

    @classmethod
    def _description_kanban_node(cls):
        """Return a small QWeb block that shows a trimmed description on kanban cards."""
        # XML parser needs escaped JS operators.
        return etree.fromstring(
            b"""
            <div t-if="record.description_short.raw_value"
                 class="o_dms_file_description_kanban text-muted mt-1 small"
                 t-att-title="record.description.raw_value">
                <i class="fa fa-align-left me-1" role="img" title="Description"/>
                <span t-esc="record.description_short.raw_value"/>
            </div>
            """
        )

    @classmethod
    def _add_description_to_kanban(cls, arch):
        # The visual template can only use fields loaded by the kanban root.
        cls._ensure_kanban_field(arch, "description")
        cls._ensure_kanban_field(arch, "description_short")

        if arch.xpath(".//*[contains(concat(' ', normalize-space(@class), ' '), ' o_dms_file_description_kanban ')]"):
            return

        node = cls._description_kanban_node()

        # Best case: insert after the visible name field inside the card template.
        name_fields = arch.xpath(".//templates//field[@name='name']")
        if name_fields:
            name_fields[0].addnext(node)
            return

        # Odoo 18 commonly uses <t t-name="card">; older kanban often uses kanban-box.
        card_templates = arch.xpath(
            ".//templates//t[@t-name='card' or @t-name='kanban-box' or contains(@t-name, 'kanban')]"
        )
        if card_templates:
            card_templates[0].append(node)
            return

        templates = arch.xpath(".//templates")
        if templates:
            templates[0].append(node)

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id=view_id, view_type=view_type, **options)

        try:
            if view_type == "form":
                self._add_description_to_form(arch)
            elif view_type in ("list", "tree"):
                self._add_description_to_list(arch)
            elif view_type == "search":
                self._add_description_to_search(arch)
            elif view_type == "kanban":
                self._add_description_to_kanban(arch)
        except Exception:
            # Do not break the whole DMS UI if a future upstream view structure changes.
            _logger.exception("Unable to inject DMS file description into %s view", view_type)

        return arch, view
