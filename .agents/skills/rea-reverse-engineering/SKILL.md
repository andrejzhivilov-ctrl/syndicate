---
name: rea-reverse-engineering
description: >-
  Reverse engineer anything: inspect applications, native binaries, Electron apps, JavaScript, .NET assemblies,
  and APIs without source code. Explains how features work, traces data flow from UI to binary, and reconstructs
  working implementations. Use when the user asks to analyze, decompile, reverse-engineer, clone a feature, or inspect how software works.
---

# REA: Reverse Engineer Anything & REAP Playbook

Comprehensive toolset and methodology for reverse engineering software from user interface behavior down to native machine code.

## 4-Step Reverse Engineering Protocol

1. **Feature Tracing**:
   - Locate the user-facing entry point (button, menu, hotkey, CLI argument).
   - Trace the handler function, IPC message, network request, or event listener.
   - Map data flow: inputs -> transformation -> disk/network write.

2. **Binary & Runtime Inspection**:
   - Native binaries: Identify exported symbols, strings, section headers, and decompiled functions (Ghidra, Hopper, IDA style).
   - Electron / Node: Extract `resources/app.asar` (using `npx asar extract`), deobfuscate JavaScript bundles, trace IPC channels (`ipcRenderer.send`, `ipcMain.handle`).
   - .NET / C#: Decompile IL assemblies (ILSpy / dnSpy conventions).
   - Web / APIs: Inspect DevTools network payloads, websocket frames, and client state machines.

3. **Evidence-Based Reporting**:
   - Every claim must cite concrete evidence: function name, file path, memory offset, or intercepted HTTP payload.
   - Separate confirmed facts from working hypotheses.

4. **Cloning & Re-implementation**:
   - Write clean, standalone re-implementations of the discovered logic in Python, TypeScript, or Go.
   - Ensure the new implementation has zero dependencies on proprietary runtime hooks.

## Reference Investigation Prompts

See the comprehensive [REA Prompts Playbook](./references/REA_PROMPTS_PLAYBOOK.md) for ready-to-use investigation prompts across 16 categories:
- Feature tracing (any program)
- Native binary exploration
- Software & feature cloning
- Game logic & WASM porting
- Firmware & embedded binaries
- Android APK decompilation
- Electron & JavaScript bundle analysis
- Anti-cheat & protection auditing
