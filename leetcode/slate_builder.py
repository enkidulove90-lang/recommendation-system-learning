"""Markdown -> LeetCode.cn Slate editor JSON converter.

Schema reverse-engineered from the rich-text-editor chunk (cn-frontendx-assets):
  Paragraph / Heading1-6 / BulletedList / OrderedList / ListItem / BlockQuote /
  CodeBlock(activeTabIndex, children=[CodeTab(language, name, children=[{text}])])
Inline marks: {bold, code, italic, strikethrough}.
"""
import re
import json


def _inline_nodes(text):
    """Parse inline markdown (bold / code / italic) into slate text nodes."""
    nodes = []
    # token order matters: inline code first (protects its content)
    pattern = re.compile(r"(`[^`]+`|\*\*[^*]+\*\*|\*[^*\n]+\*)")
    for part in pattern.split(text):
        if not part:
            continue
        if part.startswith("`") and part.endswith("`") and len(part) > 2:
            nodes.append({"text": part[1:-1], "code": True})
        elif part.startswith("**") and part.endswith("**") and len(part) > 4:
            nodes.append({"text": part[2:-2], "bold": True})
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            nodes.append({"text": part[1:-1], "italic": True})
        else:
            nodes.append({"text": part})
    if not nodes:
        nodes = [{"text": ""}]
    return nodes


def _fence_info(line, fence_re):
    m = fence_re.match(line)
    if m:
        lang = (m.group(1) or "plainText").strip().lower()
        # editor expects e.g. "python3" style language keys; unknown ones fall back visually
        return lang
    return None


def markdown_to_slate(md):
    """Convert a markdown string to a slate value (list of block nodes)."""
    fence_re = re.compile(r"^```([A-Za-z0-9_+\-#]*)\s*$")
    heading_re = re.compile(r"^(#{1,6})\s+(.*)$")
    bullets_re = re.compile(r"^\s*[-*]\s+(.*)$")
    ordered_re = re.compile(r"^\s*\d+[.)]\s+(.*)$")
    quote_re = re.compile(r"^\s*>\s?(.*)$")

    blocks = []
    in_code = False
    code_lang = "plainText"
    code_lines = []
    list_items = None      # ("BulletedList"|"OrderedList", [inline children])
    quote_lines = None

    def flush_list():
        nonlocal list_items
        if list_items:
            kind, items = list_items
            blocks.append({
                "type": kind,
                "children": [{"type": "ListItem", "children": ch} for ch in items],
            })
            list_items = None

    def flush_quote():
        nonlocal quote_lines
        if quote_lines:
            children = []
            for i, ln in enumerate(quote_lines):
                if i:
                    children.append({"text": "\n"})
                children.extend(_inline_nodes(ln))
            blocks.append({"type": "BlockQuote", "children": children})
            quote_lines = None

    def flush_all():
        flush_list()
        flush_quote()

    for line in (md or "").replace("\r\n", "\n").split("\n"):
        fence = _fence_info(line, fence_re)
        if in_code:
            if fence is not None:
                blocks.append({
                    "type": "CodeBlock",
                    "activeTabIndex": 0,
                    "children": [{
                        "type": "CodeTab",
                        "language": code_lang,
                        "name": "",
                        "children": [{"text": "\n".join(code_lines)}],
                    }],
                })
                in_code, code_lines = False, []
            else:
                code_lines.append(line)
            continue
        if fence is not None:
            flush_all()
            in_code, code_lang, code_lines = True, fence or "plainText", []
            continue

        m = heading_re.match(line)
        if m:
            flush_all()
            level = min(len(m.group(1)), 6)
            blocks.append({
                "type": f"Heading{level}",
                "children": _inline_nodes(m.group(2)),
            })
            continue

        m = quote_re.match(line)
        if m:
            flush_list()
            if quote_lines is None:
                quote_lines = []
            quote_lines.append(m.group(1))
            continue

        m = bullets_re.match(line)
        if m:
            flush_quote()
            if not list_items or list_items[0] != "BulletedList":
                flush_list()
                list_items = ("BulletedList", [])
            list_items[1].append(_inline_nodes(m.group(1)))
            continue

        m = ordered_re.match(line)
        if m:
            flush_quote()
            if not list_items or list_items[0] != "OrderedList":
                flush_list()
                list_items = ("OrderedList", [])
            list_items[1].append(_inline_nodes(m.group(1)))
            continue

        flush_all()
        if line.strip():
            blocks.append({"type": "Paragraph", "children": _inline_nodes(line)})
        # blank line: paragraph break, nothing to emit

    if in_code:  # unterminated fence — flush anyway
        blocks.append({
            "type": "CodeBlock",
            "activeTabIndex": 0,
            "children": [{
                "type": "CodeTab",
                "language": code_lang,
                "name": "",
                "children": [{"text": "\n".join(code_lines)}],
            }],
        })
    flush_all()
    return blocks


def code_tabs_node(tabs, active_index=0):
    """Build a multi-language CodeBlock node.

    tabs: list of (language_key, code_string). The editor renders one selectable
    tab per entry (Python / C++ / Java ...), active_index chooses the default tab.
    """
    children = []
    for lang, code in tabs:
        children.append({
            "type": "CodeTab",
            "language": lang,
            "name": "",
            "children": [{"text": text_wrap_last(code)}],
        })
    return {"type": "CodeBlock", "activeTabIndex": active_index, "children": children}


def text_wrap_last(code):
    return code.rstrip("\n")


def attach_code_tabs(blocks, tabs, active_index=0):
    """Replace the first CodeBlock (the Code section) with a multi-tab one.

    If the editorial has no code block at all, append one at the end.
    Returns the (mutated) blocks list.
    """
    if not tabs:
        return blocks
    for i, b in enumerate(blocks):
        if b.get("type") == "CodeBlock":
            blocks[i] = code_tabs_node(tabs, active_index)
            return blocks
    blocks.append(code_tabs_node(tabs, active_index))
    return blocks


def slate_to_json(md):
    return json.dumps(markdown_to_slate(md), ensure_ascii=False)
