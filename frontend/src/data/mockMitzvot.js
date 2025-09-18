// Mock data for 613 Biblical Laws
export const categories = [
  { id: 'faith-god', name: 'Faith & Relationship with God', count: 8 },
  { id: 'torah-study', name: 'Torah Study & Teaching', count: 8 },
  { id: 'temple-worship', name: 'Temple & Worship', count: 85 },
  { id: 'dietary-laws', name: 'Dietary Laws', count: 19 },
  { id: 'tithes-offerings', name: 'Tithes & Offerings', count: 9 },
  { id: 'festivals', name: 'Festivals & Holy Days', count: 43 },
  { id: 'ethics-morality', name: 'Ethics & Morality', count: 65 },
  { id: 'family-marriage', name: 'Family & Marriage', count: 48 },
  { id: 'civil-criminal', name: 'Civil & Criminal Law', count: 76 },
  { id: 'purity-laws', name: 'Purity Laws', count: 52 },
  { id: 'business-society', name: 'Business & Society', count: 34 },
  { id: 'leadership', name: 'Leadership & Government', count: 23 },
  { id: 'land-agriculture', name: 'Land & Agriculture', count: 43 },
  { id: 'other', name: 'Other Laws', count: 100 }
];

export const statusTypes = [
  { value: 'direct', label: 'Direct in Bible', color: 'bg-green-100 text-green-800' },
  { value: 'indirect', label: 'Indirect in Bible', color: 'bg-blue-100 text-blue-800' },
  { value: 'rabbinic', label: 'Rabbinic Origin', color: 'bg-purple-100 text-purple-800' },
  { value: 'traditional', label: 'Traditional', color: 'bg-orange-100 text-orange-800' }
];

