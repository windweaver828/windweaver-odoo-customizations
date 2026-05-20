# DMS File Description

Adds an editable `description` field to OCA DMS files (`dms.file`) and exposes it in common DMS UI surfaces:

- DMS file form metadata
- DMS file list view as an optional column
- DMS file search view and filters
- DMS file kanban cards with a short preview
- Odoo file viewer overlay when opening a DMS file from the DMS kanban preview

The module avoids hard-coding DMS view XML IDs by injecting into generated views from `dms.file._get_view()`.


## 18.0.1.0.5

- Avoid SCSS `min()` with `calc()` so Odoo/dark-mode Sass compilation works.


## 18.0.1.0.6

- Carry the DMS file description into Odoo's file viewer state instead of relying on arbitrary mail Attachment fields being preserved.
- Also patch the DMS preview_binary field used on full file forms.


## 18.0.1.0.7

- Remove the experimental fullscreen FileViewer patch.
- Add the full description directly to DMS's `preview_binary` field widget (`dms.FilePreviewField`), underneath the inline open/download/preview controls.


## 18.0.1.0.9

- Refreshes the DMS preview-panel description after likely file-detail saves/dialog confirmations instead of using stale cached descriptions.
