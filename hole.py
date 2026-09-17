# -*- coding: utf-8 -*-
"""Holt die Wochenangebote und baut daraus die Seite index.html.

Schreibt ausschliesslich in den eigenen Ordner:
  angebote.json  - die gesammelten Angebote
  index.html     - die fertige Seite fuer das iPad
  bericht.txt    - was beim Lauf passiert ist

REWE je Filiale (seit Fassung 9): Der Abrufweg (Angebotsseite des Marktes,
fehlende Angebotskacheln ueber /api/frontend-includes) stammt aus dem Projekt
KorbKlar von lesecuritae fuer Tarnkappe.info,
https://github.com/lesecuritae/KorbKlar (src/supermarkt/sources/rewe.py),
und wurde in der Funktion rewe() nachgebaut. Lizenz des Originals:

BSD 3-Clause License

Copyright (c) 2026 lesecuritae fuer Tarnkappe.info
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import io
import json
import os
import re
import sys
import uuid
from datetime import datetime, timedelta, timezone

ORDNER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ORDNER)
from gruppen import gruppe_von, ALLE_GRUPPEN  # noqa: E402

VERSION = "11"
PLZ = "01279"
ORT = "Dresden"
BERICHT = []

# Nur diese Maerkte kommen in die Seite. Erlaubnisliste, keine Sperrliste:
# was hier nicht steht, faellt weg.
ERLAUBT = [
    "lidl",
    "kaufland",
    "edeka",
    "rewe",
    "penny",
    "netto marken-discount",
    "norma",
    "aldi",
]


def kurzname(markt):
    """Vereinheitlicht die Marktnamen fuer die Anzeige."""
    m = (markt or "").strip()
    n = m.lower()
    if n.startswith("rewe"):
        return "REWE"
    if n.startswith("netto marken"):
        return "Netto"
    if n.startswith("penny"):
        return "PENNY"
    if n.startswith("edeka"):
        return "EDEKA"
    if n.startswith("lidl"):
        return "Lidl"
    if n.startswith("kaufland"):
        return "Kaufland"
    if n.startswith("norma"):
        return "NORMA"
    if n.startswith("aldi"):
        return "ALDI"
    return m


def erlaubt(markt):
    m = (markt or "").lower()
    if "foodservice" in m:          # Gastro-Grosshandel, nicht fuer Privatkunden
        return False
    for e in ERLAUBT:
        if m.startswith(e):
            return True
    return False


def sag(t=""):
    t = str(t)
    BERICHT.append(t)
    try:
        print(t)
    except Exception:
        print(t.encode("ascii", "replace").decode("ascii"))


try:
    from curl_cffi import requests as cr
except Exception as e:
    sag("curl_cffi fehlt: %s" % e)
    cr = None


def hole(url, headers=None, cookies=None, timeout=60):
    return cr.get(url, headers=headers or {}, cookies=cookies or {},
                  impersonate="chrome", timeout=timeout)


def tag(iso):
    """'2026-09-19T21:59:59Z' -> '19.09.2026'"""
    if not iso:
        return ""
    s = str(iso)[:10]
    try:
        d = datetime.strptime(s, "%Y-%m-%d")
        return d.strftime("%d.%m.%Y")
    except Exception:
        return s


def iso_tag(iso):
    return str(iso)[:10] if iso else ""


def zahl(x):
    """'1,99 EUR' oder 1.99 oder {'price':'1,99'} -> 1.99"""
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, dict):
        for k in ("price", "value", "amount", "formatted"):
            if x.get(k) is not None:
                return zahl(x.get(k))
        return None
    m = re.search(r"\d+[.,]\d{1,2}|\d+", str(x))
    if not m:
        return None
    try:
        return float(m.group(0).replace(",", "."))
    except Exception:
        return None


ANGEBOTE = []


def merke(markt, name, zusatz, preis, altpreis, grundpreis, von, bis):
    name = (name or "").strip()
    if not name or not erlaubt(markt):
        return
    if len(name) < 3 or not re.search(r"[A-Za-zÄÖÜäöüß]{3}", name):
        return  # Reste wie "00" oder "-- 50"
    ANGEBOTE.append({
        "markt": kurzname(markt),
        "name": name,
        "zusatz": (zusatz or "").strip(),
        "preis": preis,
        "altpreis": altpreis,
        "grundpreis": (grundpreis or "").strip(),
        "von": iso_tag(von),
        "bis": iso_tag(bis),
        "gruppe": gruppe_von(name, zusatz),
    })


# ------------------------------------------------------------------ LIDL
def lidl():
    sag("--- Lidl ---")
    h = {
        "Accept": "application/json",
        "Accept-Language": "de-DE",
        "User-Agent": "LidlPlus/17.0.5 Android okhttp/4.12.0",
        "X-Client-Version": "17.0.5",
        "X-Client-Platform": "android",
    }
    st = hole("https://stores.lidlplus.com/api/v4/DE", h).json()
    filialen = [s for s in st if s.get("locality") == ORT]
    if not filialen:
        filialen = [s for s in st if str(s.get("postalCode", "")).startswith("01")]
    if not filialen:
        sag("keine Filiale gefunden")
        return
    f = filialen[0]
    sag("Filiale %s, %s" % (f.get("storeKey"), f.get("address")))
    d = hole("https://offers.lidlplus.com/app/api/v4/DE/%s/offers" % f.get("storeKey"), h).json()
    offers = d.get("offers", []) if isinstance(d, dict) else d
    n = 0
    for o in offers:
        pb = o.get("priceBox") or {}
        preis = pb.get("largePartNumeric")
        alt = pb.get("smallPartNumeric")
        if preis is None:
            continue
        titel = o.get("title") or ""
        marke = o.get("brand") or ""
        name = ("%s %s" % (marke, titel)).strip() if marke and marke.lower() not in titel.lower() else titel
        pack = o.get("packaging") or ""
        grund = ""
        m = re.search(r"1 (kg|l|Liter|Stk)[^\n]*", pack)
        if m:
            grund = m.group(0)
        pack = re.sub(r"\s*Normalpreis:.*", "", pack, flags=re.S).strip()
        merke("Lidl", name, pack.replace("\n", " "), preis, alt, grund,
              o.get("startValidityDate"), o.get("endValidityDate"))
        n += 1
    sag("uebernommen: %d" % n)


# ----------------------------------------------------------------- EDEKA
def edeka():
    sag("--- Edeka ---")
    h = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "de-DE,de;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    }
    mk = hole("https://www.edeka.de/api/marketsearch/markets?searchstring=%s&limit=999" % PLZ, h).json().get("markets", [])
    if not mk:
        sag("kein Markt gefunden")
        return
    gesehen = set()
    for m in mk[:3]:
        mid = m.get("id")
        kette = (m.get("distributionChannelName") or "EDEKA").strip()
        sag("Markt %s (%s)" % (m.get("name"), mid))
        try:
            docs = hole("https://www.edeka.de/eh/service/eh/offers?marketId=%s&limit=99999" % mid, h).json().get("docs", [])
        except Exception as e:
            sag("  Fehler: %s" % e)
            continue
        n = 0
        for o in docs:
            titel = o.get("titel") or o.get("title")
            preis = o.get("preis") if o.get("preis") is not None else o.get("price")
            if not titel or preis is None:
                continue
            schl = (kette, titel, preis)
            if schl in gesehen:
                continue
            gesehen.add(schl)
            besch = o.get("beschreibung") or o.get("description") or ""
            besch = re.sub(r"\s+", " ", besch)[:200]
            bis = ""
            t = o.get("zusatztext") or ""
            mm = re.search(r"g.ltig bis \w+, den (\d{2})\.(\d{2})\.(\d{4})", t)
            if mm:
                bis = "%s-%s-%s" % (mm.group(3), mm.group(2), mm.group(1))
            merke(kette, titel, besch, preis, None, "", "", bis)
            n += 1
        sag("  uebernommen: %d" % n)


# ------------------------------------------------------------- MARKTGURU
# Die Marktguru-Schluessel stehen NICHT in dieser Datei, weil sie auch im
# oeffentlichen Repository transwo/einkaufsapp liegt. Bei GitHub kommen sie
# aus den Geheimnissen (Secrets) MARKTGURU_APIKEY und MARKTGURU_CLIENTKEY,
# am PC aus marktguru_schluessel.json in diesem Ordner (wird nie hochgeladen).
def _mg_schluessel():
    api = os.environ.get("MARKTGURU_APIKEY", "").strip()
    client = os.environ.get("MARKTGURU_CLIENTKEY", "").strip()
    if api and client:
        return api, client, "Geheimnis"
    try:
        with io.open(os.path.join(ORDNER, "marktguru_schluessel.json"), encoding="utf-8") as f:
            d = json.load(f)
        return d.get("x-apikey", ""), d.get("x-clientkey", ""), "Datei"
    except Exception:
        return "", "", "fehlt"


_MG_API, _MG_CLIENT, _MG_QUELLE = _mg_schluessel()
MG_HEAD = {
    "x-apikey": _MG_API,
    "x-clientkey": _MG_CLIENT,
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
}


def mg_abfrage(q, limit=1000, offset=0):
    u = ("https://api.marktguru.de/api/v1/offers/search?as=web&q=%s&limit=%d&offset=%d&zipCode=%s"
         % (q, limit, offset, PLZ))
    r = hole(u, MG_HEAD)
    if r.status_code != 200:
        return None, r.status_code
    return r.json(), 200


def marktguru():
    sag("--- Marktguru ---")
    sag("Schluessel: %s" % _MG_QUELLE)
    # Erst pruefen, ob eine Sammelabfrage ohne Suchwort alles liefert.
    d, code = mg_abfrage("", 1000, 0)
    if d is None:
        sag("Sammelabfrage HTTP %s" % code)
        gesamt = 0
    else:
        gesamt = d.get("totalResults") or 0
        sag("Sammelabfrage ohne Suchwort: totalResults=%s, geliefert=%d" % (gesamt, len(d.get("results") or [])))

    treffer = []
    if gesamt and len(d.get("results") or []) > 0:
        treffer = d.get("results")
        offset = len(treffer)
        while offset < min(gesamt, 5000):
            d2, c2 = mg_abfrage("", 1000, offset)
            if not d2 or not d2.get("results"):
                break
            treffer.extend(d2["results"])
            offset += len(d2["results"])
        sag("insgesamt geholt: %d" % len(treffer))
    else:
        # Rueckfall: nach Warengruppen-Stichwoertern suchen
        sag("Sammelabfrage leer - suche stattdessen nach Stichwoertern")
        from gruppen import GRUPPEN
        woerter = []
        for _, ws in GRUPPEN:
            woerter.extend(ws[:14])
        gesehen_id = set()
        for w in woerter:
            try:
                d3, c3 = mg_abfrage(w, 50, 0)
            except Exception:
                continue
            if not d3:
                continue
            for o in (d3.get("results") or []):
                if o.get("id") in gesehen_id:
                    continue
                gesehen_id.add(o.get("id"))
                treffer.append(o)
        sag("ueber Stichwoerter geholt: %d" % len(treffer))

    n = 0
    rewe_weg = 0
    for o in treffer:
        adv = (o.get("advertisers") or [{}])[0]
        markt = adv.get("name") or "?"
        if REWE_DIREKT[0] and markt.lower().startswith("rewe"):
            rewe_weg += 1   # REWE kommt schon direkt vom Markt, siehe rewe()
            continue
        prod = (o.get("product") or {}).get("name") or ""
        marke = (o.get("brand") or {}).get("name") or ""
        if marke.startswith("thisisnobrand"):
            marke = ""
        name = ("%s %s" % (marke, prod)).strip() if marke else prod
        gv = (o.get("validityDates") or [{}])[0]
        rp = o.get("referencePrice")
        merke(markt, name, o.get("description"), o.get("price"), o.get("oldPrice"),
              ("%s" % rp) if rp else "", gv.get("from"), gv.get("to"))
        n += 1
    if REWE_DIREKT[0]:
        sag("REWE-Eintraege weggelassen (kommen direkt vom Markt): %d" % rewe_weg)
    else:
        sag("REWE kommt ueber Marktguru (direkter Abruf lieferte nichts)")
    sag("uebernommen: %d" % n)


# ------------------------------------------------------------------ REWE
# Dietrichs Markt: REWE Center, Enderstr. 59, 01277 Dresden (Marktnummer
# 4031024, gemessen mit rewe_pruefen.py am 17.09.2026). Die Angebotsseite
# enthaelt alle Angebote als Eintraege mit data-offer-nan, aber nur wenige
# fertige Kacheln; der Rest wird je 25 ueber /api/frontend-includes geholt.
# Weg nach KorbKlar (lesecuritae, BSD-3, siehe Kopf dieser Datei).
# Liefert der Abruf nichts, bleibt REWE_DIREKT falsch und REWE kommt wie
# bisher ueber Marktguru.
REWE_MARKT = "4031024"
REWE_SEITE = "https://www.rewe.de/angebote/dresden/4031024/rewe-center-enderstr-59/"
REWE_DIREKT = [False]
REWE_PROSPEKT = [""]  # seit Fassung 11: Blaetterprospekt des Marktes, von rewe() gelesen


def _rewe_woche():
    """Montag und Sonntag der Angebotswoche; sonntags gilt schon die naechste
    (wie bei KorbKlar)."""
    heute = datetime.now().date()
    naechste = heute.weekday() == 6
    montag = heute - timedelta(days=heute.weekday())
    if naechste:
        montag = montag + timedelta(days=7)
    return naechste, montag, montag + timedelta(days=6)


def _rewe_titel(knoten):
    if knoten is None:
        return ""
    for sup in knoten.find_all("sup"):
        sup.decompose()
    return re.sub(r"\s+", " ", knoten.get_text(" ", strip=True).replace("\xad", "")).strip()


def rewe():
    sag("--- REWE ---")
    from bs4 import BeautifulSoup
    naechste, von, bis = _rewe_woche()
    url = REWE_SEITE + ("?week=next" if naechste else "")
    s = cr.Session(impersonate="chrome")
    h = {"Accept": "text/html,application/xhtml+xml,*/*;q=0.8", "Accept-Language": "de-DE,de;q=0.9"}
    r = s.get(url, headers=h, timeout=60)
    sag("Markt %s, %s -> HTTP %s" % (REWE_MARKT, "naechste Woche" if naechste else "diese Woche", r.status_code))
    if r.status_code != 200:
        return
    soup = BeautifulSoup(r.text, "html.parser")
    # Seit Fassung 11: Der Knopf "Angebote als Prospekt" der Marktseite oeffnet
    # den Blaetterprospekt dieses Marktes (publitas, mit Woche und Marktnummer).
    pb = soup.select_one("[data-testid='sos-handbill-frame'][data-src], iframe[data-src*='publitas']") \
        or soup.find(attrs={"data-src": re.compile("publitas")})
    if pb and pb.get("data-src", "").startswith("https://"):
        REWE_PROSPEKT[0] = pb.get("data-src")
        sag("Prospekt des Marktes: %s" % REWE_PROSPEKT[0])
    else:
        sag("Prospekt des Marktes: nicht auf der Seite gefunden")
    woche = "next" if naechste else "current"
    wurzel = soup.select_one("#sos-categories-%s, .sos-categories-%s, [data-categories-week-value='%s']"
                             % (woche, woche, woche)) or soup
    eintraege = {}
    for hl in wurzel.select("[data-offer-nan]"):
        nan = hl.get("data-offer-nan")
        if not nan or nan in eintraege:
            continue
        eintraege[nan] = {"ww": hl.get("data-offer-wwident") or REWE_MARKT,
                          "kachel": hl.select_one(".cor-offer-renderer-tile")}
    fehlend = [n for n, v in eintraege.items() if v["kachel"] is None]
    sag("Angebote auf der Seite: %d, nachzuladen: %d" % (len(eintraege), len(fehlend)))
    kopf = {"Accept": "application/json", "Content-Type": "application/json",
            "Rd-Client-Href": url, "Origin": "https://www.rewe.de", "Referer": url}
    fehler = 0
    for start in range(0, len(fehlend), 25):
        stueck = fehlend[start:start + 25]
        ids, last = {}, []
        for n in stueck:
            rid = str(uuid.uuid4())
            ids[rid] = n
            last.append({"id": rid, "namespace": "cor", "name": "offer-tile-by-nan",
                         "params": {"nan": n},
                         "query": {"wwIdent": eintraege[n]["ww"], "showDuration": "auto",
                                   "showFootnotes": "", "enableDetailDeeplink": "true",
                                   "enablePerformanceMark": "", "heroStyles": "false"}})
        try:
            r2 = s.post("https://www.rewe.de/api/frontend-includes", headers=kopf, json=last, timeout=60)
            if r2.status_code != 200:
                fehler += 1
                continue
            for item in r2.json():
                n = ids.get(item.get("id"))
                c = item.get("content")
                if n and isinstance(c, str) and c.strip():
                    cs = BeautifulSoup(c, "html.parser")
                    eintraege[n]["kachel"] = cs.select_one(".cor-offer-renderer-tile") or cs
        except Exception:
            fehler += 1
    if fehler:
        sag("Nachladen fehlgeschlagen in %d von %d Abrufen" % (fehler, (len(fehlend) + 24) // 25))
    k = 0
    ohne_preis = 0
    for n, v in eintraege.items():
        kachel = v["kachel"]
        if kachel is None:
            continue
        name = _rewe_titel(kachel.select_one(".cor-offer-information__title"))
        pk = kachel.select_one(".cor-offer-price__tag-price")
        pm = re.search(r"(\d{1,4}(?:[.,]\d{1,2})?)\s*€", pk.get_text(" ", strip=True)) if pk else None
        if not name or not pm:
            ohne_preis += 1
            continue
        teile = [re.sub(r"\s+", " ", x.get_text(" ", strip=True))
                 for x in kachel.select(".cor-offer-information__additional")]
        zusatz = " ".join(x for x in teile if x).replace("\xad", "")
        zusatz = re.sub(r"\s+,", ",", zusatz).strip(" ,")
        gm = re.search(r"\((1\s*(?:kg|l|Liter|Stück|Stk\.?|WL|m)\s*=\s*[\d.,]+\s*€)\)", zusatz)
        grund = gm.group(1) if gm else ""
        merke("REWE", name, zusatz, zahl(pm.group(1)), None, grund, von.isoformat(), bis.isoformat())
        k += 1
    sag("uebernommen: %d, ohne Name oder Preis: %d" % (k, ohne_preis))
    if k > 0:
        REWE_DIREKT[0] = True


# -------------------------------------------------------------- KAUFLAND
def kaufland():
    sag("--- Kaufland ---")
    h = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    }
    liste = hole("https://filiale.kaufland.de/.klstorefinder.json", h).json()
    if isinstance(liste, dict):
        liste = liste.get("stores") or liste.get("items") or []
    treffer = [s for s in liste if str(s.get("t", "")).startswith(ORT) or str(s.get("pc", "")).startswith("01")]
    if not treffer:
        sag("keine Filiale gefunden")
        return
    f = treffer[0]
    code = f.get("n")
    sag("Filiale %s %s" % (code, f.get("cn")))
    r = hole("https://filiale.kaufland.de/angebote/uebersicht.html", h, {"x-aem-variant": str(code)})
    txt = r.text
    marker = "window.SSR['"
    p = txt.find(marker)
    n = 0
    while p >= 0 and n == 0:
        start = txt.find("{", p)
        if start < 0:
            break
        tiefe = 0
        i = start
        in_str = False
        esc = False
        while i < len(txt):
            c = txt[i]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
            else:
                if c == '"':
                    in_str = True
                elif c == "{":
                    tiefe += 1
                elif c == "}":
                    tiefe -= 1
                    if tiefe == 0:
                        break
            i += 1
        roh = txt[start:i + 1]
        try:
            obj = json.loads(roh)
        except Exception:
            p = txt.find(marker, p + 1)
            continue
        n += ernte_kaufland(obj)
        p = txt.find(marker, p + 1)
    sag("uebernommen: %d" % n)


def ernte_kaufland(obj):
    """Sucht rekursiv nach Angebotsobjekten."""
    gefunden = [0]

    def lauf(o):
        if isinstance(o, dict):
            if o.get("component") == "OfferTemplate":
                props = (o.get("props") or {})
                od = props.get("offerData") or {}
                for cyc in (od.get("cycles") or []):
                    for cat in (cyc.get("categories") or []):
                        for ang in (cat.get("offers") or []):
                            preis = zahl(ang.get("formattedPrice"))
                            if preis is None:
                                preis = zahl(ang.get("price"))
                            if preis is None:
                                continue
                            # title ist bei Kaufland nur die Marke,
                            # der Artikelname steht in subtitle.
                            marke = (ang.get("title") or ang.get("detailTitle") or "").strip()
                            artikel = (ang.get("subtitle") or "").strip()
                            if artikel and artikel.lower() not in marke.lower():
                                name = (marke + " " + artikel).strip()
                            else:
                                name = marke or artikel
                            merke("Kaufland", name,
                                  (ang.get("detailDescription") or "").strip(),
                                  preis, zahl(ang.get("formattedOldPrice")),
                                  (ang.get("unit") or "").strip(),
                                  ang.get("dateFrom") or cyc.get("dateFrom"),
                                  ang.get("dateTo") or cyc.get("dateTo"))
                            gefunden[0] += 1
            for v in o.values():
                lauf(v)
        elif isinstance(o, list):
            for v in o:
                lauf(v)

    lauf(obj)
    return gefunden[0]


# ------------------------------------------------------------------ ALDI
# ALDI NORD legt die Angebote in die Seite selbst: im Block
# <script id="__NEXT_DATA__"> steht unter props/pageProps/apiData ein Text,
# der wieder JSON ist; darin je Angebot ein Eintrag unter res/algoliaDataMap.
# Die Angebote gelten fuer alle ALDI-NORD-Filialen gleich.
ALDI_SEITEN = [
    ("diese Woche", "https://www.aldi-nord.de/angebote.html"),
    ("naechste Woche", "https://www.aldi-nord.de/angebote-vorschau.html"),
]


def _aldi_eintraege(o, aus):
    """Sucht alle 'algoliaDataMap'-Woerterbuecher, auch in JSON-Texten."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "algoliaDataMap" and isinstance(v, dict):
                for e in v.values():
                    if isinstance(e, dict) and "currentPrice" in e:
                        aus.append(e)
            else:
                _aldi_eintraege(v, aus)
    elif isinstance(o, list):
        for v in o:
            _aldi_eintraege(v, aus)
    elif isinstance(o, str) and "currentPrice" in o:
        try:
            _aldi_eintraege(json.loads(o), aus)
        except Exception:
            pass


