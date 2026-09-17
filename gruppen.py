# -*- coding: utf-8 -*-
"""Ordnet einen Angebotstext einer Warengruppe zu. Fassung 3 (16.09.2026)."""

# Geprueft wird in dieser Reihenfolge: VORAB, GRUPPEN, NACHTRAG.
# Die erste passende Gruppe gewinnt.
#
# VORAB = Non-Food. Steht vorn, damit z. B. "Kochtopf" nicht als Lebensmittel zaehlt.
#
# ACHTUNG, daran haengt hole.py: Marktguru wird mit den ERSTEN 14 Woertern
# jeder Gruppe in GRUPPEN abgefragt. Neue Woerter deshalb nur HINTEN
# anhaengen. Bei Gruppen mit weniger als 14 Woertern (Tier) kommen neue
# Woerter in NACHTRAG, sonst aendern sich die Abfragen.

VORAB = [
    ("Tier", [
        "romeo", "cachet",
    ]),
    ("Kleidung & Schuhe", [
        "esmara", "lupilu", "hip&hopps", "oyanda", "townland", "puma ", "herren-", "damen-",
        "socken", "pyjama", "jeans", "t-shirt", "hoodie", "sneaker", "pantolette",
        "stiefelette",
        "up2fashion", "l&d unterwäsche", "hausschuhe", "pullover", "steppweste", "regencape",
        "l&d ", "boots", "sweatshirt", "pilotenjacke", "unterwäsche", "langarmshirt", "baby-body", "rucksack", "weekender",
    ]),
    ("Werkzeug & Garten", [
        "parkside", "pattex", "packband", "klebeband", "komposter",
        "workzone", "ferrex", "kabelbinder", "tesamoll",
        "deco craft", "alpina",
    ]),
    ("Haushaltswaren & Technik", [
        "blaumann", "livarno", "silvercrest", "jes collection", "kesper", "keter",
        "spice&soul", "liv&bo", "x4-life", "tristar", "bestron", "cleanmaxx", "grundig",
        "crelando", "bratpfanne", "grillpfanne", "wokpfanne", "kochtopf", "messer-set",
        "folienabroller", "treteimer", "einkaufskorb", "partycontainer", "schwerlastregal",
        "home creation", "ambiano", "live in style", "quigg", "easy home", "puzzle", "bilderbuch", "plüschtier", "kalender",
        "casalux", "novitesse", "toylino", "funko", "paw patrol", "simba plüschfigur", "wissensbücher", "entdeckerbuch", "kreativbuch", "aktivitätsbuch", "baby-spannbett", "baby-kuscheldecke",
        "crofton", "maginon",
    ]),
    ("Pflanzen & Blumen", [
        "calluna", "chrysanthem", "orchidee", "blühpflanze", "bepflanzt", "herbstaster",
        "heidekraut", "sommerheide", "fensterblatt", "punktblume", "gräser", "strauß",
        "farben pro topf", "fairtrade rosen", "sprayrosen",
        "callunen", "alpenveilchen", "sedum",
        "kulturtopf",
    ]),
]

