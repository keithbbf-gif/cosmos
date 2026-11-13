# Licenses

The chess rules engine in `chess_rules.js` is original code in this folder. No third-party chess library is copied into this tree.

chess.js 1.4.0 was reachable on jsDelivr when this folder was built. Its package.json says BSD-2-Clause. The compiled file `dist/cjs/chess.js` listed there is 107331 bytes. That build was not vendored. The perft counts used as checks are the ones published on the Chess Programming Wiki page Perft Results (initial position 20 / 400 / 8902 / 197281, plus the Kiwipete, position 3, position 4, and position 5 depths this folder's test actually runs).

No other third-party source is included. The page uses Unicode chess glyphs from the font on the machine.
