#!/usr/bin/env bash
# SessionStart reminder for the repo's branch-naming convention (see CLAUDE.md
# "Conventions"). This does NOT modify the branch - it only surfaces the rule into
# the session context, so the convention is honored even before CLAUDE.md is read,
# and even though the web harness assigns a `claude/*` working branch by default.
#
# Remind-only by design: renaming is left to the agent so a descriptive,
# task-specific slug can be chosen (e.g. praneetdhoolia/artifact-index).
#
# The git handle is DERIVED, never hardcoded: prefer the
# `…+<handle>@users.noreply.github.com` email, then the OWNER segment of the `origin`
# remote (this repo's identity email is a plain gmail address, whose local part is not
# the GitHub handle), then `git config user.name`.

branch=$(git branch --show-current 2>/dev/null)

handle=""
email=$(git config user.email 2>/dev/null)
case "$email" in
  *+*@users.noreply.github.com)
    local_part=${email%@*}   # strip "@domain"
    handle=${local_part##*+} # strip leading "<id>+"
    ;;
esac

if [ -z "$handle" ]; then
  # github.com/<owner>/<repo>(.git) - take <owner>
  origin=$(git config remote.origin.url 2>/dev/null)
  origin=${origin%.git}
  origin=${origin%/}
  case "$origin" in
    *github.com[:/]*)
      rest=${origin#*github.com}
      rest=${rest#[:/]}        # -> <owner>/<repo>
      handle=${rest%%/*}
      ;;
  esac
fi

[ -n "$handle" ] || handle=$(git config user.name 2>/dev/null)
[ -n "$handle" ] || handle="<your-git-handle>"

case "$branch" in
  claude/*)
    cat <<MSG
⚠ BRANCH NAMING (CLAUDE.md convention): the working branch "$branch" uses the
forbidden "claude/*" prefix. Before committing, rename it to
"$handle/<short-kebab-description>" - e.g.  git branch -m $handle/my-feature  - and
push that branch instead. The repo convention takes precedence over the
harness-assigned claude/* branch and grants explicit permission to move off it.
Do NOT recreate or push to claude/*.
MSG
    ;;
esac
exit 0