def _euro(x):
    return ("%.2f" % x).replace(".", ",") + " €"


def aldi():
    sag("--- ALDI ---")
    h = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.9",
    }
    n = 0
    for was, u in ALDI_SEITEN:
        r = hole(u, h, timeout=60)
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text, re.S)
        if r.status_code != 200 or not m:
            sag("%s: HTTP %s, Datenblock %s" % (was, r.status_code, "gefunden" if m else "FEHLT"))
            continue
        eintraege = []
        _aldi_eintraege(json.loads(m.group(1)), eintraege)
        k = 0
        for e in eintraege:
            if e.get("isAvailable") is False:
                continue
            cp = e.get("currentPrice") or {}
            preis = zahl(cp.get("priceValue"))
            if preis is None:
                continue
            marke = (e.get("brandName") or "").strip()
            titel = (e.get("name") or "").strip()
            name = ("%s %s" % (marke, titel)).strip() if marke and marke.lower() not in titel.lower() else titel
            alt = zahl((cp.get("strikePrice") or {}).get("strikePriceValue"))
            grund = ""
            bp = cp.get("basePrice") or []
            if bp and bp[0].get("basePriceValue") is not None:
                einheit = str(bp[0].get("basePriceScale") or "")
                einheit = {"Liter": "l"}.get(einheit, einheit)
                grund = "1 %s = %s" % (einheit, _euro(float(bp[0]["basePriceValue"])))
            teile = [e.get("salesUnit") or "", e.get("shortDescription") or ""]
            if e.get("isDepositProduct") and e.get("depositValue"):
                teile.append("zzgl. %s Pfand" % _euro(float(e["depositValue"])))
            zusatz = re.sub(r"\s+", " ", ", ".join([t.strip() for t in teile if t and t.strip()]))
            pp = (e.get("promotionPrices") or [{}])[0]
            merke("ALDI", name, zusatz, preis, alt, grund,
                  pp.get("validFromLocalDate"), pp.get("validUntilLocalDate"))
            k += 1
        sag("%s: %d Angebote im Datenblock, uebernommen %d" % (was, len(eintraege), k))
        n += k
    sag("uebernommen: %d" % n)