GRUPPEN = [
    ("Obst", [
        "apfel", "aepfel", "äpfel", "birne", "banane", "traube", "weintraube", "erdbeer",
        "himbeer", "heidelbeer", "blaubeer", "brombeer", "johannisbeer", "kirsch", "pflaume",
        "zwetschge", "nektarine", "pfirsich", "aprikose", "melone", "ananas", "mango",
        "orange", "mandarine", "clementine", "zitrone", "limette", "kiwi", "avocado",
        "granatapfel", "feige", "dattel", "obst", "beeren", "papaya", "grapefruit",
        "clementinen", "sharon", "physalis", "rhabarber", "quitte", "mirabelle",
        "passionsfrucht",
    ]),
    ("Gemüse", [
        "tomate", "gurke", "paprika", "zwiebel", "knoblauch", "kartoffel", "moehre", "möhre",
        "karotte", "salat", "kopfsalat", "eisberg", "rucola", "spinat", "brokkoli",
        "blumenkohl", "kohlrabi", "rotkohl", "weisskohl", "weißkohl", "wirsing", "lauch",
        "porree", "sellerie", "zucchini", "aubergine", "kuerbis", "kürbis", "champignon",
        "pilz", "radieschen", "rettich", "rote bete", "spargel", "bohne", "erbse", "mais",
        "ingwer", "gemuese", "gemüse", "petersilie", "schnittlauch", "kraeuter", "kräuter",
        "fenchel", "pastinake", "chicoree", "chicorée", "mangold", "steckrübe", "steckruebe",
        "topinambur", "batate", "schalotte", "lauchzwiebel", "basilikum", "dill", "minze",
        "koriander", "oliven", "sauerkraut", "sprossen", "keimlinge", "bundmoehren",
        "bundmöhren", "rosenkohl", "pak choi",
    ]),
    ("Brot & Backwaren", [
        "brot", "broetchen", "brötchen", "semmel", "baguette", "toast", "croissant", "brezel",
        "kuchen", "torte", "gebaeck", "gebäck", "keks", "waffel", "muffin", "donut", "stollen",
        "knaeckebrot", "knäckebrot", "zwieback", "baecker", "bäcker", "striezel", "stollen",
        "linzer", "lebkuchen", "printen", "spekulatius", "berliner", "pfannkuchen", "kraepfel",
        "kräpfel", "hoernchen", "hörnchen", "bagel", "wrap", "tortilla", "fladen", "ciabatta",
        "focaccia", "streusel", "plunder", "backstube", "poffertjes", "pancakes", "pinsa",
        "vanillestange", "zwirbel",
        "laugenkranz", "pan tostados",
    ]),
    ("Milch & Käse", [
        "milch", "butter", "kaese", "käse", "joghurt", "jogurt", "quark", "sahne", "schmand",
        "creme fraiche", "crème fraîche", "frischkaese", "frischkäse", "mozzarella", "gouda",
        "emmentaler", "camembert", "feta", "margarine", "pudding", "buttermilch", "kefir",
        "mascarpone", "ricotta", "parmesan", "schmelzkaese", "schmelzkäse", "skyr", "ayran",
        "molke", "sauerrahm", "creme fresh", "obatzda", "harzer", "bergkaese", "bergkäse",
        "brie", "gorgonzola", "halloumi", "hirtenkaese", "hirtenkäse", "raclette",
        "scheibletten", "kaeseaufschnitt", "käseaufschnitt", "alpro", "soya drink",
        "hafer drink", "haferdrink", "mandeldrink", "sojadrink", "kondensmilch", "kaffeesahne",
        "creme double", "frische eier ", "kaergarden", "almzeit", "der große bauer", "actimel",
        "activia", "almighurt", "grand dessert", "caffè latte", "yogos", "froop",
        "cremige scheiben", "limburger", "cheddar", "bayerntaler", "extrazarte", "lätta",
        "streichfett", "zaziki", "grütze", "süßspeisen", "dr. oetker high protein", "rubius",
        "kerrygold", "patros",
    ]),
    ("Fleisch & Wurst", [
        "fleisch", "hackfleisch", "hack", "schnitzel", "steak", "braten", "gulasch",
        "kotelett", "haehnchen", "hähnchen", "haenchen", "pute", "rind", "schwein", "lamm",
        "wurst", "salami", "schinken", "speck", "bratwurst", "leberwurst", "mortadella",
        "aufschnitt", "frikadelle", "bulette", "cabanossi", "wiener", "bockwurst", "geflügel",
        "gefluegel", "bratwuerste", "bratwürste", "nackensteak", "rouladen", "filet", "keule",
        "hackbraten", "leberkaese", "leberkäse", "sülze", "suelze", "kasseler", "gyros",
        "döner", "doener", "kebab", "ente", "gans", "kalb", "wild", "kaninchen", "haxen",
        "tafelspitz", "jungbullen", "hamburger", "hühnchen", "fried chicken", "knacker",
        "würstchen", "kabanossi", "kaminwurzen", "cevapcici", "serrano", "prosciutto",
        "weißgelegter",
        "herta",
        "burger xxl",
    ]),
    ("Fisch", [
        "fisch", "lachs", "forelle", "thunfisch", "hering", "matjes", "makrele", "kabeljau",
        "seelachs", "scholle", "garnele", "shrimp", "muschel", "sardine", "surimi",
        "pangasius", "bücklinge", "heilbutt", "anchovis", "meeresfrüchte",
        "sushi",
    ]),
    ("Tiefkühl", [
        "tiefkuehl", "tiefkühl", "tk-", "pizza", "eiscreme", "speiseeis", "pommes", "gefrier",
        "gefroren", "haehnchennuggets", "fischstaebchen", "fischstäbchen", "magnum",
        "langnese", "ice cream", "mövenpick eis", "piccolinis", "pizzeria", "frosta",
        "eis-box", "backfrische",
        "mccain", "häagen-dazs", "ofenfrische",
    ]),
    ("Getränke", [
        "wasser", "saft", "saefte", "säfte", "nektar", "limonade", "cola", "fanta", "sprite",
        "bier", "wein", "sekt", "prosecco", "schnaps", "likoer", "likör", "whisky", "vodka",
        "wodka", "rum", "gin", "kaffee", "espresso", "tee", "kakao", "energy", "getraenk",
        "getränk", "schorle", "aperol", "spritz", "brause", "eistee", "pils", "weizen",
        "helles", "radler", "riesling", "pinot", "merlot", "chardonnay", "cabernet", "rioja",
        "grigio", "rosé", "rose wein", "amaro", "aperitif", "vermouth", "wermut", "punsch",
        "gluehwein", "glühwein", "sirup", "mineralwasser", "spezi", "smoothie",
        "molkegetraenk", "proteindrink", "bionade", "tonic", "ginger ale", "cidre",
        "premium lager", "premium beer", "guinness", "doppelkorn", "champagner", "spumante",
        "cinzano asti", "secco", "frizzante", "cuvée", "sauvignon", "federweißer", "whiskey",
        "liqueur", "ice tea", "sports drink", "hohes c", "valensina", "hella feelgood",
        "matcha", "tassimo",
        "limo",
        "wódka", "osborne",
    ]),
    ("Süßes & Snacks", [
        "schokolade", "schoko", "praline", "bonbon", "gummibaer", "gummibär", "haribo",
        "chips", "flips", "cracker", "erdnuss", "nuss", "mandel", "cashew", "riegel",
        "suessigkeit", "süßigkeit", "popcorn", "salzstange", "milka", "ritter sport",
        "kinder ", "lakritz", "marshmallow", "toffee", "karamell", "nougat", "marzipan",
        "waffeln", "kekse", "biskuit", "brezeln", "nachos", "tortilla chips",
        "studentenfutter", "trockenfruechte", "trockenfrüchte", "walnuss", "haselnuss",
        "pistazie", "macadamia", "paranuss", "kuerbiskerne", "kürbiskerne",
        "sonnenblumenkerne", "nüsse", "balisto", "balconi", "duplo", "pom-bär", "cheez-it",
        "saltletts", "pretzel", "snack mix", "snuggles", "tasty snacks", "wasa tasty", "choco",
        "dominosteine", "prinzen-rolle", "manner", "lindor", "lindt", "maoam", "celebrations",
        "merci", "nimm2", "lachgummi", "schogetten", "snickers", "treets", "wafer",
        "mars mixed", "knusperecken",
        "m&m", "wine gums", "chupa chups", "fruchtgummi", "twix",
    ]),
    ("Vorrat & Konserven", [
        "nudel", "spaghetti", "pasta", "reis", "mehl", "zucker", "salz", "pfeffer", "gewuerz",
        "gewürz", "oel", "öl", "essig", "konserve", "dose", "passierte", "tomatenmark",
        "sauce", "sosse", "soße", "ketchup", "senf", "mayonnaise", "honig", "marmelade",
        "konfiture", "muesli", "müsli", "cornflakes", "haferflocken", "suppe", "bruehe",
        "brühe", "linsen", "kichererbsen", "couscous", "gries", "grieß", "backmischung",
        "hefe", "pesto", "balsamico", "spaetzle", "spätzle", "gnocchi", "tortellini",
        "ravioli", "lasagne", "risotto", "polenta", "bulgur", "quinoa", "kokosmilch",
        "currypaste", "sojasosse", "sojasauce", "wasabi", "sambal", "harissa", "streuwuerze",
        "streuwürze", "bruehwuerfel", "brühwürfel", "backpulver", "vanillezucker",
        "puderzucker", "speisestaerke", "speisestärke", "gelierzucker", "nutella",
        "nuss-nougat", "erdnussbutter", "sirup", "apfelmus", "kompott", "konfitüre",
        "fruchtaufstrich", "cerealien", "eintopf", "fertiggericht", "noodle", "soba",
        "orecchiette", "gnocchetti", "bouillon", "beanz", "hummus", "klöße", "klösse",
        "knödel", "teigtaschen", "bolognese", "burrito", "dürüm", "air-fryer-spray",
        "culinesse", "pfannengericht",
        "chio dip", "superfood", "fruchtmus", "valess",
        "antipasti", "griechische beilage", "paella", "gazpacho", "dip xxl", "frische mahlzeit",
    ]),
    ("Haushalt & Drogerie", [
        "waschmittel", "spuelmittel", "spülmittel", "reiniger", "putz", "muellbeutel",
        "müllbeutel", "toilettenpapier", "kuechenrolle", "küchenrolle", "taschentuch",
        "windel", "shampoo", "duschgel", "zahnpasta", "zahnbuerste", "zahnbürste", "deo",
        "seife", "creme", "rasier", "binden", "tampon", "batterie", "gluehbirne", "glühbirne",
        "alufolie", "frischhaltefolie", "backpapier", "slipeinlagen", "pods", "weichspueler",
        "weichspüler", "entkalker", "wc-", "wc ", "klarspueler", "klarspüler",
        "spuelmaschinen", "spülmaschinen", "handseife", "bodytonic", "haarspray", "haarfarbe",
        "styling", "wattestaebchen", "wattestäbchen", "feuchttuecher", "feuchttücher",
        "gesichtscreme", "handcreme", "sonnenmilch", "mundspuelung", "mundspülung",
        "zahnseide", "rasierklingen", "waschgel", "papiertaschentuecher",
        "papiertaschentücher", "servietten", "kerze", "bref power", "fairy", "febreze",
        "powerball", "küchentücher", "haar-coloration", "hygiene-spüler", "lenor",
        "wäscheparfüm", "dove dusche", "pflegedusche", "pampers", "rohrfrei", "sauberdropz",
        "haarentfernung", "swiffer", "vileda", "vanish", "megaperls", "weißer riese",
        "power force", "schuhpflege",
        "spontex", "garnier",
    ]),
    ("Tier", [
        "hundefutter", "katzenfutter", "tiernahrung", "whiskas", "pedigree", "katzenstreu",
        "vogelfutter",
    ]),
]

NACHTRAG = [
    ("Tier", [
        "hundesnack", "hunde-snack", "hundenahrung", "katzennahrung", "katzennassfutter",
        "katzentrockennahrung", "katzen nassnahrung", "purina", "vitakraft", "perfect fit",
        "romeo",
    ]),
]

def _norm(s):
    """Umlaute vereinheitlichen, damit 'Erdnuesse' und 'Erdnüsse' gleich behandelt werden."""
    s = str(s).lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(a, b)
    return s


_GRUPPEN_NORM = [(name, [_norm(w) for w in woerter]) for name, woerter in VORAB + GRUPPEN + NACHTRAG]


def gruppe_von(*texte):
    t = _norm(" ".join([str(x) for x in texte if x]))
    for name, woerter in _GRUPPEN_NORM:
        for w in woerter:
            if w in t:
                return name
    return "Sonstiges"


ALLE_GRUPPEN = list(dict.fromkeys([g[0] for g in GRUPPEN] + [g[0] for g in VORAB] + ["Sonstiges"]))
