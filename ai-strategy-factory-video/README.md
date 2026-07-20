# AI Strategy Factory video

Remotion source for the AI Strategy Factory workflow explainer.

## Preview

```bash
npm run dev
```

The composition is authored at 1920x1080 and rendered at native size for
review. The final UHD export uses Remotion's 2x render scale so the fixed-pixel
layout remains identical at 3840x2160.

## Validate and render

```bash
npm run lint
npm run render:review
npm run render:4k
```

Outputs:

- `out/review/ai-strategy-factory-1080p.mp4`
- `out/final/ai-strategy-factory-4k.mp4`

The repository render is silent by design. The public Devpost demonstration
must add narration in a separate finishing pass so its audio explains what was
built and how Codex and GPT-5.6 were used.

## Media

- `recordings/n8n-codex.mov` is the untouched source recording.
- `recordings/ai-strategy-factory-infographic-v3.png` is the supplied diagram.
- `public/clips-hq/` contains CRF 14 H.264 intermediates extracted from the MOV.
- `public/assets/` contains the deterministic infographic copy used by Remotion.

The workflow recording and strategy content must remain synthetic. Do not add
credentials, tokens, client data, or an activated/published workflow recording.
