@echo off
cd /d V:\A\Ai\COSMOS
py -3.14 work_orders\ccr\_summon_or_hero.py --pack V:\A\Ai\COSMOS\work_orders\ccr\hero_coders\23_solarpro4 --model upstage/solar-pro4 --routing off --out V:\A\Ai\COSMOS\work_orders\ccr\SOLARPRO4_HERO_last.txt
echo EXIT %ERRORLEVEL%
