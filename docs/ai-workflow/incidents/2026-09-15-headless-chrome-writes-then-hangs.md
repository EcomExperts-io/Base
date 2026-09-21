---
title: "Headless Chrome wrote the screenshot and then never exited"
date: 2026-09-15
repo: Base
scope: generic
surfaced_by: hook
should_have_caught: .claude/scripts/render-screenshot.sh
status: harvested
---

# Headless Chrome wrote the screenshot and then never exited

## What happened

The first version of `render-screenshot.sh` ran `Google Chrome --headless=new
--screenshot=…` in the foreground. On the second invocation in a session
Chrome wrote the PNG and then stayed alive indefinitely; the calling command
hung, and the session's tool call timed out. macOS ships no `timeout` binary,
so the usual guard was not available.

## How it surfaced

A tool-call timeout while testing the verify pipeline, with the process still
visible in `ps` afterwards holding the throwaway profile directory.

## What fixed it

Running Chrome in the background, polling for the output file, and killing the
process once the file exists or a deadline passes. Renders now return in two to
three seconds with no leftover process.

## Which rule or check should have caught it, and why it did not

Nothing could have named this in advance; it is a platform behaviour. It is
recorded so the next person who wraps headless Chrome starts from the poll-and-
kill shape rather than rediscovering the hang.