export const mockMitzvot = [
  {
    id: 1,
    number: 1,
    title: "To know that God exists",
    traditionalWording: "To believe in the existence of God.",
    sourceVerse: "Exodus 20:2 — \"I am the LORD thy God, which have brought thee out of the land of Egypt, out of the house of bondage.\"",
    book: "Exodus",
    chapter: 20,
    verse: 2,
    status: "direct",
    category: "faith-god",
    scholarlyNote: "Maimonides places this as the first mitzvah. While some scholars view it as more of a declaration than a command, Dead Sea Scrolls fragments confirm its foundational role in Israelite faith.",
    keywords: ["God", "existence", "belief", "faith", "foundation", "monotheism"]
  },
  {
    id: 2,
    number: 2,
    title: "Not to entertain thoughts of other gods",
    traditionalWording: "Do not even think there are other gods before Me.",
    sourceVerse: "Exodus 20:3 — \"Thou shalt have no other gods before me.\"",
    book: "Exodus",
    chapter: 20,
    verse: 3,
    status: "direct",
    category: "faith-god",
    scholarlyNote: "This commandment is universally preserved across Bible versions, including the Septuagint. It serves as a cornerstone of monotheism.",
    keywords: ["idolatry", "monotheism", "thoughts", "gods", "commandment"]
  },
  {
    id: 21,
    number: 21,
    title: "Not to eat blood",
    traditionalWording: "Abstain from consuming blood.",
    sourceVerse: "Leviticus 7:26 — \"Moreover ye shall eat no manner of blood, whether it be of fowl or of beast, in any of your dwellings.\"",
    book: "Leviticus",
    chapter: 7,
    verse: 26,
    status: "direct",
    category: "dietary-laws",
    scholarlyNote: "Universally recognized prohibition; reinforced multiple times across Leviticus and Deuteronomy.",
    keywords: ["blood", "dietary", "kosher", "prohibition", "consumption"]
  },
  {
    id: 30,
    number: 30,
    title: "To slaughter animals before eating",
    traditionalWording: "Animals must be slaughtered properly before eating.",
    sourceVerse: "Deuteronomy 12:21 — \"If the place which the LORD thy God hath chosen... be too far from thee, then thou shalt kill of thy herd and of thy flock... as I have commanded thee, and thou shalt eat in thy gates.\"",
    book: "Deuteronomy",
    chapter: 12,
    verse: 21,
    status: "indirect",
    category: "dietary-laws",
    scholarlyNote: "Verse presumes knowledge of proper slaughter \"as I have commanded,\" though Torah gives no explicit details; rabbinic tradition preserves the method (shechita).",
    keywords: ["slaughter", "shechita", "kosher", "animals", "food preparation"]
  },
  {
    id: 51,
    number: 51,
    title: "To rest on the Sabbath day",
    traditionalWording: "Cease all work on the seventh day.",
    sourceVerse: "Exodus 20:8–10 — \"Remember the sabbath day, to keep it holy... in it thou shalt not do any work.\"",
    book: "Exodus",
    chapter: 20,
    verse: "8-10",
    status: "direct",
    category: "festivals",
    scholarlyNote: "Sabbath observance is a core commandment with repeated emphasis.",
    keywords: ["Sabbath", "rest", "holy", "work", "seventh day"]
  },
  {
    id: 115,
    number: 115,
    title: "To honor father and mother",
    traditionalWording: "Respect and honor parents.",
    sourceVerse: "Exodus 20:12 — \"Honour thy father and thy mother: that thy days may be long upon the land which the LORD thy God giveth thee.\"",
    book: "Exodus",
    chapter: 20,
    verse: 12,
    status: "direct",
    category: "family-marriage",
    scholarlyNote: "One of the Ten Commandments, emphasizing family structure and respect for authority.",
    keywords: ["parents", "honor", "respect", "family", "commandment"]
  },
  {
    id: 98,
    number: 98,
    title: "To judge fairly",
    traditionalWording: "Judge honestly and impartially.",
    sourceVerse: "Leviticus 19:15 — \"Ye shall do no unrighteousness in judgment: thou shalt not respect the person of the poor, nor honour the person of the mighty: but in righteousness shalt thou judge thy neighbour.\"",
    book: "Leviticus",
    chapter: 19,
    verse: 15,
    status: "direct",
    category: "civil-criminal",
    scholarlyNote: "Foundation of biblical justice system, emphasizing impartiality regardless of social status.",
    keywords: ["justice", "judgment", "impartial", "righteousness", "law"]
  },
  {
    id: 208,
    number: 208,
    title: "To love your neighbor as yourself",
    traditionalWording: "Love your neighbor.",
    sourceVerse: "Leviticus 19:18 — \"Thou shalt not avenge, nor bear any grudge against the children of thy people, but thou shalt love thy neighbour as thyself: I am the LORD.\"",
    book: "Leviticus",
    chapter: 19,
    verse: 18,
    status: "direct",
    category: "ethics-morality",
    scholarlyNote: "Called by Jesus the second greatest commandment, foundational to biblical ethics.",
    keywords: ["love", "neighbor", "ethics", "relationship", "commandment"]
  }
];

// Generate additional mock data to represent full 613 count
const generateMockMitzvot = () => {
  const additional = [];
  for (let i = 9; i <= 613; i++) {
    if (![21, 30, 51, 98, 115, 208].includes(i)) {
      const category = categories[Math.floor(Math.random() * categories.length)];
      const status = statusTypes[Math.floor(Math.random() * statusTypes.length)];
      const books = ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy'];
      const book = books[Math.floor(Math.random() * books.length)];
      
      additional.push({
        id: i,
        number: i,
        title: `Mitzvah ${i} - Sample Law`,
        traditionalWording: `Traditional wording for mitzvah ${i}.`,
        sourceVerse: `${book} ${Math.floor(Math.random() * 50) + 1}:${Math.floor(Math.random() * 30) + 1} — "Sample verse text for mitzvah ${i}."`,
        book: book,
        chapter: Math.floor(Math.random() * 50) + 1,
        verse: Math.floor(Math.random() * 30) + 1,
        status: status.value,
        category: category.id,
        scholarlyNote: `Scholarly note explaining the context and significance of mitzvah ${i}.`,
        keywords: ['sample', 'law', 'commandment', 'torah']
      });
    }
  }
  return additional;
};

export const allMitzvot = [...mockMitzvot, ...generateMockMitzvot()].sort((a, b) => a.number - b.number);