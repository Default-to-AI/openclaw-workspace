# Tasks

All tasks are written inline across your vault notes — this page queries and surfaces them in one place using the **Obsidian Tasks** plugin.

---

## How to use Tasks

### Writing a task anywhere in the vault

Type a checkbox in any note:

```
- [ ] Task description
```

That's a task. The plugin tracks it wherever it lives.

**Optional metadata you can append:**

| Syntax | Meaning | Example |
|---|---|---|
| `📅 YYYY-MM-DD` | Due date | `📅 2026-04-15` *(plugin requires ISO format — cannot use DD-MM-YYYY here)* |
| `⏫` / `🔼` / `🔽` | Priority (high / medium / low) | `⏫` |
| `🔁 every week` | Recurrence | `🔁 every monday` |
| `➕ YYYY-MM-DD` | Created date | auto-added if configured |
| `✅ YYYY-MM-DD` | Completion date | auto-filled on check |

You can also type the emoji directly or use the Tasks modal: place your cursor on a task line and press the hotkey (default: no hotkey set — go to **Settings → Hotkeys** and bind "Tasks: Create or edit task").

### Completing a task

Click the checkbox. If the task has a recurrence rule, a new instance is automatically created.

### Editing a task

Click the pencil icon that appears when hovering, or use the Create/Edit hotkey on the task line. The modal lets you set due date, priority, recurrence, and tags without typing emoji manually.

---

## Views

### Today

```tasks
not done
due today
```

### Overdue

```tasks
not done
due before today
```

### Upcoming (next 7 days)

```tasks
not done
due after today
due before in 7 days
sort by due
```

### All open tasks

```tasks
not done
sort by due
sort by priority
```

### Completed (last 7 days)

```tasks
done
done after 7 days ago
sort by done reverse
```

---

## Tips

- Tasks live in your domain notes, not here. This page is just the dashboard.
- Keep tasks close to context: a task about a Finance decision belongs in a Finance wiki page, not in a standalone list.
- Use priority sparingly — if everything is high priority, nothing is.
- The graph view won't show tasks, but Dataview can query them with more flexibility if you need custom views later.
