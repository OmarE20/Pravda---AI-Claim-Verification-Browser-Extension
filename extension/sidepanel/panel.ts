import type { CheckResponse, Citation, EvidenceChunk, RuntimeMessage, Verdict } from "../types";

const app = document.getElementById("app") as HTMLElement;

function el<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  className?: string,
  text?: string
): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function renderLoading(): void {
  app.replaceChildren();
  const wrap = el("div", "loading");
  wrap.append(el("div", "spinner"), el("span", undefined, "Checking evidence..."));
  app.appendChild(wrap);
}

function renderError(message: string): void {
  app.replaceChildren();
  app.appendChild(el("div", "error-box", `Couldn't reach Pravda backend: ${message}`));
}

function isCited(evidence: EvidenceChunk, citations: Citation[]): boolean {
  return citations.some((c) => c.source_url === evidence.source_url);
}

function renderEvidenceCard(evidence: EvidenceChunk, citations: Citation[]): HTMLElement {
  const card = el("div", `evidence-card${isCited(evidence, citations) ? " cited" : ""}`);

  const head = el("div", "evidence-card-head");
  const link = el("a", "evidence-source", evidence.title || evidence.source_domain);
  link.href = evidence.source_url;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  head.appendChild(link);
  head.appendChild(
    el("span", "reliability-score", `${Math.round(evidence.reliability_score * 100)}%`)
  );
  card.appendChild(head);

  card.appendChild(el("div", "evidence-content", evidence.content.slice(0, 220)));

  const meta = el("div", "evidence-meta");
  meta.appendChild(el("span", "provenance-tag", evidence.provenance));
  meta.appendChild(
    el(
      "span",
      undefined,
      `rep ${evidence.signals.domain_reputation.toFixed(2)} · recency ${evidence.signals.recency.toFixed(
        2
      )} · corrob ${evidence.signals.corroboration.toFixed(2)}`
    )
  );
  card.appendChild(meta);

  return card;
}

function renderVerdictBlock(verdict: Verdict, evidence: EvidenceChunk[]): HTMLElement {
  const block = el("div", "claim-block");
  block.appendChild(el("div", "claim-text", verdict.claim));

  const badge = el("span", `verdict-badge ${verdict.label}`);
  badge.appendChild(document.createTextNode(verdict.label));
  badge.appendChild(el("span", "confidence", ` ${Math.round(verdict.confidence * 100)}% conf.`));
  block.appendChild(badge);

  block.appendChild(el("div", "rationale", verdict.rationale));

  const relatedEvidence = evidence.filter((e) =>
    verdict.citations.some((c) => c.source_url === e.source_url)
  );
  const otherEvidence = evidence.filter(
    (e) => !verdict.citations.some((c) => c.source_url === e.source_url)
  );
  const ordered = [...relatedEvidence, ...otherEvidence].slice(0, 6);

  if (ordered.length > 0) {
    block.appendChild(el("div", "evidence-section-title", "Evidence"));
    for (const evidenceChunk of ordered) {
      block.appendChild(renderEvidenceCard(evidenceChunk, verdict.citations));
    }
  }

  return block;
}

function renderResult(payload: CheckResponse): void {
  app.replaceChildren();

  if (payload.claims.length === 0) {
    app.appendChild(
      el("div", "empty-state", "No claims were found in that highlight.")
    );
    return;
  }

  for (const claim of payload.claims) {
    if (!claim.checkable) {
      const block = el("div", "claim-block");
      block.appendChild(el("div", "claim-text", claim.text));
      block.appendChild(
        el("div", "not-checkable", claim.reason || "This isn't a checkable factual claim.")
      );
      app.appendChild(block);
      continue;
    }
    const verdict = payload.verdicts.find((v) => v.claim === claim.text);
    if (!verdict) continue;
    app.appendChild(renderVerdictBlock(verdict, payload.evidence));
  }

  app.appendChild(el("div", "evidence-meta", `Checked in ${Math.round(payload.latency_ms)} ms`));
}

chrome.runtime.onMessage.addListener((message: RuntimeMessage) => {
  if (message.type === "CHECK_LOADING") {
    renderLoading();
  } else if (message.type === "CHECK_RESULT") {
    renderResult(message.payload);
  } else if (message.type === "CHECK_ERROR") {
    renderError(message.error);
  }
});
