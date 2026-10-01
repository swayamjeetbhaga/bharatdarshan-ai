"use client";

import ReactMarkdown from "react-markdown";
import type { Components } from "react-markdown";

const components: Components = {
  p: ({ ...props }) => <p className="mb-2 last:mb-0" {...props} />,
  ul: ({ ...props }) => <ul className="mb-2 list-disc space-y-1 pl-4 last:mb-0" {...props} />,
  ol: ({ ...props }) => <ol className="mb-2 list-decimal space-y-1 pl-4 last:mb-0" {...props} />,
  li: ({ ...props }) => <li {...props} />,
  strong: ({ ...props }) => <strong className="font-semibold text-foreground" {...props} />,
  h1: ({ ...props }) => (
    <h3 className="mb-1 mt-2 font-display font-semibold text-secondary first:mt-0" {...props} />
  ),
  h2: ({ ...props }) => (
    <h3 className="mb-1 mt-2 font-display font-semibold text-secondary first:mt-0" {...props} />
  ),
  h3: ({ ...props }) => (
    <h3 className="mb-1 mt-2 font-display font-semibold text-secondary first:mt-0" {...props} />
  ),
  a: ({ ...props }) => (
    <a className="text-primary underline" target="_blank" rel="noopener noreferrer" {...props} />
  ),
  code: ({ ...props }) => (
    <code className="rounded bg-secondary/10 px-1 py-0.5 text-xs" {...props} />
  ),
};

export default function Markdown({ children }: { children: string }) {
  return <ReactMarkdown components={components}>{children}</ReactMarkdown>;
}
