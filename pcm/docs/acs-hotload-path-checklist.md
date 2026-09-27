# ACS / full-adopter path and filename checklist

For ACS and any full PCM+CGM hotload adopter, human-readable **titles alone are not enough**. Apply all three rows:

| Surface | Requirement | Owner / pointer |
| --- | --- | --- |
| Titles / issue / PR / commit / docs prose | Human-readable (existing CGM HSW / writing-direction) | CGM HSW |
| **Output / artifact filenames** | Pin and apply the CGM filename helper once it lands ([content-generation-modules#26](https://github.com/Pukujan/content-generation-modules/issues/26)); multi-dimension labels (pitch vs speed) must not collapse to one opaque token | CGM #26 |
| Continuity-managed **source paths** | Pronounceable new file/folder names per [`CONTINUITY_PATH_NAMING.md`](CONTINUITY_PATH_NAMING.md) | PCM (this stack) |

This checklist is binding for new work going forward. Do not rewrite published blob history unless an issue explicitly scopes a rename.

See also [`TARGET_ADOPTION.md`](TARGET_ADOPTION.md) (adoption checklist) and PCM [#213](https://github.com/Pukujan/project-continuity-modules/issues/213).
