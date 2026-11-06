-- Pandoc Lua filter for the PDF/LaTeX build of the manual. Three jobs:
--
-- 1. A fenced ```mermaid block is replaced by the Graphviz twin of the
--    same diagram, pre-rendered to PDF under diagrams/. The block declares
--    its twin and its caption in its first lines, as Mermaid comments, so
--    that a Markdown viewer that renders Mermaid natively still draws the
--    block unchanged:
--
--      ```mermaid
--      %% name: method-scheme
--      %% caption: The compile loop of the method.
--      flowchart LR
--      ...
--      ```
--
--    A block without a name is replaced by a short notice, never silently
--    dropped. The image path is relative to the Markdown file pandoc reads.
--
-- 2. A level-1 heading with the class `part` becomes \part{...} in LaTeX
--    (a leading "Part N — " of the title is dropped, since \part numbers
--    itself); other writers keep the heading.
--
-- 3. Inline code gets a break opportunity after '/', '.', '-', '_' and ':'
--    in LaTeX, so that a long path or option in a table cell wraps instead
--    of overflowing the margin.

local function first_lines(text)
  local name, caption
  for line in text:gmatch("[^\n]+") do
    local n = line:match("^%%%%%s*name:%s*(%S+)%s*$")
    local c = line:match("^%%%%%s*caption:%s*(.-)%s*$")
    if n then name = n end
    if c then caption = c end
    if not line:match("^%%%%") then break end
  end
  return name, caption
end

function CodeBlock(el)
  if not el.classes:includes("mermaid") then
    return nil
  end
  local name, caption = first_lines(el.text)
  if not name then
    return pandoc.Para({pandoc.Emph({pandoc.Str("[Mermaid diagram without a Graphviz twin; see the Markdown source]")})})
  end
  local src = "diagrams/" .. name .. ".pdf"
  local inlines = caption and pandoc.read(caption, "markdown").blocks[1].content or {pandoc.Str(name)}
  -- No width attribute: pandoc's template caps the natural size of the
  -- render at the line width and the text height, keeping the aspect ratio.
  local img = pandoc.Image(inlines, src, "")
  -- A Figure element, not a paragraph: the reader's implicit-figure rule
  -- ran before this filter, so the figure has to be built here explicitly.
  return pandoc.Figure({pandoc.Plain({img})}, pandoc.Caption({pandoc.Plain(inlines)}),
                       pandoc.Attr("fig-" .. name, {}, {}))
end

local function is_latex()
  return FORMAT:match("latex") ~= nil
end

function Header(el)
  if el.level == 1 and el.classes:includes("part") and is_latex() then
    local title = pandoc.utils.stringify(el.content)
    title = title:gsub("^Part%s+[IVXLC]+%s+[—–-]+%s+", "")
    return pandoc.RawBlock("latex", "\\part{" .. title .. "}")
  end
  return nil
end

local LATEX_ESCAPES = {
  ["\\"] = "\\textbackslash{}", ["{"] = "\\{", ["}"] = "\\}", ["$"] = "\\$",
  ["&"] = "\\&", ["#"] = "\\#", ["^"] = "\\textasciicircum{}", ["_"] = "\\_",
  ["%"] = "\\%", ["~"] = "\\textasciitilde{}",
}

local function escape_latex(s)
  return (s:gsub("[\\{}$&#^_%%~]", LATEX_ESCAPES))
end

function Code(el)
  if not is_latex() then
    return nil
  end
  local out = {}
  for ch in el.text:gmatch(".") do
    out[#out + 1] = escape_latex(ch)
    if ch == "/" or ch == "." or ch == "-" or ch == "_" or ch == ":" then
      out[#out + 1] = "\\allowbreak{}"
    end
  end
  return pandoc.RawInline("latex", "\\texttt{" .. table.concat(out) .. "}")
end
