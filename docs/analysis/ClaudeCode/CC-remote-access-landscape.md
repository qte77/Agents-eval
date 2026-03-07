---
title: CC Remote Access Landscape
source: https://omnara.com, https://cloudcli.ai, https://code.claude.com/docs/en/remote-control
purpose: Comparison of remote access options for monitoring and steering Claude Code sessions (Ralph loop, teams, baselines) from mobile/web.
created: 2026-03-07
---

**Status**: Landscape research (informational — not implementation requirements)

## Problem Statement

Ralph loop and CC teams runs are long-running interactive sessions. Currently, the developer must stay at the terminal to provide input, approve permissions, or steer when stuck. Remote access enables monitoring and steering from phone/web without being desk-bound.

## Options Compared

<!-- markdownlint-disable MD013 -->

| Aspect | CC Remote Control (native) | Omnara | CloudCLI | DIY (tmux + Tailscale) |
| ------ | -------------------------- | ------ | -------- | ---------------------- |
| **Type** | Built-in CC feature | Third-party SaaS (YC S25) | Open source (7.8k stars) | Self-hosted infrastructure |
| **Execution** | Local machine only | Local + cloud sandbox failover | Cloud VMs | Local machine |
| **Mobile app** | Claude iOS/Android app | Dedicated iOS app (4.3 stars) | Browser-based | Terminal app (Termius, Blink) |
| **Voice input** | No | Yes (two-way voice coding) | No | No |
| **Offline continuation** | No — session pauses until reconnect | Yes — cloud sandbox takes over | Yes — cloud-native | No — session pauses |
| **Push notifications** | No | Yes (agent needs input / task done) | No | No |
| **Security model** | Outbound HTTPS only, TLS, Anthropic API | Outbound WebSocket, no E2E encryption | SSH-based, cloud VMs | Full control (your infra) |
| **Multi-agent support** | One session per instance | Agent orchestration dashboard | Persistent sessions | Multiple tmux panes |
| **Pricing** | Free (included in CC subscription) | $20/mo (10 free sessions/mo) | Open source (cloud hosting costs) | Free (your infra costs) |
| **Setup** | `claude remote-control` | `curl install + omnara` | Docker/cloud setup | tmux + Tailscale/WireGuard |
| **Codex support** | No | Yes (Claude Code + OpenAI Codex) | Yes (Claude Code + Cursor + Codex) | Any terminal tool |
| **Maintenance risk** | Anthropic-maintained | Pivoted once (CLI wrapper → Agent SDK); small team | Community-maintained | Zero external dependency |

<!-- markdownlint-enable MD013 -->

## Detailed Notes

### CC Remote Control (Native)

Already analyzed in [CC-remote-control-analysis.md](CC-remote-control-analysis.md). Built-in, zero-cost, zero-setup. Limitation: no offline continuation — laptop must stay on and connected.

### Omnara

- **YC S25 startup** (San Francisco, 3-person team) ([source][omnara-yc])
- **Pivoted**: Original open-source CLI wrapper (`omnara-ai/omnara`, Apache-2.0) is **archived and unmaintained** as of late 2025. New version built on Claude Agent SDK as a standalone platform ([source][omnara-gh])
- **Key differentiator**: Cloud sandbox failover — if laptop goes offline, session continues in hosted sandbox. Code state preserved via git commits ([source][omnara-techmonk])
- **Architecture**: Headless daemon on local machine → outbound WebSocket → Omnara server → web/mobile clients ([source][omnara-hn])
- **Security concern**: No end-to-end encryption. Conversation state and code diffs transit through Omnara servers ([source][omnara-techmonk])
- **Voice**: Two-way voice coding mode for hands-free interaction ([source][omnara-hiretop])
- **Localhost previews**: Preview dev server on phone without SSH tunnels ([source][omnara-appstore])
- **Pricing**: 10 free sessions/month, $20/month unlimited. Local runs use your own Claude/Codex tokens ([source][omnara-hn])

### CloudCLI

