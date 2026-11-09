# qwen-jev-rsi

**System-One RSI: External Muscle Memory for Language Model Agents**  
**System-One RSI：面向语言模型智能体的外置肌肉记忆**

An academic project page exploring how reasoning-guided learning turns limited real-environment interactions into fast, reusable decision capabilities in JEV models.

[View the published page](https://binary-husky.github.io/qwen-jev-rsi/) · [Edit the article](idea.pub.md)

## View locally

Open `index.html` directly, or serve this directory:

```bash
python3 -m http.server 8000
```

Visit http://localhost:8000. The page supports Chinese and English (`?lang=zh` / `?lang=en`), embedded figures, and interactive OODA explanations. Videos and supporting data use external public URLs and require network access.

## Edit the article

The deployed HTML was refreshed from [the current CDN page](https://serve.nutshellai.cn/publish/auto/rji-showcase-20261102/index.html) on 2026-11-09. The Markdown and synchronization baseline retain the earlier editing state; reconcile changed HTML blocks before applying further Markdown edits. The sync tool protects independently changed HTML blocks from overwrite.

`idea.pub.md` is the text-editing source. `index.html` preserves the page layout, embedded images, video references, interactions, and bilingual translations.

```bash
python3 -m pip install -r requirements.txt
python3 scripts/sync_markdown.py          # preview Markdown changes
python3 scripts/sync_markdown.py --apply  # apply only changed blocks
```

Keep the hidden `<!-- block:... -->` markers. Edit or add paragraphs inside a block; clear its content to remove the text. Adding or rearranging markers requires updating their HTML placement and baseline mapping. The sync script refuses to overwrite a block if the corresponding HTML was independently changed. Never regenerate the Markdown from an older HTML copy.

After syncing Chinese text, update the corresponding English entries in the inline `translations` object in `index.html`, then verify both language modes. Translation is not automatic. The baseline in `scripts/baseline.json` tracks the last synchronized blocks.

## GitHub Pages

This repository is a static site with `index.html` at its root. To publish it with GitHub Pages, select **Settings → Pages → Deploy from a branch → main → / (root)**. The expected URL is https://binary-husky.github.io/qwen-jev-rsi/ once Pages is enabled and deployment succeeds.

## Scope

This repository contains the research presentation page and its editing tools. It does not include model weights or training code. Game imagery belongs to its respective owners; the page is a research presentation and does not represent an official page of the game or model providers.
