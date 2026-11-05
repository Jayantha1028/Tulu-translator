/**
 * Historical Tulu Dictionary (Rev. August Männer, Basel Mission Press, 1886)
 */

const HISTORICAL_TULU_CORPUS = [
  {
    "id": 1,
    "tulu_kannada": "ಅಗೆಲ್",
    "tulu_tigalari": "𑎀𑎔𑏁𑎭𑏎",
    "tulu_latin": "agel",
    "english": "An annual domestic ancestral feast / sacrifice of fish or fowl offered to deceased ancestors",
    "part_of_speech": "noun",
    "domain": "Agrarian & Domestic Ritual",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 2,
    "tulu_kannada": "ಅಟಿಲ್",
    "tulu_tigalari": "𑎀𑎜𑎹𑎭𑏎",
    "tulu_latin": "aTil",
    "english": "Hearth / Kitchen / Traditional indoor cooking fireplace",
    "part_of_speech": "noun",
    "domain": "Domestic Life",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 3,
    "tulu_kannada": "ಅಟ್ಟ",
    "tulu_tigalari": "𑎀𑎜𑏐𑎜",
    "tulu_latin": "aTTa",
    "english": "Loft / Attic / Elevated platform under thatched roof for storing dry seeds and grain",
    "part_of_speech": "noun",
    "domain": "Architecture & Tools",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 4,
    "tulu_kannada": "ಅಡಿಪಾಯ",
    "tulu_tigalari": "𑎀𑎞𑎹𑎦𑎸𑎫",
    "tulu_latin": "aDipaaya",
    "english": "Foundation / Substructure stone base of a traditional house",
    "part_of_speech": "noun",
    "domain": "Architecture & Tools",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 5,
    "tulu_kannada": "ಅಡಿಕೆ",
    "tulu_tigalari": "𑎀𑎞𑎹𑎒𑏁",
    "tulu_latin": "aDike",
    "english": "Areca nut / Betel nut crop of coastal plantations",
    "part_of_speech": "noun",
    "domain": "Flora & Agriculture",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 6,
    "tulu_kannada": "ಕಂಡ",
    "tulu_tigalari": "𑎒𑏌𑎞",
    "tulu_latin": "kaMDa",
    "english": "Wet paddy field plot enclosed by low mud dykes",
    "part_of_speech": "noun",
    "domain": "Paddy Cultivation",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 7,
    "tulu_kannada": "ಕಿದೆ",
    "tulu_tigalari": "𑎒𑎹𑎣𑏁",
    "tulu_latin": "kide",
    "english": "Cattle shed / Pen / Fold for cows, calves and working oxen",
    "part_of_speech": "noun",
    "domain": "Animal Husbandry",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 8,
    "tulu_kannada": "ಬೆಣ್ಣಿ",
    "tulu_tigalari": "𑎨𑏁𑎠𑏐𑎠𑎹",
    "tulu_latin": "beNNi",
    "english": "Paddy cultivation / Agriculture in coastal wetlands",
    "part_of_speech": "noun",
    "domain": "Paddy Cultivation",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 9,
    "tulu_kannada": "ಮುಡೆ",
    "tulu_tigalari": "𑎪𑎻𑎞𑏁",
    "tulu_latin": "muDe",
    "english": "Large spherical bundle of unhusked rice packed tightly in rice straw rope",
    "part_of_speech": "noun",
    "domain": "Paddy Cultivation",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 10,
    "tulu_kannada": "ಕಳ",
    "tulu_tigalari": "𑎒𑎳",
    "tulu_latin": "kaLa",
    "english": "Threshing floor / Open earthen ground prepared for threshing grain",
    "part_of_speech": "noun",
    "domain": "Paddy Cultivation",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 11,
    "tulu_kannada": "ನೇಜಿ",
    "tulu_tigalari": "𑎥𑏂𑎙𑎹",
    "tulu_latin": "nEji",
    "english": "Young green paddy seedlings ready for transplanting",
    "part_of_speech": "noun",
    "domain": "Paddy Cultivation",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 12,
    "tulu_kannada": "ಕೊಯ್ಲು",
    "tulu_tigalari": "𑎒𑏆𑎫𑏐𑎭𑎻",
    "tulu_latin": "koylu",
    "english": "Harvesting / Reaping of the ripe golden paddy crop",
    "part_of_speech": "noun",
    "domain": "Paddy Cultivation",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 13,
    "tulu_kannada": "ತೂತು",
    "tulu_tigalari": "𑎡𑎼𑎡𑎻",
    "tulu_latin": "tootu",
    "english": "Sluice gate / Earthen water outlet channeling water between paddy terraces",
    "part_of_speech": "noun",
    "domain": "Paddy Cultivation",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 14,
    "tulu_kannada": "ಬೈಲು",
    "tulu_tigalari": "𑎨𑏅𑎭𑎻",
    "tulu_latin": "bailu",
    "english": "Low-lying fertile valley field suitable for double paddy crops",
    "part_of_speech": "noun",
    "domain": "Paddy Cultivation",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 15,
    "tulu_kannada": "ಪಂಬ",
    "tulu_tigalari": "𑎦𑏌𑎨",
    "tulu_latin": "paMba",
    "english": "Water channel / Narrow irrigation furrow between field ridges",
    "part_of_speech": "noun",
    "domain": "Paddy Cultivation",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 16,
    "tulu_kannada": "ತೋಡು",
    "tulu_tigalari": "𑎡𑏇𑎞𑎻",
    "tulu_latin": "tODu",
    "english": "Natural freshwater brook / Drainage stream flowing to river",
    "part_of_speech": "noun",
    "domain": "Geography & Water",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 17,
    "tulu_kannada": "ಮಾಣಿ",
    "tulu_tigalari": "𑎪𑎸𑎠𑎹",
    "tulu_latin": "maaNi",
    "english": "Youthful apprentice / Boy working on farm or temple",
    "part_of_speech": "noun",
    "domain": "Social & Kinship",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 18,
    "tulu_kannada": "ಗದ್ದೆ",
    "tulu_tigalari": "𑎔𑎣𑏐𑎣𑏁",
    "tulu_latin": "gadde",
    "english": "Wetland plot for paddy cultivation",
    "part_of_speech": "noun",
    "domain": "Paddy Cultivation",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 19,
    "tulu_kannada": "ಬೆಳೆ",
    "tulu_tigalari": "𑎨𑏁𑎳𑏁",
    "tulu_latin": "beLe",
    "english": "Crop / Agricultural yield of harvest",
    "part_of_speech": "noun",
    "domain": "Paddy Cultivation",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 20,
    "tulu_kannada": "ಬೀಜ",
    "tulu_tigalari": "𑎨𑎺𑎙",
    "tulu_latin": "beeja",
    "english": "Selected seed grain preserved for the next sowing season",
    "part_of_speech": "noun",
    "domain": "Paddy Cultivation",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 21,
    "tulu_kannada": "ನೇಗಿಲು",
    "tulu_tigalari": "𑎥𑏂𑎔𑎹𑎭𑎻",
    "tulu_latin": "nEgilu",
    "english": "Traditional wooden plough drawn by a pair of oxen",
    "part_of_speech": "noun",
    "domain": "Architecture & Tools",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 22,
    "tulu_kannada": "ನೊಗ",
    "tulu_tigalari": "𑎥𑏆𑎔",
    "tulu_latin": "noga",
    "english": "Wooden yoke placed on the necks of ploughing bullocks",
    "part_of_speech": "noun",
    "domain": "Architecture & Tools",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 23,
    "tulu_kannada": "ಹಗ್ಗ",
    "tulu_tigalari": "𑎲𑎔𑏐𑎔",
    "tulu_latin": "hagga",
    "english": "Twisted rope made of strong coir or wild plant fiber",
    "part_of_speech": "noun",
    "domain": "Architecture & Tools",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 24,
    "tulu_kannada": "ಮಡು",
    "tulu_tigalari": "𑎪𑎞𑎻",
    "tulu_latin": "maDu",
    "english": "Deep natural pool in a riverbed where water remains during dry summer",
    "part_of_speech": "noun",
    "domain": "Geography & Water",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 25,
    "tulu_kannada": "ತೂಕ",
    "tulu_tigalari": "𑎡𑎼𑎒",
    "tulu_latin": "tooka",
    "english": "Measurement of weight / Counterbalance scale",
    "part_of_speech": "noun",
    "domain": "Architecture & Tools",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 26,
    "tulu_kannada": "ಕಡಲ್",
    "tulu_tigalari": "𑎒𑎞𑎭𑏎",
    "tulu_latin": "kaDal",
    "english": "Ocean / Sea / Vast open waters of Arabian Sea",
    "part_of_speech": "noun",
    "domain": "Marine & Maritime",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 27,
    "tulu_kannada": "ಕಡಲತೀರ",
    "tulu_tigalari": "𑎒𑎞𑎭𑎡𑎺𑎬",
    "tulu_latin": "kaDalateera",
    "english": "Sandy seashore / Coastal surf line",
    "part_of_speech": "noun",
    "domain": "Marine & Maritime",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 28,
    "tulu_kannada": "ಮೀನ್",
    "tulu_tigalari": "𑎪𑎺𑎥𑏎",
    "tulu_latin": "meen",
    "english": "Fish of any species swimming in sea or estuary",
    "part_of_speech": "noun",
    "domain": "Marine & Maritime",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 29,
    "tulu_kannada": "ಬಲೆ",
    "tulu_tigalari": "𑎨𑎭𑏁",
    "tulu_latin": "bale",
    "english": "Fishing net woven of fine thread used by coastal fishermen",
    "part_of_speech": "noun",
    "domain": "Marine & Maritime",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 30,
    "tulu_kannada": "ಓಡಿ",
    "tulu_tigalari": "𑎐𑎞𑎹",
    "tulu_latin": "ODi",
    "english": "Traditional coastal canoe / Dugout fishing boat",
    "part_of_speech": "noun",
    "domain": "Marine & Maritime",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 31,
    "tulu_kannada": "ಪತ್ತಾರ್",
    "tulu_tigalari": "𑎦𑎡𑏐𑎡𑎸𑎬𑏎",
    "tulu_latin": "pattaar",
    "english": "Granary / Large wooden chest for keeping grain secure",
    "part_of_speech": "noun",
    "domain": "Domestic Life",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 32,
    "tulu_kannada": "ಮಲ್ಪೆ",
    "tulu_tigalari": "𑎪𑎭𑏐𑎦𑏁",
    "tulu_latin": "malpe",
    "english": "Natural coastal sea harbour / Haven for sailing craft",
    "part_of_speech": "noun",
    "domain": "Marine & Maritime",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 33,
    "tulu_kannada": "ತೂಗು",
    "tulu_tigalari": "𑎡𑎼𑎔𑎻",
    "tulu_latin": "toogu",
    "english": "Anchor / Heavy stone or iron weight for mooring boats",
    "part_of_speech": "noun",
    "domain": "Marine & Maritime",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 34,
    "tulu_kannada": "ಬಾಯ್ಲು",
    "tulu_tigalari": "𑎨𑎸𑎫𑏐𑎭𑎻",
    "tulu_latin": "baaylu",
    "english": "Shallow estuary flat exposed during low tide",
    "part_of_speech": "noun",
    "domain": "Marine & Maritime",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 35,
    "tulu_kannada": "ಕಲ್ಕ",
    "tulu_tigalari": "𑎒𑎭𑏐𑎒",
    "tulu_latin": "kalka",
    "english": "Rocky underwater reef dangerous to coastal wooden crafts",
    "part_of_speech": "noun",
    "domain": "Marine & Maritime",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 36,
    "tulu_kannada": "ಮಡಂ",
    "tulu_tigalari": "𑎪𑎞𑏌",
    "tulu_latin": "maDaM",
    "english": "Salt-water mangrove creek bordering backwaters",
    "part_of_speech": "noun",
    "domain": "Marine & Maritime",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 37,
    "tulu_kannada": "ಉಪ್ಪು",
    "tulu_tigalari": "𑎄𑎦𑏐𑎦𑎻",
    "tulu_latin": "uppu",
    "english": "Natural sea salt crystallized from sea water in coastal pans",
    "part_of_speech": "noun",
    "domain": "Food & Dining",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 38,
    "tulu_kannada": "ಚಿಪ್ಪು",
    "tulu_tigalari": "𑎗𑎹𑎦𑏐𑎦𑎻",
    "tulu_latin": "chippu",
    "english": "Sea shell / Bivalve mollusc shell gathered on beach",
    "part_of_speech": "noun",
    "domain": "Marine & Maritime",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 39,
    "tulu_kannada": "ಏಡಿ",
    "tulu_tigalari": "𑎋𑎞𑎹",
    "tulu_latin": "EDi",
    "english": "Edible crab found along coastal mangroves and mudflats",
    "part_of_speech": "noun",
    "domain": "Marine & Maritime",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 40,
    "tulu_kannada": "ಸಿಗಡಿ",
    "tulu_tigalari": "𑎱𑎹𑎔𑎞𑎹",
    "tulu_latin": "sigaDi",
    "english": "Marine prawn / Shrimp caught in estuary nets",
    "part_of_speech": "noun",
    "domain": "Marine & Maritime",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 41,
    "tulu_kannada": "ದಂಡೆ",
    "tulu_tigalari": "𑎣𑏌𑎞𑏁",
    "tulu_latin": "daMDe",
    "english": "Riverbank / Sandy margin bordering flowing stream",
    "part_of_speech": "noun",
    "domain": "Geography & Water",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 42,
    "tulu_kannada": "ಸುಳಿ",
    "tulu_tigalari": "𑎱𑎻𑎳𑎹",
    "tulu_latin": "suLi",
    "english": "Whirlpool / Swirling eddy in river or deep estuary",
    "part_of_speech": "noun",
    "domain": "Geography & Water",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 43,
    "tulu_kannada": "ಅಲೆ",
    "tulu_tigalari": "𑎀𑎭𑏁",
    "tulu_latin": "ale",
    "english": "Ocean wave / Rolling breaker surging against sandy shore",
    "part_of_speech": "noun",
    "domain": "Marine & Maritime",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 44,
    "tulu_kannada": "ತೆರೆ",
    "tulu_tigalari": "𑎡𑏁𑎬𑏁",
    "tulu_latin": "tere",
    "english": "Foaming tidal wave crashing against coastal headlands",
    "part_of_speech": "noun",
    "domain": "Marine & Maritime",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 45,
    "tulu_kannada": "ಬುಗ್ಗೆ",
    "tulu_tigalari": "𑎨𑎻𑎔𑏐𑎔𑏁",
    "tulu_latin": "bugge",
    "english": "Freshwater spring bubbling forth from subterranean rock",
    "part_of_speech": "noun",
    "domain": "Geography & Water",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 46,
    "tulu_kannada": "ಇಲ್ಲ",
    "tulu_tigalari": "𑎂𑎭𑏐𑎭",
    "tulu_latin": "illa",
    "english": "House / Homestead / Ancestral dwelling of Tulu family",
    "part_of_speech": "noun",
    "domain": "Domestic Life",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 47,
    "tulu_kannada": "ಬಾಕಿಲ್",
    "tulu_tigalari": "𑎨𑎸𑎒𑎹𑎭𑏎",
    "tulu_latin": "baakil",
    "english": "Doorway / Entrance portal of timber",
    "part_of_speech": "noun",
    "domain": "Architecture & Tools",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 48,
    "tulu_kannada": "ಜನ್ನೆಲ್",
    "tulu_tigalari": "𑎙𑎥𑏐𑎥𑏁𑎭𑏎",
    "tulu_latin": "jannel",
    "english": "Window with wooden vertical bars admitting breeze",
    "part_of_speech": "noun",
    "domain": "Architecture & Tools",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 49,
    "tulu_kannada": "ಚಾವಡಿ",
    "tulu_tigalari": "𑎗𑎸𑎮𑎞𑎹",
    "tulu_latin": "chaavaDi",
    "english": "Open front veranda / Pillared hall for guests and court assemblies",
    "part_of_speech": "noun",
    "domain": "Architecture & Tools",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 50,
    "tulu_kannada": "ಕೊಟ್ಟಗೆ",
    "tulu_tigalari": "𑎒𑏆𑎜𑏐𑎜𑎔𑏁",
    "tulu_latin": "koTTage",
    "english": "Cattle byre / Covered shed attached to homestead",
    "part_of_speech": "noun",
    "domain": "Architecture & Tools",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 51,
    "tulu_kannada": "ಮಣೆ",
    "tulu_tigalari": "𑎪𑎠𑏁",
    "tulu_latin": "maNe",
    "english": "Low wooden plank stool on small legs used when dining or praying",
    "part_of_speech": "noun",
    "domain": "Domestic Life",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 52,
    "tulu_kannada": "ಕತ್ತಿ",
    "tulu_tigalari": "𑎒𑎡𑏐𑎡𑎹",
    "tulu_latin": "katti",
    "english": "Chopping knife / Heavy curved billhook machete of iron",
    "part_of_speech": "noun",
    "domain": "Architecture & Tools",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 53,
    "tulu_kannada": "ಕೈಲ್",
    "tulu_tigalari": "𑎒𑏅𑎭𑏎",
    "tulu_latin": "kail",
    "english": "Long-handled wooden ladle / Coconut shell spoon for serving curry",
    "part_of_speech": "noun",
    "domain": "Domestic Life",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 54,
    "tulu_kannada": "ಕನ್ನಡಿ",
    "tulu_tigalari": "𑎒𑎥𑏐𑎥𑎞𑎹",
    "tulu_latin": "kannaDi",
    "english": "Reflecting looking glass mirror",
    "part_of_speech": "noun",
    "domain": "Domestic Life",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 55,
    "tulu_kannada": "ಬಟ್ಟಲು",
    "tulu_tigalari": "𑎨𑎜𑏐𑎜𑎭𑎻",
    "tulu_latin": "baTTalu",
    "english": "Bronze or bell-metal round dining plate",
    "part_of_speech": "noun",
    "domain": "Domestic Life",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 56,
    "tulu_kannada": "ಕುಪ್ಪಿ",
    "tulu_tigalari": "𑎒𑎻𑎦𑏐𑎦𑎹",
    "tulu_latin": "kuppi",
    "english": "Glass flask / Bottle for keeping coconut oil or medicine",
    "part_of_speech": "noun",
    "domain": "Domestic Life",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 57,
    "tulu_kannada": "ಚೆಂಬು",
    "tulu_tigalari": "𑎗𑏁𑏌𑎨𑎻",
    "tulu_latin": "cheMbu",
    "english": "Round copper or brass vessel for drinking water",
    "part_of_speech": "noun",
    "domain": "Domestic Life",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 58,
    "tulu_kannada": "ಅಗಲ್",
    "tulu_tigalari": "𑎀𑎔𑎭𑏎",
    "tulu_latin": "agal",
    "english": "Wide-mouthed shallow earthen vessel for boiling milk",
    "part_of_speech": "noun",
    "domain": "Domestic Life",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 59,
    "tulu_kannada": "ಕುಂಬಾರ",
    "tulu_tigalari": "𑎒𑎻𑏌𑎨𑎸𑎬",
    "tulu_latin": "kuMbaara",
    "english": "Potter artisan who shapes clay upon revolving wheel",
    "part_of_speech": "noun",
    "domain": "Artisans & Crafts",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 60,
    "tulu_kannada": "ಕಮ್ಮಾರ",
    "tulu_tigalari": "𑎒𑎪𑏐𑎪𑎸𑎬",
    "tulu_latin": "kammaara",
    "english": "Blacksmith who forges iron billhooks, nails and ploughshares",
    "part_of_speech": "noun",
    "domain": "Artisans & Crafts",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 61,
    "tulu_kannada": "ಬಡಗಿ",
    "tulu_tigalari": "𑎨𑎞𑎔𑎹",
    "tulu_latin": "baDagi",
    "english": "Carpenter artisan skilled in hewing house beams and carving doors",
    "part_of_speech": "noun",
    "domain": "Artisans & Crafts",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 62,
    "tulu_kannada": "ಅಕ್ಕಸಾಲಿ",
    "tulu_tigalari": "𑎀𑎒𑏐𑎒𑎱𑎸𑎭𑎹",
    "tulu_latin": "akkasaali",
    "english": "Goldsmith artisan who fashions gold ornaments and sacred amulets",
    "part_of_speech": "noun",
    "domain": "Artisans & Crafts",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 63,
    "tulu_kannada": "ನೇಯ್ಗೆ",
    "tulu_tigalari": "𑎥𑏂𑎫𑏐𑎔𑏁",
    "tulu_latin": "nEyge",
    "english": "Weaving of cotton cloth upon traditional wooden handloom",
    "part_of_speech": "noun",
    "domain": "Artisans & Crafts",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 64,
    "tulu_kannada": "ದೀಪ",
    "tulu_tigalari": "𑎣𑎺𑎦",
    "tulu_latin": "deepa",
    "english": "Earthen or brass lamp fed with oil and cotton wick",
    "part_of_speech": "noun",
    "domain": "Domestic Life",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 65,
    "tulu_kannada": "ಮಂಚ",
    "tulu_tigalari": "𑎪𑏌𑎗",
    "tulu_latin": "maMcha",
    "english": "Four-legged wooden cot strung with coir rope webbing",
    "part_of_speech": "noun",
    "domain": "Domestic Life",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 66,
    "tulu_kannada": "ಪೆಟ್ಟಿಗೆ",
    "tulu_tigalari": "𑎦𑏁𑎜𑏐𑎜𑎹𑎔𑏁",
    "tulu_latin": "peTTige",
    "english": "Wooden chest fitted with lock for storing heirloom jewelry",
    "part_of_speech": "noun",
    "domain": "Domestic Life",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 67,
    "tulu_kannada": "ಸರಪಳಿ",
    "tulu_tigalari": "𑎱𑎬𑎦𑎳𑎹",
    "tulu_latin": "sarapaLi",
    "english": "Forged iron or brass link chain used for swinging cot or temple bells",
    "part_of_speech": "noun",
    "domain": "Domestic Life",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 68,
    "tulu_kannada": "ಬಿಂದಿಗೆ",
    "tulu_tigalari": "𑎨𑎹𑏌𑎣𑎹𑎔𑏁",
    "tulu_latin": "biMdige",
    "english": "Spherical copper or brass water pot carried on hip",
    "part_of_speech": "noun",
    "domain": "Domestic Life",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 69,
    "tulu_kannada": "ಕೊಡ",
    "tulu_tigalari": "𑎒𑏆𑎞",
    "tulu_latin": "koDa",
    "english": "Earthen water vessel fired in potter kiln",
    "part_of_speech": "noun",
    "domain": "Domestic Life",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 70,
    "tulu_kannada": "ಉರಿಲು",
    "tulu_tigalari": "𑎄𑎬𑎹𑎭𑎻",
    "tulu_latin": "urilu",
    "english": "Hanging woven string network suspended from ceiling for food pots",
    "part_of_speech": "noun",
    "domain": "Domestic Life",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 71,
    "tulu_kannada": "ಬರ್ಪುನು",
    "tulu_tigalari": "𑎨𑎬𑏐𑎦𑎻𑎥𑎻",
    "tulu_latin": "barpunu",
    "english": "To come / Arrive / Approach (classical verbal noun in -unu)",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 72,
    "tulu_kannada": "ಪೋಪುನು",
    "tulu_tigalari": "𑎦𑏇𑎦𑎻𑎥𑎻",
    "tulu_latin": "pOpunu",
    "english": "To go / Depart / Proceed onward",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 73,
    "tulu_kannada": "ತಿನ್ಪುನು",
    "tulu_tigalari": "𑎡𑎹𑎥𑏐𑎦𑎻𑎥𑎻",
    "tulu_latin": "tinpunu",
    "english": "To eat solid food / Masticate",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 74,
    "tulu_kannada": "ಪರ್ಪುನು",
    "tulu_tigalari": "𑎦𑎬𑏐𑎦𑎻𑎥𑎻",
    "tulu_latin": "parpunu",
    "english": "To drink liquid / Quench thirst",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 75,
    "tulu_kannada": "ತೂಪುನು",
    "tulu_tigalari": "𑎡𑎼𑎦𑎻𑎥𑎻",
    "tulu_latin": "toopunu",
    "english": "To see / Behold with eyes / Examine",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 76,
    "tulu_kannada": "ಕೇನ್ಪುನು",
    "tulu_tigalari": "𑎒𑏂𑎥𑏐𑎦𑎻𑎥𑎻",
    "tulu_latin": "kEnpunu",
    "english": "To listen / Hear / Inquire of someone",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 77,
    "tulu_kannada": "ಪಾತೆರ್ಪುನು",
    "tulu_tigalari": "𑎦𑎸𑎡𑏁𑎬𑏐𑎦𑎻𑎥𑎻",
    "tulu_latin": "paaterpunu",
    "english": "To converse / Speak words / Articulate speech",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 78,
    "tulu_kannada": "ಕುಳ್ಳುನು",
    "tulu_tigalari": "𑎒𑎻𑎳𑏐𑎳𑎻𑎥𑎻",
    "tulu_latin": "kuLLunu",
    "english": "To sit down / Be seated upon seat",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 79,
    "tulu_kannada": "ಉಂತುನು",
    "tulu_tigalari": "𑎄𑏌𑎡𑎻𑎥𑎻",
    "tulu_latin": "uMtunu",
    "english": "To stand upright / Cease motion / Halt",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 80,
    "tulu_kannada": "ಜೆಪ್ಪುನು",
    "tulu_tigalari": "𑎙𑏁𑎦𑏐𑎦𑎻𑎥𑎻",
    "tulu_latin": "jeppunu",
    "english": "To lie down / Sleep / Rest body",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 81,
    "tulu_kannada": "ಕೊರ್ಪುನು",
    "tulu_tigalari": "𑎒𑏆𑎬𑏐𑎦𑎻𑎥𑎻",
    "tulu_latin": "korpunu",
    "english": "To bestow / Give / Impart to another",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 82,
    "tulu_kannada": "ದೆತೊನುನು",
    "tulu_tigalari": "𑎣𑏁𑎡𑏆𑎥𑎻𑎥𑎻",
    "tulu_latin": "detonunu",
    "english": "To receive / Accept / Take into hand",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 83,
    "tulu_kannada": "ಮಲ್ಪುನು",
    "tulu_tigalari": "𑎪𑎭𑏐𑎦𑎻𑎥𑎻",
    "tulu_latin": "malpunu",
    "english": "To do / Fabricate / Accomplish deed",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 84,
    "tulu_kannada": "ಕಲ್ಪುನು",
    "tulu_tigalari": "𑎒𑎭𑏐𑎦𑎻𑎥𑎻",
    "tulu_latin": "kalpunu",
    "english": "To acquire knowledge / Learn / Study letters",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 85,
    "tulu_kannada": "ಪನ್ಪುನು",
    "tulu_tigalari": "𑎦𑎥𑏐𑎦𑎻𑎥𑎻",
    "tulu_latin": "panpunu",
    "english": "To narrate / Tell / Declare statement",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 86,
    "tulu_kannada": "ಓಡುನು",
    "tulu_tigalari": "𑎐𑎞𑎻𑎥𑎻",
    "tulu_latin": "ODunu",
    "english": "To run swiftly on foot / Hasten",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 87,
    "tulu_kannada": "ನಲಿಪುನು",
    "tulu_tigalari": "𑎥𑎭𑎹𑎦𑎻𑎥𑎻",
    "tulu_latin": "nalipunu",
    "english": "To dance in rhythm / Frolic with joy",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 88,
    "tulu_kannada": "ಪಾಡುನು",
    "tulu_tigalari": "𑎦𑎸𑎞𑎻𑎥𑎻",
    "tulu_latin": "paaDunu",
    "english": "To put / Place inside / Pour liquid",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 89,
    "tulu_kannada": "ಬರೆಪುನು",
    "tulu_tigalari": "𑎨𑎬𑏁𑎦𑎻𑎥𑎻",
    "tulu_latin": "barepunu",
    "english": "To inscribe characters / Write on palm leaf",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 90,
    "tulu_kannada": "ಓದುನು",
    "tulu_tigalari": "𑎐𑎣𑎻𑎥𑎻",
    "tulu_latin": "Odunu",
    "english": "To read aloud / Recite written scripture",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 91,
    "tulu_kannada": "ಕಾಪುನು",
    "tulu_tigalari": "𑎒𑎸𑎦𑎻𑎥𑎻",
    "tulu_latin": "kaapunu",
    "english": "To guard / Wait expectantly / Watch over",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 92,
    "tulu_kannada": "ತೆರಿಯುನು",
    "tulu_tigalari": "𑎡𑏁𑎬𑎹𑎫𑎻𑎥𑎻",
    "tulu_latin": "teriyunu",
    "english": "To understand intellectually / Know fact",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 93,
    "tulu_kannada": "ಗೆಲಿಪುನು",
    "tulu_tigalari": "𑎔𑏁𑎭𑎹𑎦𑎻𑎥𑎻",
    "tulu_latin": "gelipunu",
    "english": "To win victory / Prevail over adversaries",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 94,
    "tulu_kannada": "ನಡಪುನು",
    "tulu_tigalari": "𑎥𑎞𑎦𑎻𑎥𑎻",
    "tulu_latin": "naDapunu",
    "english": "To walk on pathway / Proceed step by step",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 95,
    "tulu_kannada": "ತುಳುಪುನು",
    "tulu_tigalari": "𑎡𑎻𑎳𑎻𑎦𑎻𑎥𑎻",
    "tulu_latin": "tuLupunu",
    "english": "To bathe body / Wash clean in water",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 96,
    "tulu_kannada": "ಬತ್ತುಂಡು",
    "tulu_tigalari": "𑎨𑎡𑏐𑎡𑎻𑏌𑎞𑎻",
    "tulu_latin": "battuMDu",
    "english": "It came / It has arrived (neuter past)",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 97,
    "tulu_kannada": "ಪೋಯಿಂಡು",
    "tulu_tigalari": "𑎦𑏇𑎫𑎹𑏌𑎞𑎻",
    "tulu_latin": "pOyiMDu",
    "english": "It went / It has departed (neuter past)",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 98,
    "tulu_kannada": "ಆಪುಂಡು",
    "tulu_tigalari": "𑎁𑎦𑎻𑏌𑎞𑎻",
    "tulu_latin": "aapuMDu",
    "english": "It happens / It becomes (neuter habitual)",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 99,
    "tulu_kannada": "ಆಯಿಂಡು",
    "tulu_tigalari": "𑎁𑎫𑎹𑏌𑎞𑎻",
    "tulu_latin": "aayiMDu",
    "english": "It happened / It was accomplished (neuter past)",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 100,
    "tulu_kannada": "ಕೊರ್ಪಾವೆ",
    "tulu_tigalari": "𑎒𑏆𑎬𑏐𑎦𑎸𑎮𑏁",
    "tulu_latin": "korpaave",
    "english": "I cause to give / Have delivered (causative verb stem)",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 101,
    "tulu_kannada": "ಕಲ್ಪಾವೆ",
    "tulu_tigalari": "𑎒𑎭𑏐𑎦𑎸𑎮𑏁",
    "tulu_latin": "kalpaave",
    "english": "I teach / Cause another to learn (causative verb stem)",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 102,
    "tulu_kannada": "ಮಲ್ಪಾವೆ",
    "tulu_tigalari": "𑎪𑎭𑏐𑎦𑎸𑎮𑏁",
    "tulu_latin": "malpaave",
    "english": "I cause to be made / Commission work (causative verb stem)",
    "part_of_speech": "verb",
    "domain": "Classical Tulu Verbs",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 103,
    "tulu_kannada": "ಅಪ್ಪೆ",
    "tulu_tigalari": "𑎀𑎦𑏐𑎦𑏁",
    "tulu_latin": "appe",
    "english": "Mother / Maternal source of life and love",
    "part_of_speech": "noun",
    "domain": "Social & Kinship",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 104,
    "tulu_kannada": "ಅಮ್ಮೆರ್",
    "tulu_tigalari": "𑎀𑎪𑏐𑎪𑏁𑎬𑏎",
    "tulu_latin": "ammer",
    "english": "Father / Head of traditional patriarchal family",
    "part_of_speech": "noun",
    "domain": "Social & Kinship",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 105,
    "tulu_kannada": "ಅಣ್ಣೆ",
    "tulu_tigalari": "𑎀𑎠𑏐𑎠𑏁",
    "tulu_latin": "aNNe",
    "english": "Elder brother held in familial reverence",
    "part_of_speech": "noun",
    "domain": "Social & Kinship",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 106,
    "tulu_kannada": "ಮೆಗ್ಯೆ",
    "tulu_tigalari": "𑎪𑏁𑎔𑏐𑎫𑏁",
    "tulu_latin": "megye",
    "english": "Younger brother protected by family",
    "part_of_speech": "noun",
    "domain": "Social & Kinship",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 107,
    "tulu_kannada": "ಅಕ್ಕ",
    "tulu_tigalari": "𑎀𑎒𑏐𑎒",
    "tulu_latin": "akka",
    "english": "Elder sister revered in family",
    "part_of_speech": "noun",
    "domain": "Social & Kinship",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 108,
    "tulu_kannada": "ಮೆಗ್ದಿ",
    "tulu_tigalari": "𑎪𑏁𑎔𑏐𑎣𑎹",
    "tulu_latin": "megdi",
    "english": "Younger sister cherished in family",
    "part_of_speech": "noun",
    "domain": "Social & Kinship",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 109,
    "tulu_kannada": "ಬಾಲೆ",
    "tulu_tigalari": "𑎨𑎸𑎭𑏁",
    "tulu_latin": "baale",
    "english": "Infant child / Little boy or girl",
    "part_of_speech": "noun",
    "domain": "Social & Kinship",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 110,
    "tulu_kannada": "ಕಂಡನಿ",
    "tulu_tigalari": "𑎒𑏌𑎞𑎥𑎹",
    "tulu_latin": "kaMDani",
    "english": "Husband / Wedded protector of wife",
    "part_of_speech": "noun",
    "domain": "Social & Kinship",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 111,
    "tulu_kannada": "ಬೊಡೆದಿ",
    "tulu_tigalari": "𑎨𑏆𑎞𑏁𑎣𑎹",
    "tulu_latin": "boDedi",
    "english": "Wife / Wedded partner of homestead",
    "part_of_speech": "noun",
    "domain": "Social & Kinship",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 112,
    "tulu_kannada": "ಮಾಮಿ",
    "tulu_tigalari": "𑎪𑎸𑎪𑎹",
    "tulu_latin": "maami",
    "english": "Maternal uncle’s wife / Mother-in-law",
    "part_of_speech": "noun",
    "domain": "Social & Kinship",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 113,
    "tulu_kannada": "ಮಾಮೆ",
    "tulu_tigalari": "𑎪𑎸𑎪𑏁",
    "tulu_latin": "maame",
    "english": "Maternal uncle / Father-in-law (central in Aliya Santana matrilineal custom)",
    "part_of_speech": "noun",
    "domain": "Social & Kinship",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 114,
    "tulu_kannada": "ಅಜ್ಜೆ",
    "tulu_tigalari": "𑎀𑎙𑏐𑎙𑏁",
    "tulu_latin": "ajje",
    "english": "Grandfather / Paternal or maternal grandfather",
    "part_of_speech": "noun",
    "domain": "Social & Kinship",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 115,
    "tulu_kannada": "ಅಜ್ಜಿ",
    "tulu_tigalari": "𑎀𑎙𑏐𑎙𑎹",
    "tulu_latin": "ajji",
    "english": "Grandmother / Paternal or maternal grandmother",
    "part_of_speech": "noun",
    "domain": "Social & Kinship",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 116,
    "tulu_kannada": "ಬಂಟೆ",
    "tulu_tigalari": "𑎨𑏌𑎜𑏁",
    "tulu_latin": "baMTe",
    "english": "Stalwart warrior / Retainer of coastal chieftains",
    "part_of_speech": "noun",
    "domain": "Social & Kinship",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 117,
    "tulu_kannada": "ದೈವ",
    "tulu_tigalari": "𑎣𑏅𑎮",
    "tulu_latin": "daiva",
    "english": "Guardian protector spirit of village and lineage shrine",
    "part_of_speech": "noun",
    "domain": "Ritual & Belief",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 118,
    "tulu_kannada": "ಭೂತ",
    "tulu_tigalari": "𑎩𑎼𑎡",
    "tulu_latin": "bhoota",
    "english": "Spiritual deity of ancestral power venerated in Kola",
    "part_of_speech": "noun",
    "domain": "Ritual & Belief",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 119,
    "tulu_kannada": "ಕೋಲ",
    "tulu_tigalari": "𑎒𑏇𑎭",
    "tulu_latin": "kOla",
    "english": "Spirit propitiation ceremony marked by elaborate dance and mask",
    "part_of_speech": "noun",
    "domain": "Ritual & Belief",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 120,
    "tulu_kannada": "ನೇಮ",
    "tulu_tigalari": "𑎥𑏂𑎪",
    "tulu_latin": "nEma",
    "english": "Periodic high festival of lineage spirits",
    "part_of_speech": "noun",
    "domain": "Ritual & Belief",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 121,
    "tulu_kannada": "ತಂಬಿಲ",
    "tulu_tigalari": "𑎡𑏌𑎨𑎹𑎭",
    "tulu_latin": "taMbila",
    "english": "Domestic ritual offering of beaten rice and coconuts to home spirits",
    "part_of_speech": "noun",
    "domain": "Ritual & Belief",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 122,
    "tulu_kannada": "ಪಾಡ್ಡನ",
    "tulu_tigalari": "𑎦𑎸𑎞𑏐𑎞𑎥",
    "tulu_latin": "paaDDana",
    "english": "Epic verse ballad recited in Tulu meters commemorating heroes and spirits",
    "part_of_speech": "noun",
    "domain": "Ritual & Belief",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 123,
    "tulu_kannada": "ಸಿರಿ",
    "tulu_tigalari": "𑎱𑎹𑎬𑎹",
    "tulu_latin": "siri",
    "english": "Epic folk heroine renowned for divine truth and justice",
    "part_of_speech": "noun",
    "domain": "Ritual & Belief",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 124,
    "tulu_kannada": "ಕಲ್ಲುರ್ಟಿ",
    "tulu_tigalari": "𑎒𑎭𑏐𑎭𑎻𑎬𑏐𑎜𑎹",
    "tulu_latin": "kallurTi",
    "english": "Sculptor maiden spirit venerated in traditional shrines",
    "part_of_speech": "noun",
    "domain": "Ritual & Belief",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 125,
    "tulu_kannada": "ಪಂಜುರ್ಲಿ",
    "tulu_tigalari": "𑎦𑏌𑎙𑎻𑎬𑏐𑎭𑎹",
    "tulu_latin": "paMjurli",
    "english": "Divine wild boar spirit protecting agriculture from pests",
    "part_of_speech": "noun",
    "domain": "Ritual & Belief",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 126,
    "tulu_kannada": "ಗುಳಿಗೆ",
    "tulu_tigalari": "𑎔𑎻𑎳𑎹𑎔𑏁",
    "tulu_latin": "guLige",
    "english": "Fierce boundary-guarding deity protecting fields and borders",
    "part_of_speech": "noun",
    "domain": "Ritual & Belief",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 127,
    "tulu_kannada": "ಜುಮಾದಿ",
    "tulu_tigalari": "𑎙𑎻𑎪𑎸𑎣𑎹",
    "tulu_latin": "jumaadi",
    "english": "Noble hermaphroditic royal spirit of Tulunadu",
    "part_of_speech": "noun",
    "domain": "Ritual & Belief",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 128,
    "tulu_kannada": "ತಾರಾಯಿ",
    "tulu_tigalari": "𑎡𑎸𑎬𑎸𑎫𑎹",
    "tulu_latin": "taaraayi",
    "english": "Ripe coconut with thick white kernel used daily in coastal cooking",
    "part_of_speech": "noun",
    "domain": "Flora & Agriculture",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 129,
    "tulu_kannada": "ಕಂಗು",
    "tulu_tigalari": "𑎒𑏌𑎔𑎻",
    "tulu_latin": "kaMgu",
    "english": "Areca nut palm tree flourishing in coastal shaded orchards",
    "part_of_speech": "noun",
    "domain": "Flora & Agriculture",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 130,
    "tulu_kannada": "ಬಜ್ಜೆಯಿ",
    "tulu_tigalari": "𑎨𑎙𑏐𑎙𑏁𑎫𑎹",
    "tulu_latin": "bajjeyi",
    "english": "Dried areca nut chewed with betel leaf and slaked lime",
    "part_of_speech": "noun",
    "domain": "Flora & Agriculture",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 131,
    "tulu_kannada": "ಪೆಲಕಾಯಿ",
    "tulu_tigalari": "𑎦𑏁𑎭𑎒𑎸𑎫𑎹",
    "tulu_latin": "pelakaayi",
    "english": "Jackfruit with sweet yellow bulbs / Staple seasonal fruit of Tulunadu",
    "part_of_speech": "noun",
    "domain": "Flora & Agriculture",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 132,
    "tulu_kannada": "ಮಾಂಗಾಯಿ",
    "tulu_tigalari": "𑎪𑎸𑏌𑎔𑎸𑎫𑎹",
    "tulu_latin": "maaMgaayi",
    "english": "Raw green mango pickled in brine with red chillies",
    "part_of_speech": "noun",
    "domain": "Flora & Agriculture",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 133,
    "tulu_kannada": "ಕುಕ್ಕು",
    "tulu_tigalari": "𑎒𑎻𑎒𑏐𑎒𑎻",
    "tulu_latin": "kukku",
    "english": "Sweet ripe mango fruit celebrated in coastal songs",
    "part_of_speech": "noun",
    "domain": "Flora & Agriculture",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 134,
    "tulu_kannada": "ತೇವು",
    "tulu_tigalari": "𑎡𑏂𑎮𑎻",
    "tulu_latin": "tEvu",
    "english": "Wild edible colocasia leaf harvested for savoury rolled rolls (patrode)",
    "part_of_speech": "noun",
    "domain": "Flora & Agriculture",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 135,
    "tulu_kannada": "ತಪ್ಪು",
    "tulu_tigalari": "𑎡𑎦𑏐𑎦𑎻",
    "tulu_latin": "tappu",
    "english": "Fresh green leafy vegetables gathered from garden",
    "part_of_speech": "noun",
    "domain": "Flora & Agriculture",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 136,
    "tulu_kannada": "ಅರಿಶಿನ",
    "tulu_tigalari": "𑎀𑎬𑎹𑎯𑎹𑎥",
    "tulu_latin": "arishina",
    "english": "Yellow turmeric rhizome used as holy purifier and spice",
    "part_of_speech": "noun",
    "domain": "Flora & Agriculture",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 137,
    "tulu_kannada": "ಮೆಣಸು",
    "tulu_tigalari": "𑎪𑏁𑎠𑎱𑎻",
    "tulu_latin": "meNasu",
    "english": "Black pepper vine berries cultivated on areca palm trunks",
    "part_of_speech": "noun",
    "domain": "Flora & Agriculture",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 138,
    "tulu_kannada": "ಶುಂಠಿ",
    "tulu_tigalari": "𑎯𑎻𑏌𑎝𑎹",
    "tulu_latin": "shuMThi",
    "english": "Fresh ginger root adding pungent aroma to herbal decoctions",
    "part_of_speech": "noun",
    "domain": "Flora & Agriculture",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 139,
    "tulu_kannada": "ಜೀರಿಗೆ",
    "tulu_tigalari": "𑎙𑎺𑎬𑎹𑎔𑏁",
    "tulu_latin": "jeerige",
    "english": "Aromatic cumin seeds tempering coastal lentil gravies",
    "part_of_speech": "noun",
    "domain": "Flora & Agriculture",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 140,
    "tulu_kannada": "ಸಾಸಿವೆ",
    "tulu_tigalari": "𑎱𑎸𑎱𑎹𑎮𑏁",
    "tulu_latin": "saasive",
    "english": "Tiny black mustard seeds popped in smoking coconut oil",
    "part_of_speech": "noun",
    "domain": "Flora & Agriculture",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 141,
    "tulu_kannada": "ಹುಣಸೆ",
    "tulu_tigalari": "𑎲𑎻𑎠𑎱𑏁",
    "tulu_latin": "huNase",
    "english": "Sour tamarind pods extracted for coastal fish curry",
    "part_of_speech": "noun",
    "domain": "Flora & Agriculture",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 142,
    "tulu_kannada": "ಬೆಳ್ಳುಳ್ಳಿ",
    "tulu_tigalari": "𑎨𑏁𑎳𑏐𑎳𑎻𑎳𑏐𑎳𑎹",
    "tulu_latin": "beLLuLLi",
    "english": "Pungent garlic cloves crushed into spicy masalas",
    "part_of_speech": "noun",
    "domain": "Flora & Agriculture",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 143,
    "tulu_kannada": "ಈರುಳ್ಳಿ",
    "tulu_tigalari": "𑎃𑎬𑎻𑎳𑏐𑎳𑎹",
    "tulu_latin": "eeruLLi",
    "english": "Red onion bulbs slicing into side salads and sambar",
    "part_of_speech": "noun",
    "domain": "Flora & Agriculture",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 144,
    "tulu_kannada": "ವಣಸ್",
    "tulu_tigalari": "𑎮𑎠𑎱𑏎",
    "tulu_latin": "vaNas",
    "english": "Formal noon or evening meal of rice and accompaniments",
    "part_of_speech": "noun",
    "domain": "Food & Dining",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 145,
    "tulu_kannada": "ನುಪ್ಪು",
    "tulu_tigalari": "𑎥𑎻𑎦𑏐𑎦𑎻",
    "tulu_latin": "nuppu",
    "english": "Hot cooked white rice / Core staple of every Tulu household",
    "part_of_speech": "noun",
    "domain": "Food & Dining",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 146,
    "tulu_kannada": "ಗಂಜಿ",
    "tulu_tigalari": "𑎔𑏌𑎙𑎹",
    "tulu_latin": "gaMji",
    "english": "Boiled rice porridge served with salted pickles and coconut chutney",
    "part_of_speech": "noun",
    "domain": "Food & Dining",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 147,
    "tulu_kannada": "ಸಾರು",
    "tulu_tigalari": "𑎱𑎸𑎬𑎻",
    "tulu_latin": "saaru",
    "english": "Spicy aromatic broth seasoned with pepper and tamarind",
    "part_of_speech": "noun",
    "domain": "Food & Dining",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 148,
    "tulu_kannada": "ಬಜ್ಜಿ",
    "tulu_tigalari": "𑎨𑎙𑏐𑎙𑎹",
    "tulu_latin": "bajji",
    "english": "Vegetable fritters dipped in spiced gram flour and fried in oil",
    "part_of_speech": "noun",
    "domain": "Food & Dining",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 149,
    "tulu_kannada": "ಚಟ್ನಿ",
    "tulu_tigalari": "𑎗𑎜𑏐𑎥𑎹",
    "tulu_latin": "chaTni",
    "english": "Fresh ground paste of coconut, green chillies, ginger and salt",
    "part_of_speech": "noun",
    "domain": "Food & Dining",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 150,
    "tulu_kannada": "ರೊಟ್ಟಿ",
    "tulu_tigalari": "𑎬𑏆𑎜𑏐𑎜𑎹",
    "tulu_latin": "roTTi",
    "english": "Thin unleavened flatbread baked upon hot earthen griddle",
    "part_of_speech": "noun",
    "domain": "Food & Dining",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 151,
    "tulu_kannada": "ದೋಸೆ",
    "tulu_tigalari": "𑎣𑏇𑎱𑏁",
    "tulu_latin": "dOse",
    "english": "Fermented rice and black gram batter crisped on flat skillet",
    "part_of_speech": "noun",
    "domain": "Food & Dining",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 152,
    "tulu_kannada": "ಪೇರ್",
    "tulu_tigalari": "𑎦𑏂𑎬𑏎",
    "tulu_latin": "pEr",
    "english": "Fresh cows milk drawn at dawn in farmstead",
    "part_of_speech": "noun",
    "domain": "Food & Dining",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 153,
    "tulu_kannada": "ತುಪ್ಪ",
    "tulu_tigalari": "𑎡𑎻𑎦𑏐𑎦",
    "tulu_latin": "tuppa",
    "english": "Clarified golden cow ghee fragranced with cardamom",
    "part_of_speech": "noun",
    "domain": "Food & Dining",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 154,
    "tulu_kannada": "ಬೆಲ್ಲ",
    "tulu_tigalari": "𑎨𑏁𑎭𑏐𑎭",
    "tulu_latin": "bella",
    "english": "Unrefined dark jaggery boiled down from sugarcane syrup",
    "part_of_speech": "noun",
    "domain": "Food & Dining",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 155,
    "tulu_kannada": "ಚೀಪೆ",
    "tulu_tigalari": "𑎗𑎺𑎦𑏁",
    "tulu_latin": "cheepe",
    "english": "Pleasing sweet sugary taste delighting the tongue",
    "part_of_speech": "adjective",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 156,
    "tulu_kannada": "ಪುಳಿ",
    "tulu_tigalari": "𑎦𑎻𑎳𑎹",
    "tulu_latin": "puLi",
    "english": "Tangy acidulous sour taste of green mango and tamarind",
    "part_of_speech": "adjective",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 157,
    "tulu_kannada": "ಖಾರ",
    "tulu_tigalari": "𑎓𑎸𑎬",
    "tulu_latin": "khaara",
    "english": "Pungent fiery spicy heat of red and green chillies",
    "part_of_speech": "adjective",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 158,
    "tulu_kannada": "ಕಹಿ",
    "tulu_tigalari": "𑎒𑎲𑎹",
    "tulu_latin": "kahi",
    "english": "Medicinal bitter taste of neem leaf and wild gourd",
    "part_of_speech": "adjective",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 159,
    "tulu_kannada": "ಉಪ್ಪುನೀರ್",
    "tulu_tigalari": "𑎄𑎦𑏐𑎦𑎻𑎥𑎺𑎬𑏎",
    "tulu_latin": "uppuneer",
    "english": "Saline salt water of ocean tide and fish curing brine",
    "part_of_speech": "noun",
    "domain": "Food & Dining",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 160,
    "tulu_kannada": "ಬರ್ಸ",
    "tulu_tigalari": "𑎨𑎬𑏐𑎱",
    "tulu_latin": "barsa",
    "english": "Heavy monsoon downpour beating down upon thatched roofs",
    "part_of_speech": "noun",
    "domain": "Nature & Weather",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 161,
    "tulu_kannada": "ಪೊರ್ತು",
    "tulu_tigalari": "𑎦𑏆𑎬𑏐𑎡𑎻",
    "tulu_latin": "portu",
    "english": "Golden sunlight / Proper time of day / Hour of appointment",
    "part_of_speech": "noun",
    "domain": "Nature & Weather",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 162,
    "tulu_kannada": "ಬೊಲ್ಪು",
    "tulu_tigalari": "𑎨𑏆𑎭𑏐𑎦𑎻",
    "tulu_latin": "bolpu",
    "english": "Radiant morning light / Luminous glow of dawn",
    "part_of_speech": "noun",
    "domain": "Nature & Weather",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 163,
    "tulu_kannada": "ಗಾಳಿ",
    "tulu_tigalari": "𑎔𑎸𑎳𑎹",
    "tulu_latin": "gaaLi",
    "english": "Cool coastal sea breeze rustling palm fronds at sundown",
    "part_of_speech": "noun",
    "domain": "Nature & Weather",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 164,
    "tulu_kannada": "ತೂ",
    "tulu_tigalari": "𑎡𑎼",
    "tulu_latin": "too",
    "english": "Blazing fire / Crackling flame upon kitchen hearth",
    "part_of_speech": "noun",
    "domain": "Nature & Weather",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 165,
    "tulu_kannada": "ಮಣ್ಣು",
    "tulu_tigalari": "𑎪𑎠𑏐𑎠𑎻",
    "tulu_latin": "maNNu",
    "english": "Rich red fertile laterite soil of coastal hills and fields",
    "part_of_speech": "noun",
    "domain": "Nature & Weather",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 166,
    "tulu_kannada": "ಇನಿ",
    "tulu_tigalari": "𑎂𑎥𑎹",
    "tulu_latin": "ini",
    "english": "The present day / Today / At the current juncture",
    "part_of_speech": "adverb",
    "domain": "Time & Numbers",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 167,
    "tulu_kannada": "ಎಲ್ಲೆ",
    "tulu_tigalari": "𑎊𑎭𑏐𑎭𑏁",
    "tulu_latin": "elle",
    "english": "The following day / Tomorrow / In the near future",
    "part_of_speech": "adverb",
    "domain": "Time & Numbers",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 168,
    "tulu_kannada": "ಕೋಡೆ್",
    "tulu_tigalari": "𑎒𑏇𑎞𑏁𑏎",
    "tulu_latin": "kODae",
    "english": "The preceding day / Yesterday (Männer: marked by distinct open vowel)",
    "part_of_speech": "adverb",
    "domain": "Time & Numbers",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 169,
    "tulu_kannada": "ಮುನ್ನಾಡೆ",
    "tulu_tigalari": "𑎪𑎻𑎥𑏐𑎥𑎸𑎞𑏁",
    "tulu_latin": "munnaaDe",
    "english": "The day before yesterday / Two days past",
    "part_of_speech": "adverb",
    "domain": "Time & Numbers",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 170,
    "tulu_kannada": "ಕಾಂಡೆ",
    "tulu_tigalari": "𑎒𑎸𑏌𑎞𑏁",
    "tulu_latin": "kaaMDe",
    "english": "Early morning twilight when cocks begin to crow",
    "part_of_speech": "noun",
    "domain": "Time & Numbers",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 171,
    "tulu_kannada": "ಬಯ್ಯ",
    "tulu_tigalari": "𑎨𑎫𑏐𑎫",
    "tulu_latin": "bayya",
    "english": "Dusk / Evening twilight when sea breeze cooleth the land",
    "part_of_speech": "noun",
    "domain": "Time & Numbers",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 172,
    "tulu_kannada": "ರಾತ್ರೆ",
    "tulu_tigalari": "𑎬𑎸𑎡𑏐𑎬𑏁",
    "tulu_latin": "raatre",
    "english": "Darkness of night beneath canopy of southern stars",
    "part_of_speech": "noun",
    "domain": "Time & Numbers",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 173,
    "tulu_kannada": "ಕಣ್ಣ್",
    "tulu_tigalari": "𑎒𑎠𑏐𑎠𑏎",
    "tulu_latin": "kaNN",
    "english": "Eye / Organ of sight / Loving or piercing glance",
    "part_of_speech": "noun",
    "domain": "Anatomy & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 174,
    "tulu_kannada": "ಕರ್ಬು",
    "tulu_tigalari": "𑎒𑎬𑏐𑎨𑎻",
    "tulu_latin": "karbu",
    "english": "Ear / Organ of hearing words and musical tunes",
    "part_of_speech": "noun",
    "domain": "Anatomy & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 175,
    "tulu_kannada": "ಮೂಕು",
    "tulu_tigalari": "𑎪𑎼𑎒𑎻",
    "tulu_latin": "mooku",
    "english": "Nose / Organ of breathing and smelling fragrance",
    "part_of_speech": "noun",
    "domain": "Anatomy & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 176,
    "tulu_kannada": "ಬಾಯಿ",
    "tulu_tigalari": "𑎨𑎸𑎫𑎹",
    "tulu_latin": "baayi",
    "english": "Mouth / Organ of eating and pronouncing spoken words",
    "part_of_speech": "noun",
    "domain": "Anatomy & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 177,
    "tulu_kannada": "ಕೈ",
    "tulu_tigalari": "𑎒𑏅",
    "tulu_latin": "kai",
    "english": "Hand / Arm / Organ of craftsmanship and giving gifts",
    "part_of_speech": "noun",
    "domain": "Anatomy & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 178,
    "tulu_kannada": "ಕಾರ್",
    "tulu_tigalari": "𑎒𑎸𑎬𑏎",
    "tulu_latin": "kaar",
    "english": "Foot / Leg / Limb enabling journeying upon pathways",
    "part_of_speech": "noun",
    "domain": "Anatomy & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 179,
    "tulu_kannada": "ನೆತ್ತೆರ್",
    "tulu_tigalari": "𑎥𑏁𑎡𑏐𑎡𑏁𑎬𑏎",
    "tulu_latin": "netter",
    "english": "Crimson lifeblood coursing within veins and heart",
    "part_of_speech": "noun",
    "domain": "Anatomy & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 180,
    "tulu_kannada": "ಕೂಲಿ",
    "tulu_tigalari": "𑎒𑎼𑎭𑎹",
    "tulu_latin": "kooli",
    "english": "Tooth / Strong ivory grinder of food",
    "part_of_speech": "noun",
    "domain": "Anatomy & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 181,
    "tulu_kannada": "ನಾಲಾಯಿ",
    "tulu_tigalari": "𑎥𑎸𑎭𑎸𑎫𑎹",
    "tulu_latin": "naalaayi",
    "english": "Tongue / Organ of discerning savours and articulating vowels",
    "part_of_speech": "noun",
    "domain": "Anatomy & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 182,
    "tulu_kannada": "ಬೆರಿ",
    "tulu_tigalari": "𑎨𑏁𑎬𑎹",
    "tulu_latin": "beri",
    "english": "Strong back of man supporting burdens of harvest",
    "part_of_speech": "noun",
    "domain": "Anatomy & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 183,
    "tulu_kannada": "ಗುಂಡಿಗೆ",
    "tulu_tigalari": "𑎔𑎻𑏌𑎞𑎹𑎔𑏁",
    "tulu_latin": "guMDige",
    "english": "Brave heart / Seat of valor, compassion and devotion",
    "part_of_speech": "noun",
    "domain": "Anatomy & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 184,
    "tulu_kannada": "ಜೀವ",
    "tulu_tigalari": "𑎙𑎺𑎮",
    "tulu_latin": "jeeva",
    "english": "Vital breath of life animating mortal clay",
    "part_of_speech": "noun",
    "domain": "Anatomy & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 185,
    "tulu_kannada": "ಎಡ್ಡೆ",
    "tulu_tigalari": "𑎊𑎞𑏐𑎞𑏁",
    "tulu_latin": "eDDe",
    "english": "Virtuous / Excellent / Beneficial / Beautiful in character",
    "part_of_speech": "adjective",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 186,
    "tulu_kannada": "ಹಾಳ್",
    "tulu_tigalari": "𑎲𑎸𑎳𑏎",
    "tulu_latin": "haaL",
    "english": "Ruinous / Corrupt / Bad / Destroyed by neglect",
    "part_of_speech": "adjective",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 187,
    "tulu_kannada": "ಮಲ್ಲ",
    "tulu_tigalari": "𑎪𑎭𑏐𑎭",
    "tulu_latin": "malla",
    "english": "Great in stature / Grand in renown / Vast in size",
    "part_of_speech": "adjective",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 188,
    "tulu_kannada": "ಎಲ್ಯ",
    "tulu_tigalari": "𑎊𑎭𑏐𑎫",
    "tulu_latin": "elya",
    "english": "Small in size / Modest in scale / Slender",
    "part_of_speech": "adjective",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 189,
    "tulu_kannada": "ಪೊರ್ಲು",
    "tulu_tigalari": "𑎦𑏆𑎬𑏐𑎭𑎻",
    "tulu_latin": "porlu",
    "english": "Graceful / Symmetrically beautiful / Pleasing to behold",
    "part_of_speech": "adjective",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 190,
    "tulu_kannada": "ಕಪ್ಪು",
    "tulu_tigalari": "𑎒𑎦𑏐𑎦𑎻",
    "tulu_latin": "kappu",
    "english": "Deep black as rain-laden cloud or raven feather",
    "part_of_speech": "adjective",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 191,
    "tulu_kannada": "ಬೊಳ್ದು",
    "tulu_tigalari": "𑎨𑏆𑎳𑏐𑎣𑎻",
    "tulu_latin": "boLdu",
    "english": "Pristine white as fresh jasmine flower or cow milk",
    "part_of_speech": "adjective",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 192,
    "tulu_kannada": "ಕೆಂಪು",
    "tulu_tigalari": "𑎒𑏁𑏌𑎦𑎻",
    "tulu_latin": "keMpu",
    "english": "Vibrant crimson red as hibiscus petal or setting sun",
    "part_of_speech": "adjective",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 193,
    "tulu_kannada": "ಮಂಜೊಲು",
    "tulu_tigalari": "𑎪𑏌𑎙𑏆𑎭𑎻",
    "tulu_latin": "maMjolu",
    "english": "Golden yellow as ground turmeric paste",
    "part_of_speech": "adjective",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 194,
    "tulu_kannada": "ಪಚ್ಚೆ",
    "tulu_tigalari": "𑎦𑎗𑏐𑎗𑏁",
    "tulu_latin": "pachche",
    "english": "Lush emerald green as newly sprouted paddy shoot",
    "part_of_speech": "adjective",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 195,
    "tulu_kannada": "ಚಂದ",
    "tulu_tigalari": "𑎗𑏌𑎣",
    "tulu_latin": "chaMda",
    "english": "Charming / Delightful / Well-proportioned in form",
    "part_of_speech": "adjective",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 196,
    "tulu_kannada": "ಭದ್ರ",
    "tulu_tigalari": "𑎩𑎣𑏐𑎬",
    "tulu_latin": "bhadra",
    "english": "Secure / Strongly bolted / Free from peril",
    "part_of_speech": "adjective",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 197,
    "tulu_kannada": "ಗಟ್ಟ",
    "tulu_tigalari": "𑎔𑎜𑏐𑎜",
    "tulu_latin": "gaTTa",
    "english": "Firm / Dense / Resolute in heart against fear",
    "part_of_speech": "adjective",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 198,
    "tulu_kannada": "ಮೆಲ್ಲ",
    "tulu_tigalari": "𑎪𑏁𑎭𑏐𑎭",
    "tulu_latin": "mella",
    "english": "Gentle / Soft-spoken / Moving with deliberate slowness",
    "part_of_speech": "adverb",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 199,
    "tulu_kannada": "ಬೇಗ",
    "tulu_tigalari": "𑎨𑏂𑎔",
    "tulu_latin": "bEga",
    "english": "Swiftly / In rapid tempo without lagging",
    "part_of_speech": "adverb",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 200,
    "tulu_kannada": "ದೂರ",
    "tulu_tigalari": "𑎣𑎼𑎬",
    "tulu_latin": "doora",
    "english": "Distant across many hills and rivers",
    "part_of_speech": "adjective",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 201,
    "tulu_kannada": "ಮುಟ್ಟ",
    "tulu_tigalari": "𑎪𑎻𑎜𑏐𑎜",
    "tulu_latin": "muTTa",
    "english": "Near at hand / Close unto boundary / Right up to",
    "part_of_speech": "adverb",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 202,
    "tulu_kannada": "ತುಂಬಾ",
    "tulu_tigalari": "𑎡𑎻𑏌𑎨𑎸",
    "tulu_latin": "tuMbaa",
    "english": "Abundantly overflowing / Full unto vessel brim",
    "part_of_speech": "adjective",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 203,
    "tulu_kannada": "ಒಂತೆ",
    "tulu_tigalari": "𑎏𑏌𑎡𑏁",
    "tulu_latin": "oMte",
    "english": "A modest measure / A little portion / Somewhat",
    "part_of_speech": "adverb",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  },
  {
    "id": 204,
    "tulu_kannada": "ಶುದ್ಧ",
    "tulu_tigalari": "𑎯𑎻𑎣𑏐𑎤",
    "tulu_latin": "shuddha",
    "english": "Pristine pure / Cleansed of all defilement and dust",
    "part_of_speech": "adjective",
    "domain": "Qualities & Senses",
    "source": "Rev. August Männer (1886), Basel Mission Press, Mangalore"
  }
];

function searchHistoricalDictionary(query, domain, pos) {
  const q = (query || "").trim().toLowerCase();
  return HISTORICAL_TULU_CORPUS.filter(item => {
    if (domain && domain !== "all" && item.domain !== domain) return false;
    if (pos && pos !== "all" && item.part_of_speech !== pos) return false;
    if (!q) return true;
    return item.english.toLowerCase().includes(q) ||
           item.tulu_kannada.includes(q) ||
           item.tulu_latin.toLowerCase().includes(q) ||
           item.domain.toLowerCase().includes(q);
  });
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { HISTORICAL_TULU_CORPUS, searchHistoricalDictionary };
}