- **Open source** (7.8k GitHub stars), cloud-native dev environments ([source][cloudcli])
- **Multi-tool**: Works with Claude Code, Cursor, Codex, Gemini ([source][cloudcli])
- **Flow**: Start from phone/browser/Linear/Jira → continue in VS Code/Cursor over SSH ([source][cloudcli])
- **Cloud-first**: Sessions run in cloud VMs, not local machine ([source][cloudcli])
- **Less relevant**: Our workflows depend on local MCP servers, state files, and project config

### DIY (tmux + Tailscale/SSH)

- **Maximum control**: tmux session + Tailscale/WireGuard VPN + mobile terminal (Termius, Blink)
- **No external dependencies**: No third-party servers handling code/conversations
- **Overhead**: Manual setup, no push notifications, raw terminal on mobile
- **Already possible**: No new tooling needed if tmux is available

## Relevance to This Project

<!-- markdownlint-disable MD013 -->

| Workflow | Best Option | Rationale |
| -------- | ----------- | --------- |
| Monitor Ralph loop from phone | CC Remote Control | Free, zero-setup, sufficient for steering |
| Long Ralph runs (laptop may sleep) | Omnara or tmux on server | CC RC drops on sleep; need offline continuation |
| CC teams monitoring | CC Remote Control | Multi-surface sync for single session |
| Parallel baseline collection | CC Cloud Sessions (`--remote`) | See [CC-cloud-sessions-analysis.md](CC-cloud-sessions-analysis.md) |
| Security-sensitive work | DIY (tmux + Tailscale) | No third-party servers; full control |

<!-- markdownlint-enable MD013 -->

### Decision Rule

**Start with CC Remote Control (free, native, zero-setup). Only evaluate Omnara if offline continuation becomes a real bottleneck — i.e., Ralph runs regularly stall because the laptop sleeps mid-session.**

### Risk Assessment

| Option | Risk | Mitigation |
| ------ | ---- | ---------- |
| CC Remote Control | Session drops on laptop sleep | Keep laptop on power + prevent sleep during runs |
| Omnara | Startup risk (3-person team, already pivoted once); no E2E encryption | Don't send sensitive code; evaluate stability before adopting |
| CloudCLI | Cloud-first doesn't fit local MCP/state workflow | Only for tasks that don't need local config |
| DIY | Setup overhead, raw terminal UX on mobile | One-time setup; acceptable for power users |

### Actionable Next Steps

1. **Try CC Remote Control** — see [CC-remote-control-analysis.md](CC-remote-control-analysis.md) for setup and decision rationale
2. **Measure**: Does the laptop actually sleep during runs? If not, CC RC is sufficient and no further evaluation needed
3. **If sleep is a problem**: Evaluate Omnara's cloud sandbox failover on a non-sensitive test repo first

## References

- [CC Remote Control docs][cc-rc] — native feature
- [Omnara][omnara] — YC S25, cloud sandbox failover
- [Omnara GitHub (archived)][omnara-gh] — original open-source version
- [CloudCLI][cloudcli] — open-source cloud dev environments
- [CC Cloud Sessions docs][cc-cloud] — Anthropic cloud execution

[cc-rc]: https://code.claude.com/docs/en/remote-control
[omnara]: https://omnara.com
[omnara-yc]: https://www.ycombinator.com/companies/omnara
[omnara-gh]: https://github.com/omnara-ai/omnara
[omnara-hn]: https://news.ycombinator.com/item?id=44878650
[omnara-techmonk]: https://techmonk.economictimes.indiatimes.com/news/ai/omnara-wants-to-put-your-coding-agent-on-your-phone/128286862
[omnara-hiretop]: https://hiretop.com/blog5/omnara-mobile-voice-interface-for-claude-code/
[omnara-appstore]: https://apps.apple.com/us/app/omnara-ai-command-center/id6748426727
[cloudcli]: https://cloudcli.ai
[cc-cloud]: https://code.claude.com/docs/en/claude-code-on-the-web
