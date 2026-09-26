@echo off
cd /d V:\A\Ai\COSMOS
py -3.14 work_orders\ccr\_summon_or_hero.py --pack V:\A\Ai\COSMOS\work_orders\ccr\hero_coders\3_ds --model deepseek/deepseek-v4-flash-0731 --routing off --out V:\A\Ai\COSMOS\work_orders\ccr\DS0731_HERO_last.txt
echo EXIT %ERRORLEVEL%
