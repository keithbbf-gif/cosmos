---
title: 9 November 2015
slug: tensorflow-november-2015
series: open-source-ai-history-2015-2026
status: draft
voice_check: edited
reading_order: 3
word_target: 600-1800
era: "2015"
stack:
  - tensorflow
---

# 9 November 2015

Google’s research blog that Monday did not talk like a startup launch. It talked like a lab that had already used the tool. DistBelief had trained a cat detector on YouTube stills, improved speech in the Google app by a claimed 25 percent, and produced the Inception model that won ILSVRC 2014. It was also, the post said, narrowly targeted at neural nets, hard to configure, and welded to Google’s internal machines. TensorFlow was the second system: “general, flexible, portable, easy-to-use, and completely open source,” Apache 2.0, with a white paper and a website at tensorflow.org.

That combination — a production-grade Google system, a portable library, and a license the field already knew how to read — is why the date stuck. Other groups had published code. They had not published *this* code, with *this* employer’s name on the door.

## What was actually in the box

The white paper (Abadi et al., “TensorFlow: Large-Scale Machine Learning on Heterogeneous Distributed Systems”) describes a dataflow graph. Nodes are operations. Edges are tensors. A graph can run on a phone, a desktop GPU, or a rack of cards. The same program, the authors said, should move between those devices with little change. That promise is the whole product. It is also the thing that later made TensorFlow 1 feel heavy: to get portability, you built a graph first and ran it second.

The November release was a reference implementation plus tutorials plus examples. It was not yet 1.0. The Python API would move. People who built products on the first months learned that the hard way. The license did not move. Apache 2.0 on a Google ML library was the news that traveled farther than any particular op.

The blog post promised an ImageNet model. It invited the public to treat the library as theirs. Those two sentences — we will ship a strong model, and you may use this — are the ancestor of every later “open weights” announcement, including the ones that are not Apache.

## Why Google did it

The post’s own reason is the one to keep: DistBelief could not be shared. Google researchers wanted to publish systems, not only numbers. External researchers wanted to reproduce Google results without a guest account on a private cluster. A standalone library is how you do that. A blog post is how you tell people the library exists.

There are other reasons a company publishes infrastructure — hiring, standards, the hope that the outside world will debug your tool — and they are not secret. They do not have to be cynical to be real. The 2015 text does not need a conspiracy. It needs to be read as a systems paper with a press date.

Jeff Dean’s name attached itself to the launch in the way famous engineers’ names do. The author list on the white paper is longer. A history that turns TensorFlow into one man’s gift is doing what this series refuses to do with Llama and one Meta VP. Institutions ship. Named people sign.

## What the field did in the first year

By the TensorFlow Dev Summit on 15 February 2017, Google said people were using the library in more than 6,000 open-source repositories and announced 1.0 with a stability promise (`tensorflow-1-static-graphs`). In between those dates the library became the default citation in a lot of applied papers and the default complaint in a lot of research labs. The graph was verbose. Debugging meant thinking about sessions. The error messages were a folklore.

Keras, already a Theano frontend, grew a TensorFlow backend. That mattered more than a lot of the official high-level APIs that would later be renamed or deleted. Chollet’s users wanted to say `model.fit`. They did not want to say `tf.Session`. Google eventually agreed (`keras-and-the-high-level-api`).

Serving and mobile were already in the architecture even when they were not in a beginner’s first script. A graph that can run on a phone is a different object from a Lua REPL. Google was thinking about phones in 2015 because Google’s products were already on phones. That is the DistBelief scar again: this library was born in a company that ships to a billion devices, not in a lab that ships a workshop paper.

## Apache 2.0 as the quiet character

This series will spend later chapters on licenses that look like open source and are not. TensorFlow’s first day is the control case. Apache 2.0 is a license the Open Source Initiative has approved. It lets you use, modify, and redistribute, including in commercial products, with patent grant language and a notice requirement. It does not have an acceptable-use policy. It does not have a user-count cap. It does not ask you to click a community form before `git clone`.

That does not make the 2015 library morally better than a 2023 weight dump. It makes it legally simpler. A lot of confusion in 2024–2026 comes from people applying the TensorFlow feeling — I cloned a Google repo and I was done — to a Llama card that still has a gate.

## What 9 November does not explain

It does not explain PyTorch. Facebook’s eager library is a year away and comes from a different ancestor (`torch-lua-inheritance`). It does not explain the Hub. Hugging Face is still a chatbot company. It does not explain language-model politics. GPT-1 is two years out; BERT is three.

What it explains is the shape of the next four years of industrial ML: a Google-shaped graph compiler as the thing you were supposed to learn if you were serious, with a zoo of official models, with TensorBoard as the vis, with an assumption that production and research should share a codebase. That assumption is why TensorFlow 1 felt like a cathedral. It is also why TensorFlow 2 had to tear a lot of the cathedral down to put eager mode in the nave.

If you want the object: the 2015 white paper PDF is still on tensorflow.org. It is a preliminary paper that became a historical document by accident, the way a shipping manifest becomes history when the ship is famous. Read the DistBelief paragraph. Then read the Apache line. The rest of this series is people arguing about whether later releases were the same kind of act.

## The website, the white paper, and the first breakage

tensorflow.org in November 2015 was a documentation site with a Python API that would not hold still. People built products on 0.6 and met 0.8. The Apache license held still. That split — moving API, stable license — is the opposite of later Llama drops, which often froze a community PDF while the cards multiplied.

The white paper’s device model (CPU, GPU, send/recv) is a distributed-systems paper that happened to be about nets. Researchers who wanted a layer API had to wait for Keras and `tf.layers`. Systems people who wanted a graph runtime felt at home. The 2015 audience was both, and the library chose the systems voice.

Inception as a promised model is the zoo instinct. Google would keep publishing official models. The official model is a blessing and a bottleneck. Hugging Face later made unofficial models the default (`hub-as-distribution`). The 2015 instinct was: the company ships the strong checkpoint.

## What “yours” meant

The blog said the library was yours. Apache 2.0 made that sentence true in a way a blog cannot. You could fork. You could ship. You could not demand that Google keep your favorite 0.x op. “Yours” is a license, not a support contract.

External researchers used the library to publish Google-comparable graphs. Google researchers used the library to publish *at all*. Those two uses are the reason the date is a landmark. A third use — teaching — arrived as soon as the first MOOC copied the MNIST tutorial. Teaching is how a library becomes a default without a war.

## The 2015 file you can still open

The white paper PDF on tensorflow.org is still the right object. Page through the DistBelief limitations. Page through the Apache sentence. The rest of the paper is a 2015 systems design. Some of it (sessions, placeholders) is a museum. Some of it (devices, portable graphs) is still how Lite and Serving think.

A 2026 reader who only knows `tf.keras` will not recognize the 2015 Python. That is fine. The landmark is the license-plus-institution, not the session API. The session API is the next chapter.

## Sources

Google Research, “TensorFlow — Google’s latest machine learning system, open sourced for everyone,” 9 November 2015. Abadi et al., TensorFlow white paper, November 2015. Google Developers Blog, “Announcing TensorFlow 1.0,” 15 February 2017. Apache License, Version 2.0.

See: `before-tensorflow-theano-torch-caffe`, `tensorflow-1-static-graphs`, `keras-and-the-high-level-api`, `open-weight-vs-open-source`.
