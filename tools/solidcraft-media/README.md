# SolidCraft course media

Everything on the SolidCraft pages (`en|cs/tutorials/solidcraft*`) is generated, so it can be
regenerated when the SolidCraft UI changes.

## Checkpoints (`stls/solidcraft/*.sc`)

Each lesson's checkpoints are built by `solidcraft-cli` from the JSON scripts in `scripts/`,
each stage on top of the previous one:

```sh
cd tools/solidcraft-media
solidcraft-cli run scripts/plate/01-sketch.json --save plate-01-sketch.sc
solidcraft-cli run scripts/plate/02-extrude.json --in plate-01-sketch.sc --save plate-02-extruded.sc
...
solidcraft-cli snapshot plate-04-parametric.sc --out plate-04-parametric.png --no-grid --width 1000 --height 625
```

`scripts/comb/05-sweep.json` produces `comb-sweep-result.json` (`--results --json-out`), and
`scripts/comb/06-export.json` the per-configuration STL/3MF/STEP files.

## Screenshots and clips (`images/solidcraft/`)

Start SolidCraft with a clean settings folder on a control port, then run the drivers:

```sh
export SOLIDCRAFT_CONTROL_TOKEN=$(openssl rand -hex 32)
SOLIDCRAFT_SETTINGS_DIR=/tmp/sc-settings solidcraft --control 27900 &
python3 shots.py          # stills -> ../../shots/   (window must be visible on screen)
python3 clips.py          # mp4 clips -> ../../clips/  (agent cursor + ~4 fps window frames)
```

`sc.py` is the one-call control-channel client both drivers use. The paths at the top of
`shots.py` assume the checkpoints live in `../media/ckpt/<lesson>/`; adjust `CK` when running
from the repository. Callouts on `window-callouts.png` are drawn with ImageMagick (see the
`magick` command in the git history of this folder).