# -------------------------------------------------------------- PROSPEKTE
# Je Markt mehrere moegliche Adressen. Genommen wird die erste, die
# wirklich antwortet - geraten wird nichts.
# Maerkte, deren Prospekt-Knopf immer geprueft wird - auch wenn der Abruf
# der Angebote einmal nichts liefert. ALDI hat seit Fassung 7 auch Angebote.
NUR_PROSPEKT = ["ALDI"]

PROSPEKT_KANDIDATEN = {
    "ALDI": [
        "https://www.aldi-nord.de/prospekte.html",
    ],
    "Lidl": [
        "https://www.lidl.de/c/online-prospekte/s10005610",
        "https://www.lidl.de/c/prospekte/s10005610",
        "https://www.lidl.de/",
    ],
    "Kaufland": [
        "https://filiale.kaufland.de/angebote/aktuelle-woche.html",
        "https://filiale.kaufland.de/prospekte.html",
        "https://filiale.kaufland.de/angebote/uebersicht.html",
    ],
    "EDEKA": [
        "https://www.edeka.de/eh/services/prospekte.jsp",
        "https://www.edeka.de/angebote/prospekte.jsp",
        "https://www.edeka.de/angebote/",
    ],
    "REWE": [
        "https://www.rewe.de/angebote/handzettel/",
        "https://www.rewe.de/angebote/",
    ],
    "PENNY": [
        "https://www.penny.de/blaettern",
        "https://www.penny.de/angebote",
        "https://www.penny.de/",
    ],
    "Netto": [
        "https://www.netto-online.de/ueber-netto/Online-Prospekte.chtm",
        "https://www.netto-online.de/filial-angebote",
        "https://www.netto-online.de/",
    ],
}


