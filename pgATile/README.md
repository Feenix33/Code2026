# Tile Loop Game - Version 1

Single-player 8x8 Pygame tile-loop game.

## Supply
100 tiles: 40 straight, 50 corner, 10 quad corner.
Four tiles are exposed. A replacement is drawn after each placement.

## Rules
- Place on any empty board square.
- No penalty for disconnected paths.
- Neighboring paths connect only when both adjacent sides have endpoints.
- Straight connects opposite sides.
- Corner connects adjacent sides.
- Quad Corner contains two independent corner paths.
- Check for loops after every placement.
- 1 point per tile in a loop.
- A Quad Corner is counted twice.
- A Quad Corner used by a second independent loop gets +5.
- Game ends after 64 placements.
- Final board remains visible on the game-over side panel.

## Controls
Mouse: select, move, place.
R: clockwise rotation.
L: counter-clockwise rotation.
ESC: quit.
Game over: Y = play again, N = quit.

## Sprite sheet
sprite_generator.py creates the generated artwork.
Set gWRITE_SPRITE_SHEET in constants.py to False to stop saving the PNG.
The generated file is assets/generated_tiles.png.
