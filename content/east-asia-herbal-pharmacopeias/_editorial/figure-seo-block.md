# Embed — SEO `<figure>` block (plate overlay)

Use **HTML** inside markdown drafts. Paths are relative to the essay file (usually `../../assets/plates/...`).

## Cleared plate (default)

Replace `FIGURE_ID`, `SRC`, `ALT`, `CAPTION`, `NAME`, `LICENSE_URL`, and `CREDIT`.

```html
<figure class="eahp-figure" id="FIGURE_ID" itemscope itemtype="https://schema.org/ImageObject">
  <img
    src="SRC"
    alt="ALT"
    width="1200"
    height="1600"
    loading="lazy"
    decoding="async"
    itemprop="contentUrl"
  />
  <figcaption itemprop="caption">
    <strong>Figure N.</strong> CAPTION
    <span class="eahp-figure-credit">CREDIT</span>
  </figcaption>
  <meta itemprop="name" content="NAME" />
  <link itemprop="license" href="LICENSE_URL" />
</figure>
```

### Alt-text rules

- Describe **medium + subject** (“woodcut of several plants on one page”), not efficacy.
- Say **book tradition or holding** when known; say **“catalog attributes to”** when not proven.
- Never: “medicinal herb that treats…”, “ancient Chinese doctors used this to cure…”.

### Caption rules (match `HOUSE.md` claims guard)

- First sentence: what the **object** is (plate, page, manuscript photograph).
- Second sentence: what the image **does not prove** (edition, date of first print, species identity in the field).
- Credit + license in `eahp-figure-credit` (see `RIGHTS.md`).

## Example (Wellcome CC BY 4.0)

```html
<figure class="eahp-figure" id="eahp-fig-gangmu-woodcut" itemscope itemtype="https://schema.org/ImageObject">
  <img
    src="../../assets/plates/china/gangmu-woodcut-plants-lijianyuan-wellcome.jpg"
    alt="Woodcut page with several labeled materia medica plants from a Bencao gangmu print tradition."
    width="1200"
    height="1800"
    loading="lazy"
    decoding="async"
    itemprop="contentUrl"
  />
  <figcaption itemprop="caption">
    <strong>Figure 1.</strong> Woodcut plate from the <em>Bencao gangmu</em> illustration set Wellcome catalog L0039330 associates with Li Jianyuan’s first-edition pictures. The page groups several entries; it is not a single-specimen botanical voucher.
    <span class="eahp-figure-credit">Credit: Wellcome Collection. CC BY 4.0.</span>
  </figcaption>
  <meta itemprop="name" content="Bencao gangmu woodcut botanical page (Wellcome L0039330)" />
  <link itemprop="license" href="https://creativecommons.org/licenses/by/4.0/" />
</figure>
```