# Seit Fassung 10: Maerkte, deren Seite die Pruefung von GitHub aus sperrt
# (rewe.de antwortet dort mit HTTP 403, am PC mit 200 - gemessen 17.09.2026).
# Antwortet keine Adresse, wird diese fest eingetragen. Nur fuer Adressen,
# die am PC schon einmal geantwortet haben.
FESTER_PROSPEKT = {
    "REWE": "https://www.rewe.de/angebote/",
}


def prospekte(maerkte):
    sag("--- Prospekte ---")
    vorab = {}
    if REWE_PROSPEKT[0]:
        vorab["REWE"] = REWE_PROSPEKT[0]
    h = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    }
    ergebnis = {}
    for m in maerkte:
        if m in vorab:
            ergebnis[m] = vorab[m]
            sag("  %-10s %s  (Prospekt des Marktes)" % (m, vorab[m]))
            continue
        for u in PROSPEKT_KANDIDATEN.get(m, []):
            try:
                r = hole(u, h, timeout=30)
                if r.status_code == 200 and len(r.text) > 2000:
                    ergebnis[m] = u
                    sag("  %-10s %s" % (m, u))
                    break
                sag("  %-10s HTTP %s  %s" % (m, r.status_code, u))
            except Exception as e:
                sag("  %-10s Fehler %s  %s" % (m, str(e)[:60], u))
        if m not in ergebnis and m in FESTER_PROSPEKT:
            ergebnis[m] = FESTER_PROSPEKT[m]
            sag("  %-10s fest eingetragen (Pruefung gesperrt)  %s" % (m, FESTER_PROSPEKT[m]))
        if m not in ergebnis:
            sag("  %-10s keine Adresse gefunden" % m)
    return ergebnis


