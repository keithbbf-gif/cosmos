# QUALIFIED SPEED BENCH — CCrew Roster (>= 16 TPS, <= $0.25 in / $1.00 out)

Added by Keith 2026-09-23. All models verified:
- Input <= $0.25 / 1M
- Output <= $1.00 / 1M
- Throughput >= 16 tps
- Context >= 256,000 tokens

| Model | Family | In ($/1M) | Out ($/1M) | Context | Latency | TPS | Coding ELO | DA ELO | Notes |
|---|---|---|---|---|---|---|---|---|---|
| **Tencent: Hy3 preview** | tencent | $0.18 | $0.60 | 262k | 4.3s | **69 t/s** | 58.8 | — | Top throughput paid |
| **NVIDIA: Nemotron 3.5 Lightning** | nvidia | $0.065 | $0.18 | 262k | 697ms | **62 t/s** | 26.8 | — | Sub-second latency |
| **Cohere: North Mini Code (free)** | cohere | **$0** | **$0** | 256k | 617ms | **58 t/s** | 36.5 | — | Free, coding-specialized |
| **Poolside: Laguna XS 2.1 (free)** | poolside | **$0** | **$0** | 262k | 667ms | **56 t/s** | — | — | Free fast coding MoE |
| **Dots Studio: Dots3-Note Preview (free)** | dots-studio | **$0** | **$0** | 512k | 1.3s | **51 t/s** | — | — | 512k free context |
| **OpenAI: GPT-6 Luna** | openai | $0.10 | $0.50 | 1.05M | 3.6s | **50 t/s** | — | — | Seated as WOMBAT |
| **Nex AGI: Nex-N2.5-Mini** | nex-agi | $0.025 | $0.10 | 262k | 864ms | **49 t/s** | — | — | Micro-cost ($0.025/M) |
| **inclusionAI: Ling 3.0 Flash VL (free)** | inclusionai | **$0** | **$0** | 262k | 2.4s | **46 t/s** | 57.0 | — | Free vision/code |
| **Qwen: Qwen3.7 Flash** | qwen | $0.03 | $0.13 | 1.0M | 801ms | **44 t/s** | — | — | 1M ctx + reasoning |
| **NVIDIA: Nemotron 3 Nano Omni (free)** | nvidia | **$0** | **$0** | 256k | 513ms | **38 t/s** | 13.8 | — | Fastest latency (513ms) |
| **Qwen: Qwen3.6 35B A3B** | qwen | $0.05 | $0.70 | 262k | 3.4s | **36 t/s** | 41.9 | — | 35B MoE |
| **Qwen: Qwen3.8 Flash** | qwen | $0.15 | $0.47 | 1.0M | 903ms | **35 t/s** | — | — | 1M ctx |
| **Google: Gemma 4 26B A4B (free)** | google | **$0** | **$0** | 262k | 1.1s | **35 t/s** | 39.3 | — | Free open Google |
| **Qwen: Qwen3.8 27B (free)** | qwen | **$0** | **$0** | 262k | 447ms | **34 t/s** | 68.1 | — | Free high-coding (68.1) |
| **Poolside: Laguna S 2.1 (free)** | poolside | **$0** | **$0** | 262k | 2.0s | **33 t/s** | — | — | Free MoE |
| **Tencent: Hy3** | tencent | $0.13 | $0.53 | 262k | 935ms | **33 t/s** | — | 1,186 | Balanced Tencent |
| **Qwen: Qwen3.8 Omni Flash** | qwen | $0.15 | $0.47 | 1.0M | 752ms | **31 t/s** | — | — | 1M multimodal |
| **Upstage: Solar Pro 4** | upstage | $0.09 | $0.36 | 524k | 3.0s | **29 t/s** | 52.7 | 1,192 | 70% off promo |
| **Thinking Machines: Inkling (free)** | thinkingmachines | **$0** | **$0** | 1.05M | 2.4s | **28 t/s** | 52.1 | 1,211 | 1M free coding (52.1) |
| **DeepSeek: DeepSeek V4 Flash 0731** | deepseek | $0.038 | $0.55 | 1.31M | 1.7s | **24 t/s** | 69.1 | 1,240 | High coding (69.1), NVMe cache |
| **Xiaomi: MiMo-V2.5** | xiaomi | $0.119 | $0.238 | 1.05M | 4.1s | **22 t/s** | 56.8 | 1,269 | 15% off, DA ELO 1269 |
| **Google: Gemma 4 31B** | google | $0.09 | $0.34 | 262k | 1.2s | **20 t/s** | 43.4 | — | Inexpensive Google open |
| **Z.ai: GLM 5.3 Flash** | zai | $0.075 | $0.25 | 1.0M* | 2.3s | **19 t/s** | 71.5 | 1,292 | High coding (71.5), 1M router ctx |
| **NVIDIA: Nemotron 3 Ultra (free)** | nvidia | **$0** | **$0** | 1.0M | 2.4s | **16 t/s** | 49.3 | 1,152 | 1M free |

*GLM context window pinned to 1,000,000 across all non-CloudFlare hosts per Keith's rule.
