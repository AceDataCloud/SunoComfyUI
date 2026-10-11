# Privacy and network behavior

- `Suno Submit Music` sends the prompt, selected model, instrumental flag, and environment key to `https://api.acedata.cloud/suno/audios`.
- `Suno Generate Lyrics` sends the prompt, selected lyrics model, and environment key to `https://api.acedata.cloud/suno/lyrics`.
- `Suno Retrieve Task` sends the task ID and key to `https://api.acedata.cloud/suno/tasks`.
- `Suno Load Audio` downloads a completed HTTPS media URL from `cdn.acedata.cloud` or `cdn.acedata2.cloud`. It refuses redirects and other hosts.
- The package does not write keys or prompts to local files or add telemetry. ComfyUI's own workflow and execution history may retain non-secret inputs such as prompts and task IDs.
- Generated media and API usage follow your Ace Data Cloud account settings and current service terms.
