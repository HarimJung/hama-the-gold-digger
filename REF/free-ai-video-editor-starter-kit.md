---
id: hama-ref-mrcreates-kit
type: reference
track: invest
status: active
last_review: 2026-11-04
---

# Free AI Video Editor Starter Kit — @mrcreates.ai (받은 그대로)

- 출처: 인스타 @mrcreates.ai 릴스 «Stop paying for AI editing tutorials …» 에 댓글 «editor» → DM 으로 받은 키트.
- 받은 날: 2026-11-04 (하림님이 붙여 넣음). 아래는 손대지 않은 전문.
- 같은 폴더의 스크린샷 3장(IMG_5644~5646)과 화면 녹화 4편이 이 릴스·계정 기록이다.

---

Free AI Video Editor Starter Kit
Oct 25, 2026 · @MR

You can build your own AI video editor with Claude Code and five free tools, and this kit has everything you need. Follow the four steps below, copy the three prompts, and use the GitHub links to find each tool.

## Before you start
Get these ready first, so no step stops you halfway.
- The Claude desktop app, with Claude Code opened inside it. Use the desktop app, not the browser.
- A Claude plan that includes Claude Code. Access may need a paid plan.
- Node.js 22 or newer, which HyperFrames requires.
- Instagram links to 3 to 5 videos whose editing style you like, for Step 3.
- One raw video clip, for Step 4.

## Step 1: Set up your workspace
Create one folder with three subfolders, then open it in Claude Code so Claude can see your files.
1. On your computer, create a folder called AI Video Editor.
2. Inside it, create three subfolders: Raw Footage, References, and Exports.
3. Open the Claude desktop app and start a new Claude Code chat.
4. Choose Local, then select the AI Video Editor folder.

```
AI Video Editor
    Raw Footage
    References
    Exports
```
Raw Footage holds your clips. References holds the videos Claude studies. Exports holds your finished videos.

## Step 2: Install the tools
Paste Prompt 1, and Claude installs and tests all five tools for you. Wait until it tells you it is ready.

### Prompt 1: Install the tools
```
I want you to be my video editor. Install these tools on my computer and test each one:

1. Remotion: github.com/remotion-dev/remotion
2. HyperFrames: github.com/heygen-com/hyperframes
3. FFmpeg: github.com/FFmpeg/FFmpeg
4. Whisper (whisper.cpp): github.com/ggml-org/whisper.cpp
5. yt dlp: github.com/yt-dlp/yt-dlp

When everything works, tell me you are ready.
```

## Step 3: Teach Claude your editing style
Paste Prompt 2 with the links to 3 to 5 videos whose editing you like, and Claude builds a brand sheet from them. Replace the three placeholders with your own Instagram links.

### Prompt 2: Learn your style
```
Learn the editing style from these videos:
[PASTE INSTAGRAM LINK 1]
[PASTE INSTAGRAM LINK 2]
[PASTE INSTAGRAM LINK 3]

1. Download each one into my References folder.
2. Study what they have in common: fonts, colors, caption style, cuts, zooms, pacing, motion graphics, music, and sound.
3. Build me a brand sheet that I can review. Make it inspired by these videos, not a copy of them.

Once I approve it, follow it every time you edit for me.
```
Read the brand sheet before you approve it. The line about being inspired, not a copy, keeps your edits original.

## Step 4: Film and edit
Film your video the way you normally would and drop the raw file into the Raw Footage folder. Then paste Prompt 3 and replace the file name.

### Prompt 3: Edit the Reel
```
Edit my new video into an Instagram Reel:
[FILE NAME] in my Raw Footage folder

1. Remove every pause longer than 0.1 seconds.
2. Follow my approved brand sheet.
3. Add captions, music, and motion graphics.
4. Use anything useful from my References folder.

Show me a storyboard to review first. After I approve it, export the final video to my Exports folder.
```
Claude shows a storyboard first. Approve it, and your finished video lands in the Exports folder.

If something feels off, tell Claude in plain words:
Make the hook bigger.

## GitHub repos
These five tools power the editor, and Prompt 1 installs all of them. All five links were checked on October 25, 2026.

| Tool | What it does here | GitHub |
|---|---|---|
| Remotion | Builds videos from React code, for edits and motion graphics | remotion-dev/remotion |
| HyperFrames | HeyGen's open source framework that turns HTML into MP4 video, built for AI agents | heygen-com/hyperframes |
| FFmpeg | Cuts, converts, and exports video and audio | FFmpeg/FFmpeg |
| Whisper (whisper.cpp) | Turns speech into text so Claude can build captions | ggml-org/whisper.cpp |
| yt dlp | Downloads your reference videos from Instagram and many other sites | yt-dlp/yt-dlp |

The FFmpeg repo on GitHub is a mirror, and the official home is ffmpeg.org. Each tool has its own license, so check the repo before using it for client work.

## Tips for better results
- Choose 3 to 5 reference videos that share the style you want.
- Review the brand sheet and the storyboard before you approve either one.
- Ask for one change at a time, in plain words, like "make the hook bigger."
- Keep your clips in Raw Footage and your finished videos in Exports, so Claude always knows where to look.

Follow along, because next I will show you my own editing style.
