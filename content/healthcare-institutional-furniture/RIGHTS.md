# RIGHTS — Healthcare institutional furniture pack

Lead `<figure class="hif-figure">` blocks combine **original CC0 schematics** (`assets/diagrams/*.svg`) and **rights-cleared documentary plates** (mostly Wikimedia Commons and U.S. government scans). **No AI-generated images. No synthetic or stock “resident” faces.** Re-check Commons license tags before WordPress publish.

Canonical rows: `assets/figures/REGISTRY.toml`. Slug map: `_editorial/figure_assignments.toml`.

Regenerate diagrams: `python3 scripts/generate_svgs.py`  
Embed / refresh drafts: `python3 _editorial/embed_figures.py`  
Verify: `python3 _editorial/check_figures.py`

## Original diagrams (CC0 1.0)

All files under `assets/diagrams/` are original line art for this pack, dedicated to the public domain under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). They are educational geometry — not surveyed rooms, not FDA drawings, not ADA certifications.

| File | Use |
| --- | --- |
| `snf-single-room-plan.svg` | CMS single-room square footage / aisle |
| `snf-double-room-plan.svg` | Double bedroom width problem |
| `seven-entrapment-zones.svg` | FDA/HBSW zone overview |
| `side-rail-geometry.svg` | Rail nicknames vs. openings |
| `room-walkthrough-sightline.svg` | Door-to-bed walk-through |
| `ada-resident-room-turn.svg` | Wheelchair turning (notional) |
| `overbed-table-clearance.svg` | Overbed vs. footplate |
| `nurses-station-sightline.svg` | Seated sightline at station |
| `mattress-zone3-gap.svg` | Rail–mattress canyon |
| `low-bed-deck-height.svg` | Low vs. standard deck |
| `medline-channel-punchout.svg` | Distributor channel (no logos) |
| `hospital-vs-residential-bed.svg` | Bed envelope vs. twin |
| `ward-to-private-room.svg` | Ward → private footprint |
| `privacy-curtain-track.svg` | Track + sprinkler |
| `spec-sheet-anatomy.svg` | Spec sheet fields |
| `bariatric-bed-envelope.svg` | Wider deck / aisle |
| `fire-code-labels.svg` | TB 117 vs. NFPA context |
| `bifma-vs-bed-system.svg` | Test-house contrast |
| `room-package-cutlist.svg` | Bid tab + cut list |
| `memory-care-loop.svg` | Wander loop + seating |
| `cms-f584-f917-tags.svg` | Survey tag primer |

## Cleared hot links (2026-09-14)

