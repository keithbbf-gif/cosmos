@echo off
cd /d V:\A\Ai\COSMOS
py -3.14 work_orders\ccr\_summon_or_hero.py --pack V:\A\Ai\COSMOS\work_orders\ccr\hero_coders\15_qwen37 --model qwen/qwen3.8-flash --routing off --out V:\A\Ai\COSMOS\work_orders\ccr\QWEN38FLASH_HERO_last.txt
echo EXIT %ERRORLEVEL%
