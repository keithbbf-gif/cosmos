---
title: Doing algebra in a pixel pipe
dek: Before CUDA, people hid linear algebra inside colors. The trick worked. It was also a cry for help.
slug: 04-shader-algebra-in-a-pixel-pipe
series: AI Compute Chip Magazine
status: staged
voice_check: edited
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
---

# Doing algebra in a pixel pipe

The first time I saw someone multiply matrices on a graphics card, they were talking about textures. Not as pictures — as arrays. You uploaded a grid of floats dressed as an image, ran a pixel shader that pretended to shade a quad, and read the “color” back as an answer. The hardware was a GeForce or a Radeon from the programmable-shader years. The API was OpenGL or Direct3D. The paper trail is the GPGPU workshop literature and the GPU Gems chapters, not a product launch.

This is easy to mythologize. It was also, as anyone who did it will tell you, miserable. You had no integers you could trust. You had no scatter writes that felt like a normal memory store. You had four-wide vectors because a pixel is rgba. You had a graphics driver that could decide your “compute job” was a frame and evict it. Debugging meant looking at a picture of your residual and hoping the pink pixels were a NaN and not a viewport.

Why do it? Because the arithmetic throughput was already ridiculous compared with a 2003 CPU, and the memory system was built to paint screens at sixty hertz. If your problem was data-parallel and fat with multiply-adds — convolution, Monte Carlo, some fluid solvers, early image filters — the card would finish while the CPU was still being polite. The price of admission was speaking graphics.

Mark Harris and others put a name on the movement: general-purpose computation on GPUs, GPGPU. The Stanford Brook work tried to hide the costume. GPU Gems (2004) had Ian Buck and Tim Purcell’s “A Toolkit for Computation on GPUs.” SIGGRAPH courses taught the same carnival trick to rooms of people who had come for shadows and left with a reduction kernel. The important public fact is not that a genius invented GPGPU in a garage. It is that a lot of labs did the same ugly thing at the same time because the hardware left them no cleaner door.

The hardware that made the trick possible was the programmable shader. NVIDIA’s GeForce 3 (2001) brought DirectX 8 vertex and pixel shaders into a shipping consumer card. ATI’s Radeon 8500 fought in the same generation. DirectX 9 and Shader Model 2, then 3, made the shaders less like a wind-up toy and more like a tiny vector machine. Once you could write arithmetic that was not a fixed-function T&L equation, you could write arithmetic that was not about triangles at all.

A pixel pipe is a bad computer that happens to be fast. That sentence is the whole era. It is also why CUDA, when it arrived, felt like someone had opened a window. You could keep the fast part and drop the costume. People who never wrote a fragment shader for a dot product sometimes assume CUDA invented GPU computing. The public papers say otherwise. CUDA industrialized a practice that already had a workshop, a mailing list, and a smell.

There is a temptation to treat the shader trick as cute prehistory. Resist that. The constraints of the trick shaped what the first compute architectures bothered to fix. Scatter, shared memory, integer support, a debugger that was not RenderDoc-for-residuals — those were answers to complaints already in the literature. When NVIDIA later said CUDA let cores “communicate, synchronize, and share data,” the press release was written against this background. You do not boast about sharing data unless last year’s machine could not.

If you want to feel the era without romanticizing it, read a GPGPU paper’s limitations section. They are all the same: precision, branching, memory model, the graphics API in the way. Then look at the speedup graph anyway. People tolerated the costume because the number at the end was real.

A standalone article should not turn this into a moral about software layers. The moral, if there is one, is smaller. When a machine is fast at the wrong language, the users will lie to it. They will call a matrix a texture. They will call a kernel a shader. They will call a scientific application a game so the driver keeps the clocks up. That is not cleverness for its own sake. That is what a platform looks like the year before it admits it is a platform.

## Sources

- GPU Gems (2004), Chapter 37, Ian Buck and Tim Purcell, “A Toolkit for Computation on GPUs.”
- Brook for GPUs, SIGGRAPH 2004 (Buck, Foley, Horn, Sugerman, Fatahalian, Houston, Hanrahan).
- Period GPGPU.org materials and SIGGRAPH GPGPU courses (mid-2000s).
- Public DirectX 8 / GeForce 3 and DirectX 9 shader-model timeline.
