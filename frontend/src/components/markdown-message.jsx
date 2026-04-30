import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Highlight, themes } from "prism-react-renderer";
import { Card, CardHeader, CardContent } from "./ui/card";
import { Button } from "./ui/button";

function CodeBlock({ inline, className, children }) {
  // normalize
  const raw = String(children ?? "");
  const code = raw.replace(/^\n+|\n+$/g, ""); // trim leading/trailing newlines
  const langRaw = (className || "").replace("language-", "").trim();
  const lang = langRaw || "text";

  // Heuristics: treat tiny/plain one-liners as inline code, not a card
  const isSingleLine = !code.includes("\n");
  const isPlainLang = ["", "text", "plain", "plaintext"].includes(
    lang.toLowerCase()
  );
  const isTrivial = isSingleLine && code.trim().length <= 40 && isPlainLang;

  if (inline || isTrivial) {
    return (
      <code className="px-1.5 py-0.5 rounded bg-zinc-800/80 text-zinc-100 font-mono text-[0.85em]">
        {code}
      </code>
    );
  }

  return (
    <Card className="my-3 overflow-hidden border-zinc-800 bg-zinc-950 text-zinc-100">
      {/* Hide header if language is generic 'text' */}
      {!isPlainLang && (
        <CardHeader className="flex flex-row items-center justify-between px-3 py-2 border-b border-zinc-800">
          <span className="text-[11px] uppercase tracking-wide text-zinc-400">
            {lang}
          </span>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 px-2 text-zinc-300 hover:bg-zinc-800"
            onClick={(e) => {
              const btn = e.currentTarget;
              const prev = btn.textContent;
              navigator.clipboard
                .writeText(code)
                .then(() => {
                  btn.textContent = "✅ Copied!";
                  setTimeout(() => (btn.textContent = prev), 1200);
                })
                .catch((err) => {
                  console.error("Clipboard copy failed", err);
                });
            }}
            title="Copy to clipboard"
          >
            ⧉ Copy
          </Button>
        </CardHeader>
      )}
      <CardContent className="p-0">
        <Highlight theme={themes.oneDark} code={code} language={lang}>
          {({ className, style, tokens, getLineProps, getTokenProps }) => (
            <pre
              className={`${className} m-0 w-full max-w-2xl overflow-x-auto overflow-y-hidden p-4 text-sm font-mono whitespace-pre`}
              style={style}
            >
              {tokens.map((line, i) => (
                <div key={i} {...getLineProps({ line })}>
                  {line.map((token, key) => (
                    <span key={key} {...getTokenProps({ token })} />
                  ))}
                </div>
              ))}
            </pre>
          )}
        </Highlight>
      </CardContent>
    </Card>
  );
}

export default function MarkdownMessage({ content }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        code: CodeBlock,
        pre: ({ children }) => <>{children}</>,
        a: ({ href, children }) => (
          <a
            href={href}
            target="_blank"
            rel="noreferrer"
            className="underline underline-offset-2 hover:opacity-90"
          >
            {children}
          </a>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
