"""Searchable, scrollable multi-select (prompt_toolkit). `visible` is pure; `pick` is the UI."""


def visible(rows, query):
    """rows: dicts with id, label, group. Keep rows whose id/label/group contain every query word."""
    words = query.lower().split()
    return [r for r in rows
            if all(w in f"{r['id']} {r['label']} {r['group']}".lower() for w in words)]


def pick(rows, selected, message):
    """Return the set of selected ids, or None if cancelled. rows with 'disabled' are shown but not selectable."""
    from prompt_toolkit import Application
    from prompt_toolkit.buffer import Buffer
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout import BufferControl, FormattedTextControl, HSplit, Layout, Window
    from prompt_toolkit.layout.dimension import Dimension

    sel = set(selected)
    state = {"cur": 0}
    query = Buffer()

    def rows_now():
        return visible(rows, query.text)

    def selectable():
        return [r for r in rows_now() if not r.get("disabled")]

    def render():
        out, last, cur_line = [], None, 0
        sel_ids = [r["id"] for r in selectable()]
        state["cur"] = min(state["cur"], max(len(sel_ids) - 1, 0))
        cur_id = sel_ids[state["cur"]] if sel_ids else None
        for r in rows_now():
            if r["group"] != last:
                last = r["group"]
                out.append(("bold", f"── {last} ──\n"))
            if r.get("disabled"):
                out.append(("fg:ansibrightblack", f"    [-] {r['label']}  (n/a: {r['disabled']})\n"))
                continue
            if r["id"] == cur_id:
                cur_line = len(out)
            mark = "x" if r["id"] in sel else " "
            out.append(("reverse" if r["id"] == cur_id else "", f"  > [{mark}] {r['label']}\n"
                        if r["id"] == cur_id else f"    [{mark}] {r['label']}\n"))
        if not out:
            out.append(("", "  (no match)\n"))
        state["line"] = cur_line
        return out

    def cursor_pos():
        from prompt_toolkit.data_structures import Point
        return Point(0, state.get("line", 0))

    def status():
        return f" {len(sel)} selected | type to filter | space toggle | ^A all shown | ^G group | enter done | esc cancel"

    kb = KeyBindings()

    def move(d):
        n = len(selectable())
        if n:
            state["cur"] = max(0, min(n - 1, state["cur"] + d))

    for keys, d in (("up", -1), ("c-p", -1), ("down", 1), ("c-n", 1), ("pageup", -10), ("pagedown", 10)):
        kb.add(keys)(lambda e, d=d: move(d))
    kb.add("home")(lambda e: state.update(cur=0))
    kb.add("end")(lambda e: state.update(cur=max(len(selectable()) - 1, 0)))

    @kb.add("space", eager=True)
    def _(e):
        s = selectable()
        if s:
            sel.symmetric_difference_update({s[state["cur"]]["id"]})

    def toggle(ids):
        ids = set(ids)
        if ids <= sel:
            sel.difference_update(ids)
        else:
            sel.update(ids)

    kb.add("c-a")(lambda e: toggle(r["id"] for r in selectable()))

    @kb.add("c-g")
    def _(e):
        s = selectable()
        if s:
            g = s[state["cur"]]["group"]
            toggle(r["id"] for r in s if r["group"] == g)

    kb.add("enter")(lambda e: e.app.exit(result=True))
    kb.add("escape", eager=True)(lambda e: e.app.exit(result=False))
    kb.add("c-c")(lambda e: e.app.exit(result=False))

    body = Window(FormattedTextControl(render, get_cursor_position=cursor_pos, show_cursor=False),
                  height=Dimension(min=5), always_hide_cursor=True)
    qwin = Window(BufferControl(query), height=1, style="underline")
    layout = Layout(HSplit([
        Window(FormattedTextControl(f" {message}"), height=1, style="bold"),
        qwin,
        body,
        Window(FormattedTextControl(status), height=1, style="reverse"),
    ]), focused_element=qwin)
    app = Application(layout=layout, key_bindings=kb, full_screen=True)
    return sel if app.run() else None
