-- Pandoc Lua filter for the EPUB edition (tools/epub/build_epub.py).
--
-- build_epub.py writes every teaching box as an environment that pandoc reads as a Div with
-- the environment's name as class, and marks the box title (and inline labels such as 解) with
-- \textsc{...}.  This filter
--   * turns those SmallCaps into <span class="label">,
--   * makes a paragraph that holds only a label into the box title <div class="box-title">,
--   * moves an anchor written as an empty Div at the start of a box onto the box itself,
--   * builds numbered equations as <div class="equation"> with <span class="eqno">,
--   * replaces \textcolor{name} styles by classes c-name (colours are in epub.css).

local BOXES = {
  chapterguide = true, guideq = true, guidegoals = true, guideprereq = true,
  intuition = true, pitfall = true, deeper = true, case = true, example = true,
  compare = true, takeaways = true, selfcheck = true, answers = true,
  stub = true, datasource = true, partintro = true, bibliography = true,
}

function SmallCaps(el)
  return pandoc.Span(el.content, { class = "label" })
end

function Span(el)
  -- a \label outside a heading becomes <span id=".." label="..">; "label" is not valid XHTML
  el.attributes.label = nil
  local style = el.attributes.style
  if style then
    local name = style:match("^color:%s*([%w]+)")
    if name then
      el.attributes.style = nil
      el.classes:insert("c-" .. name)
    end
  end
  return el
end

local function only_label(block)
  if block.t ~= "Para" and block.t ~= "Plain" then return nil end
  local found = nil
  for _, x in ipairs(block.content) do
    if x.t == "Span" and x.classes:includes("label") and not found then
      found = x
    elseif x.t ~= "Space" and x.t ~= "SoftBreak" then
      return nil
    end
  end
  return found
end

local function take_anchor(el)
  local first = el.content[1]
  if first and first.t == "Div" and #first.content == 0 and first.identifier ~= "" then
    if el.identifier == "" then el.identifier = first.identifier end
    el.content:remove(1)
  end
end

local function equation(el, key)
  take_anchor(el)
  local number, math = nil, {}
  for _, b in ipairs(el.content) do
    local lab = only_label(b)
    if lab then
      number = pandoc.utils.stringify(lab)
    elseif b.t == "Para" or b.t == "Plain" then
      for _, x in ipairs(b.content) do
        if x.t == "Math" then table.insert(math, x) end
      end
    end
  end
  local inl = {}
  if number then table.insert(inl, pandoc.Span({ pandoc.Str(number) }, { class = "eqno" })) end
  for _, m in ipairs(math) do table.insert(inl, m) end
  local classes = { "equation" }
  if key then table.insert(classes, "keyeq") end
  return pandoc.Div({ pandoc.Para(inl) }, { id = el.identifier, class = table.concat(classes, " ") })
end

function Div(el)
  if el.classes:includes("epubequation") then return equation(el, false) end
  if el.classes:includes("epubkeyeq") then return equation(el, true) end
  local kind = el.classes[1]
  if not BOXES[kind] then return nil end
  take_anchor(el)
  local first = el.content[1]
  local lab = first and only_label(first)
  if lab then
    el.content[1] = pandoc.Div({ pandoc.Plain(lab.content) }, { class = "box-title" })
  end
  el.classes:insert(1, "box")
  return el
end
