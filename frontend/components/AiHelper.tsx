"use client";

import { useState, useSyncExternalStore, type FormEvent } from "react";
import Markdown from "@/components/Markdown";
import {
  sendChatMessage,
  extractErrorMessage,
  type ChatMessage,
} from "@/lib/api";
import {
  getAiHelperState,
  getAiHelperServerSnapshot,
  subscribeAiHelper,
  toggleAiHelper,
  closeAiHelper,
  clearPlaceContext,
} from "@/lib/aiHelper";
import { categoryLabel } from "@/lib/attractionCategories";

export default function AiHelper() {
  const { isOpen, placeContext } = useSyncExternalStore(
    subscribeAiHelper,
    getAiHelperState,
    getAiHelperServerSnapshot
  );

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function executeSend(text: string) {
    if (!text || loading) return;

    const history = messages;
    setMessages([...history, { role: "user", content: text }]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const result = await sendChatMessage(
        text,
        history,
        placeContext?.placeName,
        placeContext?.district || undefined,
        placeContext?.placeId
      );
      setMessages((prev) => [...prev, { role: "assistant", content: result.answer }]);
    } catch (err) {
      setError(extractErrorMessage(err, "The AI helper couldn't respond. Try again in a moment."));
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text) return;
    await executeSend(text);
  }

  function handleQuickPrompt(question: string) {
    executeSend(question);
  }

  const quickChips = placeContext
    ? [
        `What do travelers say about ${placeContext.placeName}?`,
        `Is ${placeContext.placeName} worth visiting?`,
        `Best time to visit & travel tips`,
        `Highlights & things to do at ${placeContext.placeName}`,
      ]
    : [
        "Best time to visit India",
        "Top national parks for tiger safari",
        "Golden Triangle travel guide",
        "How to plan an India trip",
      ];

  return (
    <div className="relative">
      <button
        type="button"
        onClick={toggleAiHelper}
        className={`group flex items-center gap-1.5 rounded-full border px-4 py-1.5 text-sm font-medium shadow-sm transition-all ${
          placeContext
            ? "border-primary bg-primary/10 text-primary hover:bg-primary/15 ring-2 ring-primary/20"
            : "border-border bg-card text-card-foreground hover:border-primary hover:text-primary"
        }`}
        title={placeContext ? `Ask AI about ${placeContext.placeName}` : "Ask AI Travel Helper"}
      >
        <span className="text-accent animate-pulse text-xs">✦</span>
        <span>Ask AI</span>
        {placeContext && (
          <span className="max-w-[110px] truncate rounded-full bg-primary/20 px-2 py-0.2 text-[0.7rem] font-semibold text-primary">
            {placeContext.placeName}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 top-full z-[2000] mt-2 flex h-[560px] w-96 max-w-[95vw] flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-2xl animate-in fade-in zoom-in-95 duration-200">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-border bg-gradient-to-br from-hero to-hero/80 px-4 py-3 text-hero-foreground">
            <div className="flex items-center gap-2 min-w-0">
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-xl bg-primary/25 text-accent text-sm font-bold shadow-sm">
                ✦
              </span>
              <div className="min-w-0">
                <p className="font-display text-sm font-semibold leading-tight text-hero-foreground">
                  BharatDarshan AI
                </p>
                {placeContext ? (
                  <p className="text-[0.7rem] text-hero-foreground/80 truncate">
                    Focused on <span className="font-semibold text-accent">{placeContext.placeName}</span>
                  </p>
                ) : (
                  <p className="text-[0.7rem] text-hero-foreground/70">India travel companion</p>
                )}
              </div>
            </div>
            <div className="flex items-center gap-1.5">
              {placeContext && (
                <button
                  type="button"
                  onClick={clearPlaceContext}
                  className="rounded-full bg-hero-foreground/10 px-2 py-0.5 text-[0.65rem] font-medium text-hero-foreground/90 hover:bg-hero-foreground/20 transition-colors"
                  title="Clear place focus"
                >
                  Clear place
                </button>
              )}
              <button
                type="button"
                onClick={closeAiHelper}
                className="flex h-7 w-7 items-center justify-center rounded-full text-hero-foreground/70 hover:bg-hero-foreground/10 hover:text-hero-foreground transition-colors"
                aria-label="Close AI helper"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Chat / Messages Area */}
          <div className="flex-1 space-y-3.5 overflow-y-auto p-4 scroll-smooth">
            {/* Fancy Contextual Card when a place is active */}
            {placeContext && (
              <div className="relative overflow-hidden rounded-2xl border border-primary/25 bg-gradient-to-br from-primary/10 via-card to-accent/5 p-4 shadow-sm backdrop-blur-sm">
                <div className="pointer-events-none absolute -right-6 -top-6 h-20 w-20 rounded-full bg-accent/15 blur-2xl" />
                <div className="pointer-events-none absolute -left-6 -bottom-6 h-20 w-20 rounded-full bg-primary/15 blur-2xl" />

                <div className="relative z-10">
                  <div className="flex items-center justify-between gap-2">
                    <span className="inline-flex items-center gap-1.5 rounded-full border border-primary/30 bg-primary/15 px-2.5 py-0.5 text-[0.68rem] font-bold uppercase tracking-wider text-primary">
                      <span className="text-accent">✦</span> Contextual Guide
                    </span>
                    {placeContext.category && (
                      <span className="text-[0.68rem] font-medium text-muted">
                        {categoryLabel(placeContext.category)}
                      </span>
                    )}
                  </div>

                  <h3 className="mt-2.5 font-display text-base font-bold tracking-tight text-foreground leading-snug">
                    Ask anything about{" "}
                    <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent underline decoration-primary/30 underline-offset-2">
                      {placeContext.placeName}
                    </span>
                  </h3>

                  {(placeContext.area || placeContext.district) && (
                    <p className="mt-1 flex items-center gap-1.5 text-xs text-muted font-medium">
                      <span>📍</span>
                      <span>
                        {[placeContext.area, placeContext.district ? `${placeContext.district} district` : null]
                          .filter(Boolean)
                          .join(" · ")}
                      </span>
                    </p>
                  )}

                  <p className="mt-2 text-xs text-muted leading-relaxed">
                    Tap a suggestion below or type any question to get factual details, history, timings, and local travel advice.
                  </p>

                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {quickChips.map((chip, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => handleQuickPrompt(chip)}
                        disabled={loading}
                        className="rounded-full border border-border bg-background/80 px-2.5 py-1 text-xs font-medium text-card-foreground shadow-xs transition-all hover:border-primary hover:bg-primary/5 hover:text-primary active:scale-95 disabled:opacity-50"
                      >
                        {chip}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* General Empty State (when no place is selected and no messages yet) */}
            {!placeContext && messages.length === 0 && (
              <div className="rounded-2xl border border-border bg-background/50 p-4 text-center">
                <span className="mx-auto flex h-10 w-10 items-center justify-center rounded-2xl bg-primary/10 text-accent text-lg">
                  ✦
                </span>
                <p className="mt-2 font-display text-sm font-semibold text-foreground">
                  India Travel Assistant
                </p>
                <p className="mt-1 text-xs text-muted leading-relaxed">
                  Ask about destinations, local customs, best seasons, itineraries, or select any place on the map to ask specific questions.
                </p>
                <div className="mt-3 flex flex-wrap justify-center gap-1.5">
                  {quickChips.map((chip, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => handleQuickPrompt(chip)}
                      disabled={loading}
                      className="rounded-full border border-border bg-card px-2.5 py-1 text-xs font-medium text-foreground hover:border-primary hover:text-primary transition-colors disabled:opacity-50"
                    >
                      {chip}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Conversation Messages */}
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`max-w-[90%] rounded-2xl px-3.5 py-2 text-sm shadow-xs ${
                  m.role === "user"
                    ? "ml-auto bg-primary text-primary-foreground font-medium"
                    : "bg-secondary/10 text-foreground border border-border/50"
                }`}
              >
                {m.role === "assistant" ? <Markdown>{m.content}</Markdown> : m.content}
              </div>
            ))}

            {loading && (
              <div className="flex items-center gap-2 text-sm text-muted">
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-primary/10 text-accent animate-spin text-xs">
                  ✦
                </span>
                <span>Thinking…</span>
              </div>
            )}
          </div>

          {error && <p className="px-4 pb-2 text-xs text-red-500 font-medium">{error}</p>}

          {/* Chat Input Form */}
          <form onSubmit={handleSubmit} className="flex gap-2 border-t border-border bg-card p-3">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={
                placeContext
                  ? `Ask anything about ${placeContext.placeName}…`
                  : "Ask about your trip to India…"
              }
              className="flex-1 rounded-full border border-border bg-background px-3.5 py-2 text-sm outline-none ring-2 ring-transparent transition-all focus:border-primary focus:ring-primary/20"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow-sm transition-all hover:opacity-90 active:scale-95 disabled:opacity-40"
            >
              Send
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
