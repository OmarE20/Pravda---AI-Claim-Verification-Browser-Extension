import type { RuntimeMessage } from "./types";

const BUTTON_ID = "pravda-check-button";

function removeButton(): void {
  document.getElementById(BUTTON_ID)?.remove();
}

function showButtonNear(rect: DOMRect, text: string): void {
  removeButton();
  const button = document.createElement("button");
  button.id = BUTTON_ID;
  button.textContent = "Check with Pravda";
  button.style.position = "absolute";
  button.style.zIndex = "2147483647";
  button.style.left = `${window.scrollX + rect.left}px`;
  button.style.top = `${window.scrollY + rect.bottom + 6}px`;
  button.style.padding = "6px 10px";
  button.style.fontSize = "13px";
  button.style.fontFamily = "system-ui, sans-serif";
  button.style.background = "#1e293b";
  button.style.color = "#4ade80";
  button.style.border = "1px solid #334155";
  button.style.borderRadius = "6px";
  button.style.cursor = "pointer";
  button.style.boxShadow = "0 2px 8px rgba(0,0,0,0.25)";

  button.addEventListener("mousedown", (e) => e.preventDefault()); // don't clear selection
  button.addEventListener("click", () => {
    const message: RuntimeMessage = { type: "HIGHLIGHT_SELECTED", text, url: window.location.href };
    chrome.runtime.sendMessage(message);
    removeButton();
  });

  document.body.appendChild(button);
}

document.addEventListener("selectionchange", () => {
  const selection = window.getSelection();
  const text = selection?.toString().trim() ?? "";
  if (!text || text.length < 3) {
    removeButton();
    return;
  }
  const range = selection!.getRangeAt(0);
  const rect = range.getBoundingClientRect();
  if (rect.width === 0 && rect.height === 0) {
    removeButton();
    return;
  }
  showButtonNear(rect, text);
});

document.addEventListener("mousedown", (e) => {
  if ((e.target as HTMLElement)?.id !== BUTTON_ID) {
    removeButton();
  }
});
