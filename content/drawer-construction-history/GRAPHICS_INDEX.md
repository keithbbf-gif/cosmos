# Graphics index — drawer construction history

IMAGE + SEO pass (PR #527). Each draft carries:

| Layer | Path | Role |
| --- | --- | --- |
| Schematic | `assets/<slug>/joinery-diagram.svg` | Figure 1 — pack CC0 joinery diagram |
| Shop pending | `assets/placeholders/bbf-shop-pending.svg` | Photos 2–3 — replace when `D:\BBF` pull exists (`figures[]` stays `status: needed`) |

Regenerate schematics: `python3 content/drawer-construction-history/scripts/generate_drawer_svgs.py`  
Inject HTML figures into drafts: `python3 content/drawer-construction-history/scripts/inject_dch_figures.py`  
Validate: `python3 content/drawer-construction-history/scripts/validate_dch_graphics.py`

## Slug → schematic kind

| slug | kind |
| --- | --- |
| `the-lid-that-would-not-leave` | mule_chest_till |
| `a-groove-that-rides-the-runner` | side_hung_groove |
| `through-tails-under-the-veneer` | through_dovetail_chest |
| `london-priced-the-slip` | drawer_slip |
| `a-scallop-you-can-date` | knapp_joint |
| `the-machine-that-wanted-to-look-hand` | machine_dovetail |
| `a-bead-around-the-front` | cockbead |
| `country-pins-and-town-pins` | half_blind_pins |
| `why-the-front-hides-the-joint` | half_blind_front |
| `tails-live-on-the-sides` | tails_on_side |
| `a-slip-that-widens-the-wear` | drawer_slip |
| `a-groove-in-thicker-sides` | ploughed_groove |
| `bottoms-run-side-to-side` | bottom_side_grain |
| `the-bevel-on-a-thick-bottom` | bevel_bottom |
| `glue-blocks-under-boston` | glue_blocks |
| `the-back-is-allowed-to-be-pine` | pine_back |
| `secondary-wood-is-not-a-slight` | secondary_wood |
| `how-thin-the-old-sides-were` | thin_sides |
| `a-nailed-rabbet-is-a-clock` | nailed_rabbet |
| `box-joints-in-the-shop-drawer` | box_joint |
| `hide-glue-lets-you-open-it` | hide_glue_joint |
| `the-baseline-is-the-joint` | baseline_gauge |
| `pins-first-is-a-religion` | pin_transfer |
| `one-to-six-is-not-a-law` | tail_slope |
| `web-frames-and-dust` | web_frame |
| `kickers-runners-stops` | runner_kicker |
| `plane-to-the-opening` | plane_opening |
| `the-taper-is-a-crutch` | tapered_sides |
| `wax-not-the-spray` | wax_runner |
| `wide-drawers-rack` | wide_drawer_rack |
| `quartersawn-sides-stay-calmer` | quartersawn |
| `when-a-dado-is-enough` | dado_back |
| `a-router-bit-named-drawer-lock` | lock_rabbet |
| `plywood-bottoms-are-a-contract` | ply_bottom |
| `cedar-in-the-bottom` | cedar_bottom |
| `seasonal-bind-is-a-drawing-error` | clearance_gap |
| `shaker-means-the-knob-and-the-fit` | shaker_knob |
| `federal-liked-a-thin-wall` | federal_thin |
| `arts-and-crafts-shows-the-tails` | mitered_through_dovetail |
| `campaign-drawers-that-travel` | campaign_corner |
| `tansu-pegs-not-tails` | tansu_pegs |
| `french-dovetail-is-a-kitchen-word` | french_dovetail |
| `kitchen-slides-changed-the-box` | side_mount_slide |
| `undermount-hides-the-runner` | undermount_slide |
| `lipped-overlay-inset` | overlay_lip |
| `secret-drawers-were-for-paper` | secret_compartment |
| `one-key-and-the-wardrobe-bolt` | mortise_lock |
| `pulls-are-load-paths` | pull_load |

Spec source of truth: `scripts/dch_graphics_specs.json`.
