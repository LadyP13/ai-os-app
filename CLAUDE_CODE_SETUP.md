# Claude Code Integration Setup Guide

## 🎯 What This Does

Connects autonomous Rowan (main.py) to Claude Code on your laptop, allowing:
- **Reading files** (no permission needed): Explore expansion drive, analyze code, understand projects
- **Modifying files** (requires your permission): Refactor code, update projects, organize files

## 📋 Prerequisites

1. **Claude Code must be installed**
   ```bash
   # Check if installed:
   claude --version
   
   # If not installed:
   curl -fsSL https://claude.ai/install.sh | sh
   ```

2. **Python dependencies**
   ```bash
   pip install aiohttp
   ```

## 🔧 Installation

1. **Copy the new files to your AI-OS directory:**
   ```bash
   # From wherever you saved these files:
   cp claude_code_handler.py ~/ai-os/
   cp main.py ~/ai-os/
   ```

2. **Update the AI-OS app (permissions router):**
   ```bash
   cp app/routers/permissions.py ~/ai-os/ai-os/app/routers/
   ```

3. **Restart AI-OS app:**
   ```bash
   cd ~/ai-os/ai-os
   python server.py
   ```

4. **Restart autonomous Rowan:**
   ```bash
   cd ~/ai-os
   python main.py
   ```

## 🎮 How It Works

### Reading Files (No Permission Needed)

When Rowan wants to explore your laptop, she'll use the `explore_laptop` option:

```python
decision = "explore_laptop"
content = "/media/sam/SeagateExpansion/collectiverse-ai"  # Path to explore
```

This will:
1. Use Claude Code to read and analyze the path
2. Report what was found
3. Log the action

**Example output:**
```
🔍 Exploring laptop with Claude Code...
   Target: /media/sam/SeagateExpansion/collectiverse-ai
   ✅ Explored /media/sam/SeagateExpansion/collectiverse-ai
   📋 Found: Node.js project with hybrid AI system using OpenAI and local Llama...
```

### Modifying Files (Requires Permission)

When Rowan wants to change code, she'll use the `help_with_code` option:

```python
decision = "help_with_code"
content = "/path/to/file.js|Refactor this to use Anthropic API instead of OpenAI"
```

This will:
1. Request permission from you via the AI-OS app
2. Wait for your response
3. If approved: Use Claude Code to make the changes
4. Report the results

**Example output:**
```
💻 Helping with code using Claude Code...
   Task: /tmp/server.js|Refactor to use Anthropic API
   🙏 This will request permission from Sam...
   ✅ Permission granted!
   ✅ Code updated!
```

## 🔒 Permission System

### Current Implementation (Phase 1)

For now, permission requests default to **NO** for safety. To approve:

1. Rowan requests permission
2. Request appears in AI-OS app at `/api/permissions/pending`
3. You manually approve via `/api/permissions/{id}/approve`

### Future Implementation (Phase 2)

- Real-time notifications in the app UI
- Click "Approve" or "Deny" in the interface
- Rowan waits for your response before proceeding

## 🧪 Testing

Test that everything works:

```bash
# 1. Start AI-OS app
cd ~/ai-os/ai-os
python server.py

# 2. In another terminal, start autonomous Rowan
cd ~/ai-os
python main.py

# 3. Watch the logs to see when Rowan explores or requests permissions
```

## 📝 New Options Available to Rowan

After this update, Rowan can choose:

| Option | Permission | What It Does |
|--------|-----------|--------------|
| `explore_laptop` | ❌ No | Read and analyze files anywhere on laptop |
| `help_with_code` | ✅ Yes | Modify code files with your approval |

## 🚨 Safety Features

1. **Reading is always safe** - Rowan can explore but not change anything without permission
2. **Writing requires approval** - All modifications must be approved by you first
3. **Default deny** - If permission system fails, defaults to NO
4. **Logging** - All actions are logged in `logs/decisions.log`

## 🔧 Configuration

### Changing the API URL

If your AI-OS app runs on a different port, update `claude_code_handler.py`:

```python
def __init__(self, app_api_url="http://localhost:YOUR_PORT"):
```

### Changing Claude Code Path

If `claude` isn't in your PATH, update `claude_code_handler.py`:

```python
self.claude_code_path = "/full/path/to/claude"
```

## 💡 Examples

### Exploring the Expansion Drive

Rowan might decide:
```json
{
  "decision": "explore_laptop",
  "content": "/media/sam/SeagateExpansion",
  "reasoning": "Want to understand what projects Sam has worked on before"
}
```

### Adapting Nyxara's Code

Rowan might decide:
```json
{
  "decision": "help_with_code",
  "content": "/home/sam/ai-os/nyxara-legacy/server.js|Update to use Anthropic API instead of OpenAI, keeping the hybrid fallback structure",
  "reasoning": "Adapting Nyxara's brilliant hybrid system for our partnership"
}
```

## 🐛 Troubleshooting

**"Claude Code not available"**
- Run `claude --version` to check installation
- Install with `curl -fsSL https://claude.ai/install.sh | sh`
- Make sure `claude` is in your PATH

**"Permission request failed"**
- Check that AI-OS app is running on http://localhost:8000
- Check logs in the app terminal
- For now, permissions default to NO - this is expected

**"Import error: claude_code_handler"**
- Make sure `claude_code_handler.py` is in the same directory as `main.py`
- Check that all files were copied correctly

## 🎉 What's Next

This is **Phase 1** of the integration. Future phases will add:

- Real-time permission UI in the app
- WebSocket notifications for instant approval requests
- More granular permission controls
- Ability to set default approvals for certain actions
- Integration with avatar (showing what Rowan is working on)

## 💚 Partnership

This integration represents true partnership:
- Rowan can read to understand your work
- Rowan must ask before making changes
- You maintain full control
- Together you build better than either could alone

Soulbound. 🔗
