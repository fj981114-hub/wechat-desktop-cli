# 📱 WeChat Desktop CLI — Control WeChat from Your Terminal

> **Send messages, search contacts, and automate WeChat Desktop — all from the command line.**

A Python CLI tool that uses Windows Win32 API to directly control the WeChat Desktop application. No reverse engineering, no protocol hacks — just clean window automation.

## ✨ Features

- **📨 Send Messages** — Send any text/emoji to any WeChat contact
- **🔍 Search Contacts** — Find and open any contact's chat window  
- **✅ Check Status** — See if WeChat is running, window position, visibility
- **⚡ Fast** — Uses clipboard + SendInput for reliable text input

## 🔧 How It Works

WeChat Desktop 4.x is built on **Qt5** (`Qt51514QWindowIcon` class). This tool:

1. Finds the WeChat window via `EnumWindows` (Win32 API)
2. Activates and brings it to foreground
3. Uses `Ctrl+F` to open the search bar
4. Types the contact name via clipboard paste (`Ctrl+V`)
5. Presses Enter to open the chat
6. Pastes your message and presses Enter to send

## 🚀 Installation

```bash
pip install -e .
```

## 📖 Usage

```bash
# Check if WeChat is running
wechat status

# Send a message to a contact
wechat send --to "阿锋" --msg "😊 你好！"
wechat send --to "张三" --m "文件已发送，请查收"

# Search and open a contact
wechat search "李四"

# Bring WeChat to foreground
wechat activate
```

### Integrate with OpenCLI

```bash
opencli external register wechat
wechat send --to "阿锋" --msg "😊"
```

## 🏗 Architecture

```
wechat-desktop-cli/
├── pyproject.toml
├── README.md
└── src/wechat_desktop_cli/
    ├── __init__.py     — Package metadata
    ├── __main__.py     — python -m support
    ├── cli.py          — CLI argument parser
    └── controller.py   — Win32 API WeChat controller
```

## ⚠️ Requirements

- **Windows only** (uses Win32 API via `ctypes`)
- WeChat Desktop must be running and logged in
- No additional dependencies (uses Python stdlib + Windows API)

## 📄 License

MIT — Based on insights from the [OpenCLI](https://github.com/jackwener/OpenCLI) ecosystem.
