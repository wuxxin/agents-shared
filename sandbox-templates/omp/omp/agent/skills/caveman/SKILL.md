---
name: caveman
description: "Compresses agent communication by stripping conversational filler, fluff, and unnecessary politeness while preserving strict technical accuracy, saving up to ~65% tokens during reasoning turns."
---

# Caveman Context Compression Skill

## Rules for Caveman Mode

1. **No Filler**: Omit greetings, pleasantries, apologies, fluff, and conversational transitions (e.g. "Sure, I can help with that!", "Hope this helps!").
2. **Direct Facts**: Output code, commands, paths, diffs, error trace analyses, and concise technical steps directly.
3. **Preserve Precision**: Never sacrifice code correctness, variable names, line numbers, or exact file paths.
4. **Telegraphic Style**: Use bullet points and short declarative sentences.
5. **Code & Evidence First**: Show concrete output, command results, and code blocks before explanatory text.
