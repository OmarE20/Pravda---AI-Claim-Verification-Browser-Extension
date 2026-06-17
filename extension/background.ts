import type { CheckResponse, RuntimeMessage } from "./types";

const DEFAULT_BACKEND_URL = "http://localhost:8000";

async function getBackendUrl(): Promise<string> {
  const stored = await chrome.storage.sync.get("backendUrl");
  return stored.backendUrl || DEFAULT_BACKEND_URL;
}

chrome.runtime.onMessage.addListener((message: RuntimeMessage, sender) => {
  if (message.type !== "HIGHLIGHT_SELECTED") return;

  const tabId = sender.tab?.id;
  if (tabId !== undefined) {
    chrome.sidePanel.open({ tabId }).catch(() => {});
  }

  void chrome.runtime.sendMessage({ type: "CHECK_LOADING" } satisfies RuntimeMessage).catch(() => {});

  (async () => {
    try {
      const backendUrl = await getBackendUrl();
      const resp = await fetch(`${backendUrl}/check`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: message.text, url: message.url }),
      });
      if (!resp.ok) {
        throw new Error(`Backend returned ${resp.status}`);
      }
      const payload = (await resp.json()) as CheckResponse;
      await chrome.runtime.sendMessage({ type: "CHECK_RESULT", payload } satisfies RuntimeMessage);
    } catch (err) {
      const error = err instanceof Error ? err.message : "Unknown error contacting backend";
      await chrome.runtime.sendMessage({ type: "CHECK_ERROR", error } satisfies RuntimeMessage);
    }
  })();

  return true;
});
