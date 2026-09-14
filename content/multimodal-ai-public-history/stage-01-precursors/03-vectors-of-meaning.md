---
id: "03"
slug: vectors-of-meaning
title: Vectors of meaning
stage: 01-precursors
stage_title: Precursors (before the 2021 hinge)
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Mikolov et al., word2vec papers, 2013"
  - "Pennington et al., GloVe, 2014"
  - "Frome et al., DeViSE, NeurIPS 2013"
  - "Kiros et al., skip-thoughts, 2015 (language-side neighbor)"
does_not_claim:
  - "that word2vec 'invented' distributional semantics"
  - "exact geometric claims beyond the public examples"
last_reviewed: 2026-09-14
---

# Vectors of meaning

The first time I saw the king–queen arithmetic, I had the same cheap thrill everyone else had. You subtract man, add woman, and the nearest neighbor is something you can tell a civilian. Meaning, for a minute, looked like a direction.

That thrill is older than word2vec. Distributional semantics is a twentieth-century idea: you shall know a word by the company it keeps. What 2013 did in public was make the company a vector you could actually hold. Mikolov’s group showed that a shallow model on a lot of text produced regularities people could poke. GloVe told a related story with a matrix factorization accent. The important public fact was not the objective. It was that *geometry* became a way the field talked about meaning.

Vision people heard that and wanted in.

If words live on a manifold where similar usage lands nearby, maybe a photograph of a dog should land near the word *dog*, and maybe a photograph of a wolf should land a little to the side, toward *wild* or *canis*. You would not need a 1000-way softmax. You would need a map. New nouns could be reached by walking. That is the dream inside DeViSE and a cluster of visual-semantic embedding papers: train a visual feature extractor, then push those features toward a frozen (or jointly trained) word space.

I want to stay honest about how this felt at the time. It felt like a clever transfer trick, not like a new industry. The word vectors were small. The image features were whatever a ConvNet of that year could give you. The datasets were the usual suspects. Zero-shot recognition — naming a class you never trained on, because you had its word vector — showed up in tables and did not show up on phones. The geometry was real enough to publish and not yet real enough to reorganize a lab.

There is a reason. Word geometry is a geometry of *usage*. *Bank* sits near money and near river if your corpus is confused, or it splits if your corpus is kind. Picture geometry is a geometry of *appearance*, plus whatever the photographer chose to include. The word *apple* in news text is a company more often than a fruit. The image “apple” on the web is a fruit, a logo, a storefront, a pie. A linear map between those geometries is a hopeful instrument. Sometimes it plays a tune. Often it plays the dataset.

Still: the idea that a joint space could *replace a classifier* is already here, years before CLIP. CLIP’s public contribution is not “what if we embedded images and text together.” It is what happens when the text is a full caption (or a title, or an alt), the image encoder is a modern stack, the loss is contrastive at batch scale, and the pairs number in the hundreds of millions. The ancestor is the joint. The phase change is the supervision and the scale.

I also want the language-only neighbor on the table. Skip-thoughts and later sentence encoders tried to give *sentences* a vector, not just words. If you are going to retrieve a picture with “a red car parked under a neon hotel sign,” you do not want a bag of word2vec averages. You want a sentence that knows *under* is a relation. The 2010s spent a lot of ink on whether that sentence vector should come from an unsupervised skip, a supervised inference task, or a transformer that had read the internet. CLIP, in the public paper, mostly sidesteps the philosophy: a text transformer reads the string you typed. The string can be a word or a prompt template. The space does the rest.

A human habit I still catch in myself: treating the vector space as a place where meaning *is*, rather than a place where a loss left a dent. The king–queen demo is a dent that happens to be pretty. CLIP-space “a photo of a…” templates are dents that happen to be useful. Neither is a theory of concepts. Both are public evidence that geometry can be an API.

If you only remember one thing from this draft, remember the invitation. Once meaning was a direction, pictures got invited to the same party. They arrived late, underdressed, and then in 2021 they ate the food. The next few drafts are the awkward years in between: captions that looked like seeing, questions that looked like reason, and embeddings that were already pointing at the door.
