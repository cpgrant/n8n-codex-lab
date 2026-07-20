# AI Strategy Factory video

Remotion source for the AI Strategy Factory workflow explainer.

## Published demonstration

The current public, narrated version is:

**[Watch AI Strategy Factory on YouTube](https://www.youtube.com/watch?v=QKJJM996nmI)**

This URL is also used by the repository README and judge guide.

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

## Narration space

The two chapters from `00:55` to `01:25` are reserved for the maker's own
explanation of the development process. A natural script is:

> I directed Codex as a virtual engineering crew across VS Code, ChatGPT on the
> web, and the macOS app. Powered by GPT-5.6, it helped design the architecture,
> build and test the n8n, MCP, and FastAPI solution, migrate SQLite to
> PostgreSQL, operate the Docker infrastructure, document the system and
> licences, manage GitHub delivery, and produce this video. I retained every
> final decision and approval.

Speak naturally rather than reading faster to fit. The complete composition is
90 seconds, leaving ample room below the hackathon's three-minute limit.

## Media

- `recordings/n8n-codex.mov` is the untouched source recording.
- `recordings/ai-strategy-factory-infographic-v3.png` is the supplied diagram.
- `public/clips-hq/` contains CRF 14 H.264 intermediates extracted from the MOV.
- `public/assets/` contains the deterministic infographic copy used by Remotion.

The workflow recording and strategy content must remain synthetic. Do not add
credentials, tokens, client data, or an activated/published workflow recording.

## Publishing an updated video

[YouTube assigns a new URL to every new upload](https://support.google.com/youtube/answer/55770);
an existing upload cannot be replaced in place. After uploading an updated
video:

1. Confirm that it is public or unlisted as required, has narration, and plays
   without requiring the uploader's account.
2. Update the `demo-video` link definition in `README.md`.
3. Update the `demo-video` link definition in `docs/JUDGE-GUIDE.md`.
4. Update the published-demonstration link near the top of this file.
5. Find any stale references before committing:

   ```bash
   rg -n "youtube\.com/watch|youtu\.be/" README.md docs ai-strategy-factory-video
   ```

6. Open each resulting link in a signed-out browser and confirm that the title,
   audio, duration, and visibility are correct.

Do not delete the previous YouTube upload until every submission form and
external page that may reference it has also been updated. An optional YouTube
card or description on the old video can direct viewers to the new version.
