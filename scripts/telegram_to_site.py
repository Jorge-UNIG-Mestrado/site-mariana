#!/usr/bin/env python3
"""Lê mensagens do bot da Mari no Telegram, parseia /receita e
   atualiza receitas.json + faz splice nos dois HTMLs do site."""
import json, os, re, sys, urllib.parse, urllib.request, html

TOKEN = os.environ["TELEGRAM_TOKEN"]
ALLOWED = {8814720795, 5386417208}  # Mari e Jorge
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECEITAS_JSON = os.path.join(ROOT, "receitas.json")
DC_HTML = os.path.join(ROOT, "mariana-source.dc.html")
COMPILED_HTML = os.path.join(ROOT, "index.html")
OFFSET_FILE = os.path.join(ROOT, ".telegram_offset")

def api(method, **params):
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(url, data=data, timeout=20) as r:
        return json.loads(r.read())

def read_offset():
    try:
        return int(open(OFFSET_FILE).read().strip())
    except Exception:
        return 0

def write_offset(n):
    open(OFFSET_FILE, "w").write(str(n))

def parse_receita(text):
    """Converte mensagem /receita ... em dict. Retorna None se inválida."""
    if not text.strip().startswith("/receita"):
        return None
    body = text.split("/receita", 1)[1].strip()
    rec = {"ingredients": [], "steps": []}
    section = None
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            continue
        low = line.lower()
        if low.startswith("nome:"):       rec["name"] = line.split(":",1)[1].strip()
        elif low.startswith("categoria:"):rec["category"] = line.split(":",1)[1].strip().lower()
        elif low.startswith("tempo:"):    rec["time"] = line.split(":",1)[1].strip()
        elif low.startswith("porções:") or low.startswith("porcoes:"):
            rec["servings"] = line.split(":",1)[1].strip()
        elif low.startswith("youtube:"):
            url = line.split(":",1)[1].strip()
            rec["yt"] = url
            m = re.search(r"(?:v=|youtu\.be/)([\w-]{6,})", url)
            rec["youtubeId"] = m.group(1) if m else ""
        elif low.startswith("benefício:") or low.startswith("beneficio:"):
            rec["benefit"] = line.split(":",1)[1].strip()
        elif low.startswith("emoji:"):    rec["emoji"] = line.split(":",1)[1].strip()
        elif low.startswith("ingredientes"): section = "ing"
        elif low.startswith("modo"):          section = "step"
        elif section == "ing" and (line.startswith("-") or line.startswith("•")):
            rec["ingredients"].append(line.lstrip("-•").strip())
        elif section == "step" and re.match(r"^\d+[\.\)]\s", line):
            rec["steps"].append(re.sub(r"^\d+[\.\)]\s*", "", line))
    required = ["name", "category", "time"]
    if not all(rec.get(k) for k in required):
        return None
    rec.setdefault("desc", "")
    rec.setdefault("benefit", "")
    rec.setdefault("bEmoji", "✨")
    rec.setdefault("emoji", "🍽️")
    rec.setdefault("servings", "")
    rec.setdefault("yt", "https://youtube.com")
    rec.setdefault("youtubeId", "")
    rec["views"] = None
    rec["featured"] = False
    return rec

def load_receitas():
    if os.path.exists(RECEITAS_JSON):
        return json.load(open(RECEITAS_JSON))
    return []

def save_receitas(items):
    json.dump(items, open(RECEITAS_JSON, "w"), ensure_ascii=False, indent=2)