| Plate key | License | Institution | Commons / source page |
| --- | --- | --- | --- |
| `empty-ward-minneapolis` | CC BY 2.0 | Minneapolis Health Department | [Empty Beds in Ward…](https://commons.wikimedia.org/wiki/File:Empty_Beds_in_Ward_of_Hospital,_Minneapolis_Health_Department.jpg) |
| `patient-room-hospital-bed` | Public domain | Wikimedia Commons | [Patient room with hospital bed](https://commons.wikimedia.org/wiki/File:Patient_room_with_hospital_bed.jpg) |
| `hospital-bed-side-view` | CC BY-SA 4.0 | Wikimedia Commons | [Hospital bed](https://commons.wikimedia.org/wiki/File:Hospital_bed.jpg) |
| `ward-red-rover` | Public domain | U.S. Navy | [Hospital ward on Red Rover](https://commons.wikimedia.org/wiki/File:Hospital_ward_on_Red_Rover.jpg) |
| `iwm-hospital-ward` | Public domain | Imperial War Museum | [Hospital Ward Art.IWMARTLD43](https://commons.wikimedia.org/wiki/File:Hospital_Ward_Art.IWMARTLD43.jpg) |
| `wellcome-womens-ward-beds` | CC BY 4.0 | Wellcome Collection | [Women's Ward beds](https://commons.wikimedia.org/wiki/File:A_line_of_hospital_beds_in_the_Women%27s_Ward_Wellcome_L0038278.jpg) |
| `ashfield-nursing-home-exterior` | CC BY-SA 4.0 | Geograph / Wikimedia | [Ashfield Nursing Home](https://commons.wikimedia.org/wiki/File:Ashfield_Nursing_Home,_Wetherby_(18th_July_2020).jpg) |
| `wood-samples-cc0` | CC0 1.0 | Wikimedia Commons | [16 wood samples](https://commons.wikimedia.org/wiki/File:16_wood_samples.jpg) |
| `morris-recliner-met` | CC0 1.0 (Met Open Access) | The Metropolitan Museum of Art | [Reclining Morris Chair MET 235723](https://commons.wikimedia.org/wiki/File:Reclining_Morris_Chair_MET_235723.jpg) |
| `bedstead-met-dt2846` | CC0 1.0 (Met Open Access) | The Metropolitan Museum of Art | [Bedstead MET DT2846](https://commons.wikimedia.org/wiki/File:Bedstead_MET_DT2846.jpg) |
| `three-drawer-cabinet` | CC BY-SA 3.0 | Wikimedia Commons | [Three drawer wooden cabinet…](https://commons.wikimedia.org/wiki/File:Three_drawer_wooden_cabinet_with_carve-out_handles.jpg) |
| `drawer-organizer-kraftmaid` | CC BY-SA 4.0 | Wikimedia Commons | [KraftMaid Drawer with Wooden Organizer](https://commons.wikimedia.org/wiki/File:KraftMaid_Drawer_with_Wooden_Organizer.jpg) |
| `hospital-train-interior-1918` | No restrictions | U.S. National Archives | [Hospital Train Patient Car, 1918](https://commons.wikimedia.org/wiki/File:Interior_View_of_A_Hospital_Train_Patient_Car,_1918.jpg) |
| `mattress-store-worcestershire` | CC BY-SA 2.0 | Geograph | [Mattress store and decontamination](https://commons.wikimedia.org/wiki/File:Worcestershire_Royal_Hospital_-_mattress_store_and_decontamination_-_geograph.org.uk_-_7250260.jpg) |
| `poston-mattresses-nara` | Public domain | U.S. National Archives | [Poston mattresses NARA 539868](https://commons.wikimedia.org/wiki/File:Poston,_Arizona._Bedding_and_mattresses_are_moved_out_of_Ward_Three_in_the_Poston_General_Hospital_._._._-_NARA_-_539868.jpg) |
| `medical-warehouse-nara` | Public domain | U.S. National Archives / DPLA | [Medical supplies warehouse](https://commons.wikimedia.org/wiki/File:MEDICAL_SUPPLIES_IN_WAREHOUSE_No._108-C,_Medical_Supply_Depot_No._2,_Near_Gievre,_Loire_et_Cher,_France_-_DPLA_-_66474414d9caf727e1c6b70ba6f6cb74.jpg) |
| `wheelchair-symbol` | Public domain | Wikimedia Commons | [Wheelchair.svg](https://commons.wikimedia.org/wiki/File:Wheelchair.svg) |

`wellcome-womens-ward-beds` and `wheelchair-symbol` are registered for swap-in; current slug assignments use other plates. Keep rows when rotating art.

## Reserved (do not scrape)

- Medline or Medilodge catalog product photography and punchout heroes with logos
- Any image showing a resident or patient face (including “dignity” stock)
- AI-generated interiors, AI “diverse seniors,” or synthetic ward photography
- Vendor SNF room renders presented as BBF installs
- FDA/HBSW official PDF figures pasted without checking agency reuse terms (link out instead)
- BBF shop stills until Keith clears `PHOTO_CAPTIONS.md` OWNER rows

## BBF shop photography

`PHOTO_CAPTIONS.md` lists staged shop and room shots for a later pass. Those files are **not** in git until cleared; do not substitute stock faces.
