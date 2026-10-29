# Safety, authorization, and privacy

Reverse engineering is a method of learning and interoperability, not a blanket authorization to inspect or alter another party's assets.

## Permission

- Identify who owns/controls the target and whether the user may test it.
- Default to passive analysis of user-provided artifacts when ownership is uncertain.
- Request explicit authorization before state-changing experiments, executable runs, traffic interception, new network requests, production load, hardware probing, or disassembly.
- Respect legal and contractual limits; refer to qualified legal or technical advice for unclear circumstances.

## Cybersecurity-sensitive boundaries

Do not assist with credential theft, unauthorized exploitation, malware development, defeating security mechanisms or license/DRM controls, evasion, or exfiltration. If a user wants to understand a potentially dangerous system, focus on defensive architecture, public design principles, safe lab simulations, and remediation.

## Physical safety

Do not walk users through hazardous repair/disassembly/modification of mains/high-voltage equipment, lithium packs, pressurized apparatus, combustible gas systems, critical automotive parts, medical devices, or industrial controls. Stop and route to safe public documentation or a qualified technician.

## Privacy and integrity

Never expose secrets, protected personal data, or private records while inventorying files or logs. The bundled scripts omit common secret-like filenames and do not upload data. They are not a substitute for human review. Do not publish data or results without permission. Preserve originals and use a separate workspace for simulations.
