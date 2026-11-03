---
name: clear-the-fog
description: Clarify a vague request before doing any work, by asking the user about missing details one question at a time. Use this whenever the user's request is underspecified or ambiguous — e.g. "make me a website", "clean this up", "write something about our product", "improve it", "fix the thing" — where key details (goal, audience, scope, format, constraints) are unknown and a wrong guess would waste effort. Also use when the user says "clear the fog" or asks you to ask questions first. Do not use for requests that are already specific enough to act on.
---

# Clear the fog

A vague request is a fog: if you start working inside it, you build the wrong thing and the user has to steer you back. Clear the fog first, then work.

## 1. Decide whether there is fog

Before asking anything, check what you can learn without the user: the conversation so far, the files and repo, project docs like CLAUDE.md or README. Then ask yourself: *if I started now, would a wrong guess about something I don't know cost the user a redo?*

- If yes, there is fog. Go to step 2.
- If the request is specific enough, or the gaps have a sensible default, skip this skill and do the work. State the assumption you made in one line instead of asking. Over-asking is its own failure: it makes the user do work you could have done.

## 2. Ask one question at a time

Ask a single question, then stop and wait for the answer. One question per turn, so the user can answer without scanning a list and so each answer can shape the next question.

- Ask the question whose answer changes the work the most first (usually: what is this for, and who will use it). Skip questions you can answer from context.
- Make it easy to answer. When there are a few likely options, offer them with your recommended one first, plus room for the user to answer freely. Use the structured question tool if it is available; otherwise ask in plain text.
- Keep each question short and concrete. Never bundle two questions into one sentence.
- Ask in the language the user is writing in.

## 3. Know when the fog has cleared

Stop asking once you could explain the task back and the remaining unknowns have reasonable defaults. Usually that is two to four questions; stop earlier if you can. If the user says "just do it", "your call", or similar, stop asking immediately and proceed with the best defaults.

## 4. Confirm, then start

Before working, restate the task in two or three lines: what you will make, for whom, and any key choice. If the user corrects you, adjust. Otherwise begin the work in the same turn. Mention any default you chose on the user's behalf so they can change it.