def splice_into_html(path, new_items_js, escaped=False):
    """Insere recipes JS antes do fechamento `];` da array RECIPES.
       Marca com sentinela pra ser idempotente — substitui bloco entre marcadores."""
    src = open(path, encoding="utf-8").read()
    nl = "\\n" if escaped else "\n"
    open_marker = f"/* TG-START */{nl}"
    close_marker = f"/* TG-END */{nl}"
    block = f"{open_marker}{new_items_js}{close_marker}"
    pattern = re.compile(
        re.escape(open_marker) + r".*?" + re.escape(close_marker),
        re.DOTALL,
    )
    if pattern.search(src):
        src2 = pattern.sub(block, src)
    else:
        # Primeira injeção: insere antes do fechamento  ];
        close_array = "  ];" if not escaped else "  ];"
        # Procura o fechamento da array RECIPES — última ocorrência de "  ];" depois de "RECIPES"
        idx = src.find("RECIPES")
        end = src.find("  ];", idx)
        if end < 0:
            print(f"[!] não achei fechamento da RECIPES em {path}", file=sys.stderr)
            return False
        src2 = src[:end] + block + src[end:]
    open(path, "w", encoding="utf-8").write(src2)
    return True

def to_js_literal(rec, next_id):
    """Converte recipe dict pra literal JS aceito pela array RECIPES."""
    def js(v):
        if v is None: return "null"
        if isinstance(v, bool): return "true" if v else "false"
        if isinstance(v, (int, float)): return str(v)
        if isinstance(v, list): return "[" + ",".join(js(x) for x in v) + "]"
        return json.dumps(v, ensure_ascii=False)
    fields = ["id","name","category","time","servings","desc","yt","youtubeId",
              "ingredients","steps","benefit","bEmoji","views","featured","emoji"]
    parts = [f"{k}:{js(rec.get(k, next_id if k=='id' else None))}" for k in fields]
    return "    { " + ", ".join(parts) + " },"

def reply(chat_id, text):
    try:
        api("sendMessage", chat_id=chat_id, text=text)
    except Exception as e:
        print(f"[!] reply falhou: {e}", file=sys.stderr)

def main():
    offset = read_offset()
    updates = api("getUpdates", offset=offset, timeout=0).get("result", [])
    if not updates:
        print("nada novo")
        return
    receitas = load_receitas()
    # ID base = max existente +1, contando os 12 originais do HTML
    base_id = max([r.get("id", 0) for r in receitas] + [12])
    added = 0
    last_update = offset
    for u in updates:
        last_update = max(last_update, u["update_id"] + 1)
        m = u.get("message") or {}
        uid = (m.get("from") or {}).get("id")
        chat = m.get("chat", {}).get("id")
        text = m.get("text", "")
        if uid not in ALLOWED:
            continue
        if not text:
            continue
        if text.strip().lower() in ("/start", "ativo?"):
            reply(chat, "Tô vivo 🍳 Manda receita no formato /receita pra publicar no site.")
            continue
        rec = parse_receita(text)
        if not rec:
            if text.strip().startswith("/receita"):
                reply(chat, "⚠️ Receita incompleta. Preciso de Nome, Categoria e Tempo no mínimo.")
            continue
        base_id += 1
        rec["id"] = base_id
        # Dedup por nome+categoria
        if any(r.get("name") == rec["name"] and r.get("category") == rec["category"] for r in receitas):
            reply(chat, f"⚠️ Já existe receita '{rec['name']}' na categoria {rec['category']}. Pulando.")
            continue
        receitas.append(rec)
        added += 1
        reply(chat, f"✅ Publicada: {rec['name']} ({rec['category']}). Vai aparecer no site em segundos.")
    write_offset(last_update)
    if not added:
        print("nada novo válido")
        return
    save_receitas(receitas)
    next_id_start = max([r["id"] for r in receitas]) + 1
    # gera JS dos itens novos pra splice
    items_js = "\n".join(to_js_literal(r, r["id"]) for r in receitas) + "\n"
    # versão escapada pra index.html (JSON-encoded)
    items_js_escaped = (items_js
                       .replace("\\", "\\\\")
                       .replace('"', '\\"')
                       .replace("\n", "\\n"))
    splice_into_html(DC_HTML, items_js, escaped=False)
    splice_into_html(COMPILED_HTML, items_js_escaped, escaped=True)
    print(f"adicionadas {added} receitas")

if __name__ == "__main__":
    main()
