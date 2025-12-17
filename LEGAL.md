# LEGAL / Licensing Guide (Commercial Forks & Redistribution)

This repository is **mixed-licensed**:

- **MIT**: applies to original DeSciOS-authored files (see individual file headers).
- **MPL 2.0**: applies to files derived from MPL 2.0 code (file-level copyleft; see individual file headers).

This document is a practical guide for commercial users and forkers. It is **not legal advice**.

## Mixed licensing (what it means)

Licensing is determined **per file** by the header at the top of that file.

- If a file header says **MIT**, that file is under the MIT License.
- If a file header says **MPL 2.0**, that file is under the Mozilla Public License 2.0.

Repository-level license texts:

- `LICENSE` (MIT) + mixed-license notice
- `LICENSE-MIT` (full MIT text)
- `LICENSE-MPL` (full MPL 2.0 text)

## Commercial / proprietary forks: allowed, with conditions

You **may** fork and ship commercial/proprietary products based on this repository, **as long as you comply with each file’s license**.

### Key rule (MPL 2.0 is file-level copyleft)

If you **distribute** a product that includes any **MPL 2.0–licensed file** from this repository:

- that file **must remain under MPL 2.0**, and
- if you **modify** it, you must make the **source code for that MPL-covered file (including your modifications)** available under MPL 2.0 to recipients.

This does **not** automatically require you to open-source unrelated files that are not MPL-covered.

## Which files are MPL vs MIT in this repository

### MPL 2.0 (Category A: MPL-derived)

These files are derived from the upstream noVNC project and are licensed under **MPL 2.0** (see file headers):

- `novnc-theme/ui.js`
- `novnc-theme/vnc.html`

### MIT (Category B: original DeSciOS-authored)

Unless a file header states otherwise, DeSciOS-authored files in this repository are intended to be under **MIT** (see file headers).

## Redistribution checklist (do this when you ship)

If you distribute binaries, containers, images, installers, or appliances that include this code:

- **Keep license headers intact** in all source files you ship.
- **Include license texts** in your distribution:
  - `LICENSE-MIT`
  - `LICENSE-MPL`
  - (and/or `LICENSE`, if you include it)
- **For MPL files you modified**:
  - provide the **exact source code** of those MPL files (including your modifications),
  - under **MPL 2.0**, and
  - in a way recipients can reasonably obtain (e.g., shipped source tarball, or a public repo/tag, or a written offer consistent with your distribution model).
- **Do not remove attribution** or existing copyright notices.

## “Can I make the whole fork proprietary?”

Not entirely.

- You can keep **your own original files** proprietary (or MIT/commercial), **but**
- you cannot relicense **MPL-covered files** as proprietary, and if you distribute them (especially modified), you must provide their source under MPL 2.0.

If you need a distribution that releases **no source code at all**, you must avoid distributing MPL-covered files (or replace them with code under terms compatible with your goals).

## Notes on “OS distributions” and open-source components

Many commercial systems ship a combination of proprietary code and open-source components. This repository supports a similar model: **MIT files are permissive**, while **MPL files require source availability for those files when distributed**.

## Contact

For licensing questions or commercial arrangements, contact the repository maintainer(s) listed in `LICENSE`.


