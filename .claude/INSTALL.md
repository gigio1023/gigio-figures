# Install these skills for Claude Code

## Preferred

```bash
npx skills add gigio1023/gigio-figures@technical-diagram --agent claude-code
npx skills add gigio1023/gigio-figures@drawio-diagram --agent claude-code
npx skills add gigio1023/gigio-figures@data-chart --agent claude-code
npx skills add gigio1023/gigio-figures@eli5-figure --agent claude-code
```

Install only the skills you want; each command is independent.

## Manual install

```bash
git clone https://github.com/gigio1023/gigio-figures.git ~/.claude/gigio-figures
mkdir -p ~/.claude/skills
ln -s ~/.claude/gigio-figures/skills/technical-diagram ~/.claude/skills/technical-diagram
ln -s ~/.claude/gigio-figures/skills/drawio-diagram ~/.claude/skills/drawio-diagram
ln -s ~/.claude/gigio-figures/skills/data-chart ~/.claude/skills/data-chart
ln -s ~/.claude/gigio-figures/skills/eli5-figure ~/.claude/skills/eli5-figure
```

Claude Code normally detects `SKILL.md` changes live. Restart only if the new top-level skills directory was created after the session started or a skill does not appear.
