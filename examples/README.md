# Example: a 30-second reel

1. Put your takes in `takes/` named `01.mp4`, `02.mp4`, ... (order = timeline order).
2. `resolve-autopilot build takes "Reel"`
3. Trim pauses in Resolve, or let your assistant do it.
4. `resolve-autopilot look "Reel" "Reel v2"`
5. `resolve-autopilot mix "Reel v2" music.wav audio --sfx whoosh1.wav whoosh2.wav`
6. `resolve-autopilot add-audio "Reel v2" audio`
7. `resolve-autopilot render "Reel v2" out reel --size 1080 1920`

Bring your own music and sound effects: none are shipped.
