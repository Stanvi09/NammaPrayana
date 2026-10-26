import { useLanguage } from "@/constants/LanguageContext";
import { useState } from "react";
import {
  Image,
  Linking,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

// These files must exist in the project's assets folder.
import englishMap from "../../assets/sitemapimgeng.jpg";
import kannadaMap from "../../assets/sitemapimgkan.jpg";

type Language = "en" | "kn" | "hi";
type Line = "Purple" | "Green" | "Yellow" | "Interchange";

type Station = {
  id: string;
  names: Record<Language, string>;
  line: Line;
};

const stations: Station[] = [
  // Purple Line
  {
    id: "whitefield",
    names: {
      en: "Whitefield (Kadugodi)",
      kn: "ವೈಟ್‌ಫೀಲ್ಡ್ (ಕಾಡುಗೋಡಿ)",
      hi: "व्हाइटफील्ड (काडुगोडी)",
    },
    line: "Purple",
  },
  {
    id: "hopefarm",
    names: {
      en: "Hopefarm Channasandra",
      kn: "ಹೋಪ್‌ಫಾರ್ಮ್ ಚನ್ನಸಂದ್ರ",
      hi: "होपफार्म चन्नसंद्र",
    },
    line: "Purple",
  },
  {
    id: "kadugodiTreePark",
    names: {
      en: "Kadugodi Tree Park",
      kn: "ಕಾಡುಗೋಡಿ ಟ್ರೀ ಪಾರ್ಕ್",
      hi: "काडुगोडी ट्री पार्क",
    },
    line: "Purple",
  },
  {
    id: "pattandurAgrahara",
    names: {
      en: "Pattandur Agrahara",
      kn: "ಪಟ್ಟಂದೂರು ಅಗ್ರಹಾರ",
      hi: "पट्टंदूर अग्रहारा",
    },
    line: "Purple",
  },
  {
    id: "sriSathyaSaiHospital",
    names: {
      en: "Sri Sathya Sai Hospital",
      kn: "ಶ್ರೀ ಸತ್ಯ ಸಾಯಿ ಆಸ್ಪತ್ರೆ",
      hi: "श्री सत्य साईं अस्पताल",
    },
    line: "Purple",
  },
  {
    id: "nallurhalli",
    names: { en: "Nallurhalli", kn: "ನಲ್ಲೂರಹಳ್ಳಿ", hi: "नल्लूरहल्ली" },
    line: "Purple",
  },
  {
    id: "kundalahalli",
    names: { en: "Kundalahalli", kn: "ಕುಂದಲಹಳ್ಳಿ", hi: "कुंदलहल्ली" },
    line: "Purple",
  },
  {
    id: "seetharampalya",
    names: { en: "Seetharampalya", kn: "ಸೀತಾರಾಮಪಾಳ್ಯ", hi: "सीतारामपाल्या" },
    line: "Purple",
  },
  {
    id: "hoodi",
    names: { en: "Hoodi", kn: "ಹೂಡಿ", hi: "हूडी" },
    line: "Purple",
  },
  {
    id: "garudacharpalya",
    names: {
      en: "Garudacharpalya",
      kn: "ಗರುಡಾಚಾರ್ಪಾಳ್ಯ",
      hi: "गरुडाचारपाल्या",
    },
    line: "Purple",
  },
  {
    id: "singayyanapalya",
    names: {
      en: "Singayyanapalya",
      kn: "ಸಿಂಗಯ್ಯನಪಾಳ್ಯ",
      hi: "सिंगय्यानपाल्या",
    },
    line: "Purple",
  },
  {
    id: "krPuram",
    names: {
      en: "Krishnarajapura (KR Pura)",
      kn: "ಕೃಷ್ಣರಾಜಪುರ",
      hi: "कृष्णराजपुरा",
    },
    line: "Purple",
  },
  {
    id: "benniganahalli",
    names: { en: "Benniganahalli", kn: "ಬೆನ್ನಿಗಾನಹಳ್ಳಿ", hi: "बेन्निगानहल्ली" },
    line: "Purple",
  },
  {
    id: "baiyappanahalli",
    names: { en: "Baiyappanahalli", kn: "ಬೈಯಪ್ಪನಹಳ್ಳಿ", hi: "बैयप्पनहल्ली" },
    line: "Purple",
  },
  {
    id: "svRoad",
    names: {
      en: "Swami Vivekananda Road",
      kn: "ಸ್ವಾಮಿ ವಿವೇಕಾನಂದ ರಸ್ತೆ",
      hi: "स्वामी विवेकानंद रोड",
    },
    line: "Purple",
  },
  {
    id: "indiranagar",
    names: { en: "Indiranagar", kn: "ಇಂದಿರಾನಗರ", hi: "इंदिरानगर" },
    line: "Purple",
  },
  {
    id: "halasuru",
    names: { en: "Halasuru", kn: "ಹಲಸೂರು", hi: "हलसूरु" },
    line: "Purple",
  },
  {
    id: "trinity",
    names: { en: "Trinity", kn: "ಟ್ರಿನಿಟಿ", hi: "ट्रिनिटी" },
    line: "Purple",
  },
  {
    id: "mgRoad",
    names: {
      en: "Mahatma Gandhi Road (MG Road)",
      kn: "ಮಹಾತ್ಮ ಗಾಂಧಿ ರಸ್ತೆ",
      hi: "महात्मा गांधी रोड",
    },
    line: "Purple",
  },
  {
    id: "cubbonPark",
    names: { en: "Cubbon Park", kn: "ಕಬ್ಬನ್ ಪಾರ್ಕ್", hi: "कब्बन पार्क" },
    line: "Purple",
  },
  {
    id: "vidhanaSoudha",
    names: { en: "Vidhana Soudha", kn: "ವಿಧಾನ ಸೌಧ", hi: "विधान सौधा" },
    line: "Purple",
  },
  {
    id: "centralCollege",
    names: {
      en: "Central College",
      kn: "ಸೆಂಟ್ರಲ್ ಕಾಲೇಜು",
      hi: "सेंट्रल कॉलेज",
    },
    line: "Purple",
  },
  {
    id: "majestic",
    names: {
      en: "Nadaprabhu Kempegowda Station (Majestic)",
      kn: "ನಾಡಪ್ರಭು ಕೆಂಪೇಗೌಡ ನಿಲ್ದಾಣ (ಮೆಜೆಸ್ಟಿಕ್)",
      hi: "नाडप्रभु केम्पेगौड़ा स्टेशन (मैजेस्टिक)",
    },
    line: "Interchange",
  },
  {
    id: "ksrRailwayStation",
    names: {
      en: "KSR Bengaluru City Railway Station",
      kn: "ಕೆಎಸ್‌ಆರ್ ಬೆಂಗಳೂರು ನಗರ ರೈಲು ನಿಲ್ದಾಣ",
      hi: "केएसआर बेंगलुरु सिटी रेलवे स्टेशन",
    },
    line: "Purple",
  },
  {
    id: "magadiRoad",
    names: { en: "Magadi Road", kn: "ಮಾಗಡಿ ರಸ್ತೆ", hi: "मगडी रोड" },
    line: "Purple",
  },
  {
    id: "hosahalli",
    names: { en: "Hosahalli", kn: "ಹೊಸಹಳ್ಳಿ", hi: "होसहल्ली" },
    line: "Purple",
  },
  {
    id: "vijayanagar",
    names: { en: "Vijayanagar", kn: "ವಿಜಯನಗರ", hi: "विजयनगर" },
    line: "Purple",
  },
  {
    id: "attiguppe",
    names: { en: "Attiguppe", kn: "ಅತ್ತಿಗುಪ್ಪೆ", hi: "अत्तिगुप्पे" },
    line: "Purple",
  },
  {
    id: "deepanjaliNagar",
    names: { en: "Deepanjali Nagar", kn: "ದೀಪಾಂಜಲಿ ನಗರ", hi: "दीपांजलि नगर" },
    line: "Purple",
  },
  {
    id: "mysoreRoad",
    names: { en: "Mysore Road", kn: "ಮೈಸೂರು ರಸ್ತೆ", hi: "मैसूर रोड" },
    line: "Purple",
  },
  {
    id: "nayandahalli",
    names: { en: "Nayandahalli", kn: "ನಾಯಂಡಹಳ್ಳಿ", hi: "नायंडहल्ली" },
    line: "Purple",
  },
  {
    id: "rrNagar",
    names: {
      en: "Rajarajeshwari Nagar",
      kn: "ರಾಜರಾಜೇಶ್ವರಿ ನಗರ",
      hi: "राजराजेश्वरी नगर",
    },
    line: "Purple",
  },
  {
    id: "jnanabharathi",
    names: { en: "Jnanabharathi", kn: "ಜ್ಞಾನಭಾರತಿ", hi: "ज्ञानभारती" },
    line: "Purple",
  },
  {
    id: "pattanagere",
    names: { en: "Pattanagere", kn: "ಪಟ್ಟಣಗೆರೆ", hi: "पट्टणगेरे" },
    line: "Purple",
  },
  {
    id: "kengeriBusTerminal",
    names: {
      en: "Kengeri Bus Terminal",
      kn: "ಕೆಂಗೇರಿ ಬಸ್ ಟರ್ಮಿನಲ್",
      hi: "केंगेरी बस टर्मिनल",
    },
    line: "Purple",
  },
  {
    id: "kengeri",
    names: { en: "Kengeri", kn: "ಕೆಂಗೇರಿ", hi: "केंगेरी" },
    line: "Purple",
  },
  {
    id: "challaghatta",
    names: { en: "Challaghatta", kn: "ಚಲ್ಲಘಟ್ಟ", hi: "चल्लघट्ट" },
    line: "Purple",
  },

  // Green Line
  {
    id: "madavara",
    names: {
      en: "Madavara (BIEC)",
      kn: "ಮಾದಾವರ (ಬಿಐಇಸಿ)",
      hi: "मदावरा (बीआईईसी)",
    },
    line: "Green",
  },
  {
    id: "chikkabidarakallu",
    names: {
      en: "Chikkabidarakallu",
      kn: "ಚಿಕ್ಕಬಿದರಕಲ್ಲು",
      hi: "चिक्कबिदरकल्लु",
    },
    line: "Green",
  },
  {
    id: "manjunathanagar",
    names: { en: "Manjunathanagar", kn: "ಮಂಜುನಾಥನಗರ", hi: "मंजुनाथनगर" },
    line: "Green",
  },
  {
    id: "nagasandra",
    names: { en: "Nagasandra", kn: "ನಾಗಸಂದ್ರ", hi: "नागसंद्र" },
    line: "Green",
  },
  {
    id: "dasarahalli",
    names: { en: "Dasarahalli", kn: "ದಾಸರಹಳ್ಳಿ", hi: "दासरहल्ली" },
    line: "Green",
  },
  {
    id: "jalahalli",
    names: { en: "Jalahalli", kn: "ಜಾಲಹಳ್ಳಿ", hi: "जलहल्ली" },
    line: "Green",
  },
  {
    id: "peenyaIndustry",
    names: {
      en: "Peenya Industry",
      kn: "ಪೀಣ್ಯ ಕೈಗಾರಿಕಾ ಪ್ರದೇಶ",
      hi: "पीन्या इंडस्ट्री",
    },
    line: "Green",
  },
  {
    id: "peenya",
    names: { en: "Peenya", kn: "ಪೀಣ್ಯ", hi: "पीन्या" },
    line: "Green",
  },
  {
    id: "goraguntepalya",
    names: { en: "Goraguntepalya", kn: "ಗೊರಗುಂಟೆಪಾಳ್ಯ", hi: "गोरगुंटेपाल्या" },
    line: "Green",
  },
  {
    id: "yeshwanthpur",
    names: { en: "Yeshwanthpur", kn: "ಯಶವಂತಪುರ", hi: "यशवंतपुर" },
    line: "Green",
  },
  {
    id: "sandalSoapFactory",
    names: {
      en: "Sandal Soap Factory",
      kn: "ಸ್ಯಾಂಡಲ್ ಸೋಪ್ ಫ್ಯಾಕ್ಟರಿ",
      hi: "सैंडल सोप फैक्ट्री",
    },
    line: "Green",
  },
  {
    id: "mahalakshmi",
    names: { en: "Mahalakshmi", kn: "ಮಹಾಲಕ್ಷ್ಮಿ", hi: "महालक्ष्मी" },
    line: "Green",
  },
  {
    id: "rajajinagar",
    names: { en: "Rajajinagar", kn: "ರಾಜಾಜಿನಗರ", hi: "राजाजीनगर" },
    line: "Green",
  },
  {
    id: "kuvempuRoad",
    names: { en: "Kuvempu Road", kn: "ಕುವೆಂಪು ರಸ್ತೆ", hi: "कुवेम्पु रोड" },
    line: "Green",
  },
  {
    id: "srirampura",
    names: { en: "Srirampura", kn: "ಶ್ರೀರಾಮಪುರ", hi: "श्रीरामपुरा" },
    line: "Green",
  },
  {
    id: "sampigeRoad",
    names: {
      en: "Mantri Square Sampige Road",
      kn: "ಮಂತ್ರಿ ಸ್ಕ್ವೇರ್ ಸಂಪಿಗೆ ರಸ್ತೆ",
      hi: "मंत्री स्क्वेयर संपिगे रोड",
    },
    line: "Green",
  },
  {
    id: "chickpete",
    names: { en: "Chickpete", kn: "ಚಿಕ್ಕಪೇಟೆ", hi: "चिकपेट" },
    line: "Green",
  },
  {
    id: "krMarket",
    names: {
      en: "Krishna Rajendra Market (KR Market)",
      kn: "ಕೃಷ್ಣ ರಾಜೇಂದ್ರ ಮಾರುಕಟ್ಟೆ",
      hi: "कृष्ण राजेंद्र मार्केट",
    },
    line: "Green",
  },
  {
    id: "nationalCollege",
    names: { en: "National College", kn: "ನ್ಯಾಷನಲ್ ಕಾಲೇಜು", hi: "नेशनल कॉलेज" },
    line: "Green",
  },
  {
    id: "lalbagh",
    names: { en: "Lalbagh", kn: "ಲಾಲ್‌ಬಾಗ್", hi: "लालबाग" },
    line: "Green",
  },
  {
    id: "southEndCircle",
    names: {
      en: "South End Circle",
      kn: "ಸೌತ್ ಎಂಡ್ ಸರ್ಕಲ್",
      hi: "साउथ एंड सर्कल",
    },
    line: "Green",
  },
  {
    id: "jayanagar",
    names: { en: "Jayanagar", kn: "ಜಯನಗರ", hi: "जयनगर" },
    line: "Green",
  },
  {
    id: "rvRoad",
    names: {
      en: "Rashtreeya Vidyalaya Road (RV Road)",
      kn: "ರಾಷ್ಟ್ರೀಯ ವಿದ್ಯಾಲಯ ರಸ್ತೆ",
      hi: "राष्ट्रीय विद्यालय रोड",
    },
    line: "Interchange",
  },
  {
    id: "banashankari",
    names: { en: "Banashankari", kn: "ಬನಶಂಕರಿ", hi: "बनशंकरी" },
    line: "Green",
  },
  {
    id: "jpNagar",
    names: { en: "JP Nagar", kn: "ಜೆಪಿ ನಗರ", hi: "जेपी नगर" },
    line: "Green",
  },
  {
    id: "yelachenahalli",
    names: { en: "Yelachenahalli", kn: "ಯಲಚೇನಹಳ್ಳಿ", hi: "यलचेनहल्ली" },
    line: "Green",
  },
  {
    id: "konanakunteCross",
    names: {
      en: "Konanakunte Cross",
      kn: "ಕೋಣನಕುಂಟೆ ಕ್ರಾಸ್",
      hi: "कोणनकुंटे क्रॉस",
    },
    line: "Green",
  },
  {
    id: "doddakallasandra",
    names: {
      en: "Doddakallasandra",
      kn: "ದೊಡ್ಡಕಲ್ಲಸಂದ್ರ",
      hi: "दोद्दकल्लसंद्र",
    },
    line: "Green",
  },
  {
    id: "vajrahalli",
    names: { en: "Vajrahalli", kn: "ವಜ್ರಹಳ್ಳಿ", hi: "वज्रहल्ली" },
    line: "Green",
  },
  {
    id: "thalaghattapura",
    names: { en: "Thalaghattapura", kn: "ತಲಘಟ್ಟಪುರ", hi: "तलघट्टपुरा" },
    line: "Green",
  },
  {
    id: "silkInstitute",
    names: {
      en: "Silk Institute",
      kn: "ಸಿಲ್ಕ್ ಇನ್‌ಸ್ಟಿಟ್ಯೂಟ್",
      hi: "सिल्क इंस्टीट्यूट",
    },
    line: "Green",
  },

  // Yellow Line
  {
    id: "ragigudda",
    names: { en: "Ragigudda", kn: "ರಾಗಿ ಗುಡ್ಡ", hi: "रागी गुड्डा" },
    line: "Yellow",
  },
  {
    id: "jayadevaHospital",
    names: {
      en: "Jayadeva Hospital",
      kn: "ಜಯದೇವ ಆಸ್ಪತ್ರೆ",
      hi: "जयदेव अस्पताल",
    },
    line: "Yellow",
  },
  {
    id: "btmLayout",
    names: { en: "BTM Layout", kn: "ಬಿಟಿಎಂ ಲೇಔಟ್", hi: "बीटीएम लेआउट" },
    line: "Yellow",
  },
  {
    id: "centralSilkBoard",
    names: {
      en: "Central Silk Board",
      kn: "ಸೆಂಟ್ರಲ್ ಸಿಲ್ಕ್ ಬೋರ್ಡ್",
      hi: "सेंट्रल सिल्क बोर्ड",
    },
    line: "Yellow",
  },
  {
    id: "bommanahalli",
    names: { en: "Bommanahalli", kn: "ಬೊಮ್ಮನಹಳ್ಳಿ", hi: "बोम्मनहल्ली" },
    line: "Yellow",
  },
  {
    id: "hongasandra",
    names: { en: "Hongasandra", kn: "ಹೊಂಗಸಂದ್ರ", hi: "होंगसंद्र" },
    line: "Yellow",
  },
  {
    id: "kudluGate",
    names: { en: "Kudlu Gate", kn: "ಕುಡ್ಲು ಗೇಟ್", hi: "कुड्लु गेट" },
    line: "Yellow",
  },
  {
    id: "singasandra",
    names: { en: "Singasandra", kn: "ಸಿಂಗಸಂದ್ರ", hi: "सिंगसंद्र" },
    line: "Yellow",
  },
  {
    id: "hosaRoad",
    names: { en: "Hosa Road", kn: "ಹೊಸ ರಸ್ತೆ", hi: "होसा रोड" },
    line: "Yellow",
  },
  {
    id: "beratenaAgrahara",
    names: {
      en: "Beratena Agrahara",
      kn: "ಬೆರಟೇನ ಅಗ್ರಹಾರ",
      hi: "बेरटेना अग्रहारा",
    },
    line: "Yellow",
  },
  {
    id: "electronicCity",
    names: {
      en: "Electronic City",
      kn: "ಎಲೆಕ್ಟ್ರಾನಿಕ್ ಸಿಟಿ",
      hi: "इलेक्ट्रॉनिक सिटी",
    },
    line: "Yellow",
  },
  {
    id: "konappanaAgrahara",
    names: {
      en: "Konappana Agrahara",
      kn: "ಕೊನಪ್ಪನ ಅಗ್ರಹಾರ",
      hi: "कोनप्पना अग्रहारा",
    },
    line: "Yellow",
  },
  {
    id: "huskurRoad",
    names: { en: "Huskur Road", kn: "ಹುಸ್ಕೂರು ರಸ್ತೆ", hi: "हुस्कुर रोड" },
    line: "Yellow",
  },
  {
    id: "hebbagodi",
    names: { en: "Hebbagodi", kn: "ಹೆಬ್ಬಗೋಡಿ", hi: "हेब्बागोडी" },
    line: "Yellow",
  },
  {
    id: "bommasandra",
    names: { en: "Bommasandra", kn: "ಬೊಮ್ಮಸಂದ್ರ", hi: "बोम्मसंद्र" },
    line: "Yellow",
  },
];

const C = {
  navy: "#102A43",
  blue: "#247BA0",
  green: "#15966A",
  red: "#D9534F",
  background: "#F3F7FA",
  white: "#FFFFFF",
  muted: "#627D98",
  border: "#D9E2EC",
  purpleLine: "#7C3AED",
  greenLine: "#15966A",
  yellowLine: "#D4A000",
};

export default function ExploreScreen() {
  const { language, t } = useLanguage();
  const lang = language as Language;

  const [originId, setOriginId] = useState("indiranagar");
  const [destinationId, setDestinationId] = useState("majestic");
  const [leaveMinutes, setLeaveMinutes] = useState(20);
  const [journeyPlanned, setJourneyPlanned] = useState(false);
  const [showAlternatives, setShowAlternatives] = useState(false);
  const [openDropdown, setOpenDropdown] = useState<
    "origin" | "destination" | null
  >(null);
  const [error, setError] = useState("");

  const stationName = (id: string) =>
    stations.find((station) => station.id === id)?.names[lang] ?? id;

  const lineColor = (line: Line) => {
    if (line === "Purple") return C.purpleLine;
    if (line === "Green") return C.greenLine;
    if (line === "Yellow") return C.yellowLine;
    return C.blue;
  };

  const planJourney = () => {
    if (originId === destinationId) {
      setError(t("sameStationError"));
      return;
    }
    setError("");
    setJourneyPlanned(true);
    setShowAlternatives(false);
  };

  const chooseStation = (id: string) => {
    if (openDropdown === "origin") setOriginId(id);
    if (openDropdown === "destination") setDestinationId(id);
    setOpenDropdown(null);
    setError("");
    setJourneyPlanned(false);
  };

  const renderStationDropdown = (kind: "origin" | "destination") => {
    const selectedId = kind === "origin" ? originId : destinationId;
    const isOpen = openDropdown === kind;
    const label = kind === "origin" ? t("from") : t("to");
    const selectedStation = stations.find(
      (station) => station.id === selectedId,
    );

    return (
      <View style={styles.dropdownBlock}>
        <Text style={styles.label}>{label}</Text>
        <Pressable
          style={styles.dropdownButton}
          onPress={() => setOpenDropdown(isOpen ? null : kind)}
        >
          <View style={styles.dropdownTextContainer}>
            <Text style={styles.dropdownSelected}>
              {stationName(selectedId)}
            </Text>
            <Text style={styles.dropdownHint}>
              {selectedStation?.line} Line
            </Text>
          </View>
          <Text style={styles.chevron}>{isOpen ? "▲" : "▼"}</Text>
        </Pressable>

        {isOpen && (
          <View style={styles.stationList}>
            <ScrollView nestedScrollEnabled style={styles.stationListScroll}>
              {stations.map((station) => (
                <Pressable
                  key={station.id}
                  style={[
                    styles.stationOption,
                    station.id === selectedId && styles.stationOptionSelected,
                  ]}
                  onPress={() => chooseStation(station.id)}
                >
                  <View
                    style={[
                      styles.lineDot,
                      { backgroundColor: lineColor(station.line) },
                    ]}
                  />
                  <View style={styles.stationOptionText}>
                    <Text style={styles.stationOptionName}>
                      {station.names[lang]}
                    </Text>
                    <Text style={styles.stationLineLabel}>
                      {station.line}
                      {station.line === "Interchange"
                        ? " · Interchange"
                        : ""}{" "}
                      Line
                    </Text>
                  </View>
                  {station.id === selectedId && (
                    <Text style={styles.checkMark}>✓</Text>
                  )}
                </Pressable>
              ))}
            </ScrollView>
          </View>
        )}
      </View>
    );
  };

  const estimate = Math.max(
    12,
    Math.abs(
      stations.findIndex((s) => s.id === destinationId) -
        stations.findIndex((s) => s.id === originId),
    ) *
      3 +
      8,
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView
        style={styles.screen}
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.header}>
          <Text style={styles.eyebrow}>NAMMAFLOW · BENGALURU</Text>
          <Text style={styles.title}>{t("journeyPlanner")}</Text>
          <Text style={styles.subtitle}>{t("chooseStationsDescription")}</Text>
        </View>

        {/* Map changes when the app language changes. */}
        <View style={styles.mapCard}>
          <Text style={styles.cardTitle}>
            {lang === "hi"
              ? "बेंगलुरु मेट्रो मानचित्र"
              : lang === "kn"
                ? "ಬೆಂಗಳೂರು ಮೆಟ್ರೋ ನಕ್ಷೆ"
                : "Bengaluru Metro Map"}
          </Text>
          <Text style={styles.cardSubtitle}>
            {lang === "hi"
              ? "नम्मा मेट्रो का मार्ग मानचित्र"
              : lang === "kn"
                ? "ನಮ್ಮ ಮೆಟ್ರೋ ಮಾರ್ಗ ನಕ್ಷೆ"
                : "Namma Metro schematic route map"}
          </Text>

          <View style={styles.officialMapContainer}>
            <Image
              source={lang === "kn" ? kannadaMap : englishMap}
              style={styles.officialMapImage}
              resizeMode="contain"
              accessibilityLabel={
                lang === "hi"
                  ? "बेंगलुरु मेट्रो मार्ग मानचित्र"
                  : lang === "kn"
                    ? "ನಮ್ಮ ಮೆಟ್ರೋ ಮಾರ್ಗ ನಕ್ಷೆ"
                    : "Bengaluru Metro schematic route map"
              }
              onError={(event) => {
                console.error(
                  "Metro map failed to load:",
                  event.nativeEvent.error,
                );
              }}
            />
          </View>

          <Pressable
            style={styles.mapButton}
            onPress={() =>
              Linking.openURL("https://english.bmrc.co.in/schematic-route-map/")
            }
          >
            <Text style={styles.mapButtonText}>
              {lang === "hi"
                ? "आधिकारिक मेट्रो नक्शा खोलें ↗"
                : lang === "kn"
                  ? "ಅಧಿಕೃತ ಮೆಟ್ರೋ ನಕ್ಷೆ ತೆರೆಯಿರಿ ↗"
                  : "Open Official BMRCL Map ↗"}
            </Text>
          </Pressable>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>{t("planYourJourney")}</Text>
          <Text style={styles.cardSubtitle}>
            {t("chooseStationsDescription")}
          </Text>

          {renderStationDropdown("origin")}

          <View style={styles.swapRow}>
            <View style={styles.swapDivider} />
            <Pressable
              style={styles.swapButton}
              onPress={() => {
                setOriginId(destinationId);
                setDestinationId(originId);
                setJourneyPlanned(false);
                setError("");
              }}
            >
              <Text style={styles.swapButtonText}>↕ Swap stations</Text>
            </Pressable>
            <View style={styles.swapDivider} />
          </View>

          {renderStationDropdown("destination")}

          {!!error && <Text style={styles.errorText}>{error}</Text>}

          <Pressable style={styles.primaryButton} onPress={planJourney}>
            <Text style={styles.primaryButtonText}>{t("planJourney")} →</Text>
          </Pressable>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>{t("whenToLeave")}</Text>
          <Text style={styles.cardSubtitle}>{t("departureOffsetHelp")}</Text>

          <View style={styles.departureControls}>
            <Pressable
              style={styles.stepButton}
              onPress={() => {
                setLeaveMinutes((v) => Math.max(0, v - 5));
                setJourneyPlanned(false);
              }}
            >
              <Text style={styles.stepButtonText}>−</Text>
            </Pressable>
            <View style={styles.departureValue}>
              <Text style={styles.departureNumber}>{leaveMinutes}</Text>
              <Text style={styles.departureUnit}>{t("minutesFromNow")}</Text>
            </View>
            <Pressable
              style={styles.stepButton}
              onPress={() => {
                setLeaveMinutes((v) => Math.min(180, v + 5));
                setJourneyPlanned(false);
              }}
            >
              <Text style={styles.stepButtonText}>+</Text>
            </Pressable>
          </View>

          <View style={styles.quickTimeRow}>
            {[0, 10, 20, 30, 45].map((minutes) => (
              <Pressable
                key={minutes}
                onPress={() => {
                  setLeaveMinutes(minutes);
                  setJourneyPlanned(false);
                }}
                style={[
                  styles.quickTimeButton,
                  leaveMinutes === minutes && styles.quickTimeButtonActive,
                ]}
              >
                <Text
                  style={[
                    styles.quickTimeText,
                    leaveMinutes === minutes && styles.quickTimeTextActive,
                  ]}
                >
                  {minutes === 0 ? t("leaveNow") : `${minutes} min`}
                </Text>
              </Pressable>
            ))}
          </View>
        </View>

        {journeyPlanned && (
          <View style={styles.resultCard}>
            <Text style={styles.resultEyebrow}>YOUR JOURNEY</Text>
            <Text style={styles.resultTitle}>{t("yourRoute")}</Text>

            <View style={styles.stationEndpoint}>
              <View
                style={[styles.endpointDot, { backgroundColor: C.green }]}
              />
              <View style={styles.endpointText}>
                <Text style={styles.endpointLabel}>{t("from")}</Text>
                <Text style={styles.endpointName}>{stationName(originId)}</Text>
              </View>
            </View>

            <View style={styles.verticalConnector} />

            <View style={styles.stationEndpoint}>
              <View style={[styles.endpointDot, { backgroundColor: C.red }]} />
              <View style={styles.endpointText}>
                <Text style={styles.endpointLabel}>{t("to")}</Text>
                <Text style={styles.endpointName}>
                  {stationName(destinationId)}
                </Text>
              </View>
            </View>

            <View style={styles.estimateRow}>
              <View style={styles.estimateBox}>
                <Text style={styles.estimateNumber}>{estimate}</Text>
                <Text style={styles.estimateLabel}>{t("minutes")}</Text>
              </View>
              <View style={styles.estimateBox}>
                <Text style={styles.estimateNumber}>
                  {leaveMinutes === 0 ? "Now" : `${leaveMinutes}m`}
                </Text>
                <Text style={styles.estimateLabel}>{t("whenToLeave")}</Text>
              </View>
            </View>

            <Text style={styles.demoNotice}>{t("estimatedDemoFootnote")}</Text>

            <Pressable
              style={styles.secondaryButton}
              onPress={() => setShowAlternatives((v) => !v)}
            >
              <Text style={styles.secondaryButtonText}>
                {showAlternatives ? t("hideAlternatives") : t("compareRoutes")}
              </Text>
            </Pressable>

            {showAlternatives && (
              <View style={styles.alternatives}>
                <View style={styles.alternativeItem}>
                  <View
                    style={[
                      styles.alternativeStripe,
                      { backgroundColor: C.purpleLine },
                    ]}
                  />
                  <View style={styles.alternativeText}>
                    <Text style={styles.alternativeTitle}>
                      {t("alternative1")}
                    </Text>
                    <Text style={styles.alternativeDescription}>
                      {stationName(originId)} → Majestic →{" "}
                      {stationName(destinationId)}
                    </Text>
                  </View>
                </View>
                <View style={styles.alternativeItem}>
                  <View
                    style={[
                      styles.alternativeStripe,
                      { backgroundColor: C.greenLine },
                    ]}
                  />
                  <View style={styles.alternativeText}>
                    <Text style={styles.alternativeTitle}>
                      {t("alternative2")}
                    </Text>
                    <Text style={styles.alternativeDescription}>
                      Check connections through Cubbon Park or RV Road.
                    </Text>
                  </View>
                </View>
                <Text style={styles.demoNotice}>{t("verifyConnections")}</Text>
              </View>
            )}
          </View>
        )}

        <View style={styles.footerNote}>
          <Text style={styles.footerNoteText}>{t("prototypeNotice")}</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: C.background },
  screen: { flex: 1 },
  content: { padding: 18, paddingBottom: 36, gap: 16 },
  header: { paddingTop: 8, paddingBottom: 4 },
  eyebrow: {
    color: C.blue,
    fontSize: 11,
    fontWeight: "800",
    letterSpacing: 1.5,
    marginBottom: 7,
  },
  title: { color: C.navy, fontSize: 28, fontWeight: "800" },
  subtitle: { color: C.muted, fontSize: 14, lineHeight: 20, marginTop: 6 },
  card: {
    backgroundColor: C.white,
    borderRadius: 20,
    padding: 18,
    borderWidth: 1,
    borderColor: C.border,
  },
  mapCard: {
    backgroundColor: C.white,
    borderRadius: 20,
    padding: 18,
    borderWidth: 1,
    borderColor: C.border,
  },
  cardTitle: { color: C.navy, fontSize: 18, fontWeight: "800" },
  cardSubtitle: { color: C.muted, fontSize: 13, lineHeight: 19, marginTop: 5 },
  officialMapContainer: {
    marginTop: 16,
    width: "100%",
    height: 480,
    backgroundColor: C.white,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: C.border,
    overflow: "hidden",
    alignItems: "center",
    justifyContent: "center",
  },
  officialMapImage: { width: "100%", height: "100%" },
  mapButton: {
    backgroundColor: C.navy,
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: "center",
    marginTop: 14,
  },
  mapButtonText: { color: C.white, fontWeight: "800", fontSize: 13 },
  dropdownBlock: { marginTop: 16 },
  label: {
    color: C.muted,
    fontSize: 12,
    fontWeight: "800",
    marginBottom: 8,
    textTransform: "uppercase",
    letterSpacing: 0.6,
  },
  dropdownButton: {
    borderWidth: 1,
    borderColor: C.border,
    borderRadius: 13,
    minHeight: 64,
    paddingHorizontal: 14,
    paddingVertical: 12,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    backgroundColor: C.white,
  },
  dropdownTextContainer: { flex: 1, paddingRight: 10 },
  dropdownSelected: { color: C.navy, fontSize: 15, fontWeight: "700" },
  dropdownHint: { color: C.muted, fontSize: 11, marginTop: 4 },
  chevron: { color: C.blue, fontSize: 15, fontWeight: "800" },
  stationList: {
    marginTop: 7,
    borderWidth: 1,
    borderColor: C.border,
    borderRadius: 13,
    overflow: "hidden",
    backgroundColor: C.white,
  },
  stationListScroll: { maxHeight: 270 },
  stationOption: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 11,
    paddingHorizontal: 12,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: C.border,
    gap: 10,
  },
  stationOptionSelected: { backgroundColor: "#EAF4FB" },
  lineDot: { width: 10, height: 10, borderRadius: 5 },
  stationOptionText: { flex: 1 },
  stationOptionName: { color: C.navy, fontSize: 13, fontWeight: "700" },
  stationLineLabel: { color: C.muted, fontSize: 11, marginTop: 3 },
  checkMark: { color: C.green, fontWeight: "900", fontSize: 17 },
  swapRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    marginTop: 13,
  },
  swapDivider: { height: 1, backgroundColor: C.border, flex: 1 },
  swapButton: {
    borderRadius: 20,
    backgroundColor: "#EAF4FB",
    paddingVertical: 8,
    paddingHorizontal: 12,
  },
  swapButtonText: { color: C.blue, fontWeight: "800", fontSize: 12 },
  primaryButton: {
    backgroundColor: C.blue,
    borderRadius: 13,
    alignItems: "center",
    paddingVertical: 15,
    marginTop: 18,
  },
  primaryButtonText: { color: C.white, fontSize: 15, fontWeight: "800" },
  errorText: { color: C.red, marginTop: 10, fontSize: 13, fontWeight: "700" },
  departureControls: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 24,
    marginTop: 18,
  },
  stepButton: {
    width: 46,
    height: 46,
    borderRadius: 15,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#EAF4FB",
  },
  stepButtonText: { color: C.blue, fontSize: 25, fontWeight: "700" },
  departureValue: { alignItems: "center", minWidth: 110 },
  departureNumber: { color: C.navy, fontSize: 36, fontWeight: "900" },
  departureUnit: { color: C.muted, fontSize: 12, marginTop: 2 },
  quickTimeRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginTop: 18,
  },
  quickTimeButton: {
    borderRadius: 10,
    borderWidth: 1,
    borderColor: C.border,
    paddingVertical: 9,
    paddingHorizontal: 12,
    backgroundColor: C.white,
  },
  quickTimeButtonActive: { backgroundColor: C.blue, borderColor: C.blue },
  quickTimeText: { color: C.navy, fontSize: 12, fontWeight: "700" },
  quickTimeTextActive: { color: C.white },
  resultCard: {
    backgroundColor: C.white,
    borderRadius: 20,
    padding: 18,
    borderWidth: 1,
    borderColor: C.border,
  },
  resultEyebrow: {
    color: C.green,
    fontSize: 11,
    letterSpacing: 1.2,
    fontWeight: "900",
  },
  resultTitle: {
    color: C.navy,
    fontSize: 20,
    fontWeight: "900",
    marginTop: 6,
    marginBottom: 18,
  },
  stationEndpoint: { flexDirection: "row", alignItems: "center", gap: 12 },
  endpointDot: { width: 12, height: 12, borderRadius: 6 },
  endpointText: { flex: 1 },
  endpointLabel: { color: C.muted, fontSize: 11, fontWeight: "700" },
  endpointName: {
    color: C.navy,
    fontSize: 15,
    fontWeight: "800",
    marginTop: 3,
  },
  verticalConnector: {
    width: 2,
    height: 22,
    backgroundColor: C.border,
    marginLeft: 5,
    marginVertical: 3,
  },
  estimateRow: { flexDirection: "row", gap: 10, marginTop: 20 },
  estimateBox: {
    flex: 1,
    backgroundColor: C.background,
    borderRadius: 13,
    padding: 13,
  },
  estimateNumber: { color: C.navy, fontSize: 22, fontWeight: "900" },
  estimateLabel: { color: C.muted, fontSize: 11, marginTop: 4 },
  demoNotice: { color: C.muted, fontSize: 11, lineHeight: 16, marginTop: 14 },
  secondaryButton: {
    borderWidth: 1,
    borderColor: C.blue,
    borderRadius: 12,
    paddingVertical: 13,
    alignItems: "center",
    marginTop: 16,
  },
  secondaryButtonText: { color: C.blue, fontWeight: "800", fontSize: 13 },
  alternatives: { marginTop: 14, gap: 12 },
  alternativeItem: {
    flexDirection: "row",
    gap: 10,
    borderRadius: 12,
    backgroundColor: "#F6F9FC",
    padding: 12,
  },
  alternativeStripe: { width: 4, borderRadius: 4 },
  alternativeText: { flex: 1 },
  alternativeTitle: { color: C.navy, fontSize: 13, fontWeight: "800" },
  alternativeDescription: {
    color: C.muted,
    fontSize: 12,
    lineHeight: 17,
    marginTop: 4,
  },
  footerNote: { paddingHorizontal: 4, paddingVertical: 4 },
  footerNoteText: {
    color: C.muted,
    fontSize: 11,
    lineHeight: 16,
    textAlign: "center",
  },
});