# ----------------------------------------------------------------- LAUF
def main():
    sag("Skript Fassung %s, Lauf vom %s" % (VERSION, datetime.now().strftime("%d.%m.%Y %H:%M:%S")))
    sag("")
    if cr is None:
        return
    # rewe() vor marktguru(): Marktguru laesst REWE weg, wenn rewe() geliefert hat.
    for fn in (lidl, edeka, rewe, marktguru, kaufland, aldi):
        try:
            fn()
        except Exception as e:
            sag("FEHLER in %s: %s" % (fn.__name__, e))
        sag("")

    # doppelte Eintraege entfernen
    gesehen = set()
    sauber = []
    for a in ANGEBOTE:
        s = (a["markt"], a["name"].lower(), a["preis"])
        if s in gesehen:
            continue
        gesehen.add(s)
        sauber.append(a)

    sauber.sort(key=lambda a: (ALLE_GRUPPEN.index(a["gruppe"]) if a["gruppe"] in ALLE_GRUPPEN else 99,
                               a["name"].lower()))

    maerkte = sorted(set([a["markt"] for a in sauber]))
    try:
        pros = prospekte(sorted(set(maerkte + NUR_PROSPEKT)))
    except Exception as e:
        sag("FEHLER Prospekte: %s" % e)
        pros = {}
    sag("")

    daten = {
        "stand": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "ort": ORT,
        "plz": PLZ,
        "prospekte": pros,
        "angebote": sauber,
    }
    with io.open(os.path.join(ORDNER, "angebote.json"), "w", encoding="utf-8") as f:
        json.dump(daten, f, ensure_ascii=False, indent=1)

    sag("=== Zusammenfassung ===")
    sag("Angebote gesamt: %d" % len(sauber))
    nach_markt = {}
    nach_gruppe = {}
    for a in sauber:
        nach_markt[a["markt"]] = nach_markt.get(a["markt"], 0) + 1
        nach_gruppe[a["gruppe"]] = nach_gruppe.get(a["gruppe"], 0) + 1
    for k in sorted(nach_markt, key=lambda x: -nach_markt[x]):
        sag("  %-28s %d" % (k, nach_markt[k]))
    sag("")
    for k in ALLE_GRUPPEN:
        if nach_gruppe.get(k):
            sag("  %-22s %d" % (k, nach_gruppe[k]))
    ohne = [a for a in sauber if a["gruppe"] == "Sonstiges"][:25]
    if ohne:
        sag("")
        sag("Beispiele ohne Gruppe (zum Nachbessern):")
        for a in ohne:
            sag("   %s | %s" % (a["markt"], a["name"]))

    # Seite bauen
    vorlage = os.path.join(ORDNER, "vorlage.html")
    if os.path.exists(vorlage):
        with io.open(vorlage, "r", encoding="utf-8") as f:
            html = f.read()
        html = html.replace("/*DATEN*/", json.dumps(daten, ensure_ascii=False))
        with io.open(os.path.join(ORDNER, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        sag("")
        sag("index.html geschrieben.")
    else:
        sag("vorlage.html fehlt - index.html nicht gebaut.")


if __name__ == "__main__":
    main()
    with io.open(os.path.join(ORDNER, "bericht.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(BERICHT))
    print("")
    print("Fertig. Bericht: " + os.path.join(ORDNER, "bericht.txt"))
