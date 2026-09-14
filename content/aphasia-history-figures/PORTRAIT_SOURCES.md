# Portrait Sources — plates ledger

Pack date: 14 September 2026 (image + SEO caption pass). **Real likenesses only** — Wikimedia Commons, NLM IHM, Wellcome, BIU Santé (Licence Ouverte). Never AI-generated faces.

On disk: `plates/<portrait_id>/plate.{jpg|png|svg}` plus **`plates/<portrait_id>/RIGHTS.md`** per plate. Profiles embed SEO `<figure>` blocks pointing at these paths.

| portrait_id | figure | cleared plate | license (file page) | source URL | credit line |
|-------------|--------|---------------|---------------------|------------|-------------|
| franz-joseph-gall | Franz Joseph Gall | yes | Public domain | https://commons.wikimedia.org/wiki/File:Franz_Joseph_Gall.jpg | Stipple engraving. Public domain. |
| jean-baptiste-bouillaud | Jean-Baptiste Bouillaud | yes | Licence Ouverte | https://commons.wikimedia.org/wiki/File:Bouillaud,_Jean-Baptiste_(1796-1881)_CIPN21514.jpg | BIU Santé CIPN21514. |
| paul-broca | Paul Broca | yes | Public domain | https://commons.wikimedia.org/wiki/File:Paul_Broca.jpg | Pierre Petit / Wellcome. |
| carl-wernicke | Carl Wernicke | yes | Public domain (NLM) | https://commons.wikimedia.org/wiki/File:C._Wernicke.jpg | J. F. Lehmann; NLM IHM. |
| ludwig-lichtheim | Ludwig Lichtheim | yes | Public domain (U.S.) | https://commons.wikimedia.org/wiki/File:Ludwig_Lichtheim.jpg | Lehmann 1925; NLM IHM. |
| john-hughlings-jackson | John Hughlings Jackson | yes | Public domain | https://commons.wikimedia.org/wiki/File:John_Hughlings_Jackson.jpg | Photogravure after Calkin, 1895. |
| henry-head | Henry Head | yes | Public domain (Commons) | https://commons.wikimedia.org/wiki/File:Henry_Head.jpg | Theodore C. Marceau; NLM IHM. |
| pierre-marie | Pierre Marie | yes | CC BY-SA 4.0 | https://commons.wikimedia.org/wiki/File:Pierre_Marie.jpg | Attribute; share alike if adapted. |
| jules-dejerine | Jules Déjerine | yes | Public domain | https://commons.wikimedia.org/wiki/File:Jules_Dejerine.jpg | Commons PD. |
| augusta-dejerine-klumpke | Augusta Déjerine-Klumpke | yes | Public domain (NLM) | https://commons.wikimedia.org/wiki/File:Augusta_D%C3%A9jerine-Klumpke.jpg | NLM IHM. |
| jacques-lordat | Jacques Lordat | yes | CC BY-SA 4.0 | https://commons.wikimedia.org/wiki/File:Jacques_Lordat.jpg | Lafosse after earlier plate. |
| theophile-alajouanine | Théophile Alajouanine | yes | CC0 1.0 | https://commons.wikimedia.org/wiki/File:Th%C3%A9ophile_Alajouanine.png | Courrier royal / Retronews. |
| aleksandr-luria | Aleksandr R. Luria | yes | Public domain (Commons-stated) | https://commons.wikimedia.org/wiki/File:Alexander_Luria.jpg | c. 1940s; photographer unknown. |
| johann-gesner | Johann A. P. Gesner | placeholder | — | — | No reliable plate. |
| kurt-goldstein | Kurt Goldstein | placeholder | — | — | Mid-century photos likely closed. |
| weisenburg-and-mcbride | Weisenburg / McBride | placeholder | — | — | Faculty archives likely closed. |
| joseph-wepman | Joseph M. Wepman | placeholder | — | — | |
| hildred-schuell | Hildred Schuell | placeholder | — | — | |
| jon-eisenson | Jon Eisenson | placeholder | — | — | |
| harold-goodglass | Harold Goodglass | placeholder | — | — | |
| edith-kaplan | Edith Kaplan | placeholder | — | — | |
| norman-geschwind | Norman Geschwind | placeholder | — | — | |
| andrew-kertesz | Andrew Kertesz | placeholder | — | — | Living. |
| martha-taylor-sarno | Martha Taylor Sarno | placeholder | — | — | Living. |
| audrey-holland | Audrey Holland | placeholder | — | — | |
| macdonald-critchley | Macdonald Critchley | placeholder | — | — | |
| wilder-penfield | Wilder Penfield | placeholder | — | — | |
| marsel-mesulam | M. Marsel Mesulam | placeholder | — | — | Living. |
| roman-jakobson | Roman Jakobson | placeholder | — | — | Most photos still in copyright. |

Re-run ingestion: `python3 content/aphasia-history-figures/portrait_plates_pass.py` (destructive to local plates; use only when refreshing from Commons).
