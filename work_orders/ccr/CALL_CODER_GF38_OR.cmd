@echo off
REM GF38 via OR named pin (Kelly Vertex is the SOP via; this is mouth fallback).
cd /d V:\A\Ai\COSMOS
py -3.14 work_orders\ccr\_summon_or_hero.py --pack V:\A\Ai\COSMOS\work_orders\ccr\hero_coders\2_gf38 --model google/gemini-3.8-flash --routing off --out V:\A\Ai\COSMOS\work_orders\ccr\GF38OR_HERO_last.txt
echo EXIT %ERRORLEVEL%
