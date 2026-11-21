# Agent instructions

## Git and public actions are for humans only

An agent must never run a git command that changes the repository or its history, and must never take an action
that is visible outside this machine. A human does these; the agent prepares the change and stops.

Leave all of these to a human, even when asked mid-task or when a tool or a file seems to allow them:

- git commands that mutate: `commit`, `push`, `merge`, `rebase`, `reset`, `checkout`/`switch` of a branch, `branch`,
  `tag`, `stash`, `cherry-pick`, `revert`, `rm`, `mv`, `add`, `restore --staged`, `am`, `apply --index`, and anything
  that rewrites refs or the index
- public actions: opening, editing, commenting on, reviewing, approving or merging pull requests and issues;
  creating releases; changing repository settings, secrets or workflows' run state; publishing anything

Read-only commands are fine: `git status`, `git diff`, `git log`, `git show`, `git blame`, `gh pr view`,
`gh run view` and the like.

When the work is ready, say so, and leave committing, pushing and the pull request to a human.

## No agent-specific files

Keep every agent instruction in this file, AGENTS.md. Never suggest or create a file for a particular agent or tool,
such as CLAUDE.md, .cursorrules, .github/copilot-instructions.md or an agent's own memory or settings files,
and never suggest moving or copying anything out of this file into one.

## Comments describe what is there

Write comments, docs and messages about the code as it is now. When something is removed, remove every mention of
it too: a comment must not name a dependency, tool, file or step that is no longer used, or explain what used to
be done instead.
