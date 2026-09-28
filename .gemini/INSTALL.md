# Install these skills for Gemini CLI

## Preferred

```bash
npx skills add gigio1023/gigio-figures@technical-figure --agent gemini-cli
npx skills add gigio1023/gigio-figures@drawio-diagram --agent gemini-cli
npx skills add gigio1023/gigio-figures@eli5-figure --agent gemini-cli
```

Install only the skills you want; each command is independent.

`technical-figure` and `eli5-figure` render with Node.js 20+ and a Chromium-family browser. Before the first figure, run `bash scripts/setup.sh` from the installed skill directory; it installs pinned npm packages and OFL fonts into `~/.cache/technical-figure` and never installs a browser.

## Manual install

```bash
git clone https://github.com/gigio1023/gigio-figures.git ~/.gemini/gigio-figures
mkdir -p ~/.gemini/skills/technical-figure ~/.gemini/skills/drawio-diagram ~/.gemini/skills/eli5-figure
cp -R ~/.gemini/gigio-figures/skills/technical-figure/. ~/.gemini/skills/technical-figure/
cp -R ~/.gemini/gigio-figures/skills/drawio-diagram/. ~/.gemini/skills/drawio-diagram/
cp -R ~/.gemini/gigio-figures/skills/eli5-figure/. ~/.gemini/skills/eli5-figure/
```

Restart Gemini CLI after copying.
