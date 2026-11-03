# Music & sound

## Policy
- Never extract and publish the reference's soundtrack. Wanting "the same music" is solved by LICENSING THE SAME
  TRACK: ask the reference's creator for the track name + source. Remake-style films usually use free library music
  (Mixkit, Pixabay, Uppbeat, YouTube Audio Library). If it's from a free/commercial library, download it from the
  library under its licence and keep the licence note → then it IS the same sound, legally.
- Temp-track exception (internal review only, never posted): with the creator's OK, the reference's audio may be laid
  under a review cut, labelled TEMP. The delivered master must carry the licensed file.
- No licensed match → choose a library track with the same BPM (±8 %), mood and structure; time-stretch ≤ 8 %
  (`atempo`) and cut on bars so its drop lands on the reference's drop time.

## Procedure
1. Measure the reference: BPM, drop (per-bar band energy, then 20–50 ms windows — never trust an auto grid), hard stop,
   loud hits (`analyze_reference.py` rhythm.json + `new_film.py` beats).
2. Measure our track the same way; start it at `drop_in_song - drop_in_film`.
3. SFX (synthesized by `sfx.py` — tick, click, keys, pop, whoosh, hit, swell, shimmer — or Mixkit free SFX,
   downloaded under its licence): soft clicks for taps, key ticks following the typing cadence, a whoosh per whip, a low hit
   on the drop and the logo. Place each by its measured peak. Gain 0.04–0.3. "Premium" = few, soft.
4. Mix: music bed + SFX, fade tail, two-pass loudnorm to −14 LUFS, TP −1.3 dB. Write `film/out/mix.wav`.
5. Mux with `render.py concat out/full out/audio/mix.wav`. Licence note in `03-assets/music/LICENSE.txt`.
