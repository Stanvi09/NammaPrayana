import AsyncStorage from "@react-native-async-storage/async-storage";
import * as Speech from "expo-speech";
import { useEffect, useState } from "react";
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { useLanguage } from "@/constants/LanguageContext";
import type { AppLanguage } from "@/constants/i18n";

const languageOptions: {
  code: AppLanguage;
  nativeName: string;
}[] = [
  { code: "en", nativeName: "English" },
  { code: "kn", nativeName: "ಕನ್ನಡ" },
  { code: "hi", nativeName: "हिन्दी" },
];

export default function SettingsScreen() {
  const { language, setLanguage, t, ready } = useLanguage();
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [preferencesReady, setPreferencesReady] = useState(false);

  useEffect(() => {
    let active = true;

    AsyncStorage.getItem("@nammaflow/voice-alerts")
      .then((saved) => {
        if (!active) return;
        if (saved === "true") setVoiceEnabled(true);
        if (saved === "false") setVoiceEnabled(false);
      })
      .catch((error) => {
        console.warn("Could not load voice setting:", error);
      })
      .finally(() => {
        if (active) setPreferencesReady(true);
      });

    return () => {
      active = false;
    };
  }, []);

  const toggleVoice = (value: boolean) => {
    setVoiceEnabled(value);

    AsyncStorage.setItem("@nammaflow/voice-alerts", String(value)).catch(
      (error) => console.warn("Could not save voice setting:", error),
    );

    if (!value) Speech.stop();
  };

  const testVoice = async () => {
    if (!voiceEnabled) return;

    await Speech.stop();

    const messages: Record<AppLanguage, string> = {
      en: "Welcome to NammaFlow. Have a smooth journey.",
      kn: "ನಮ್ಮಫ್ಲೋಗೆ ಸ್ವಾಗತ. ನಿಮ್ಮ ಪ್ರಯಾಣ ಸುಗಮವಾಗಿರಲಿ.",
      hi: "नम्माफ्लो में आपका स्वागत है। आपकी यात्रा शुभ हो।",
    };

    const speechLanguages: Record<AppLanguage, string> = {
      en: "en-IN",
      kn: "kn-IN",
      hi: "hi-IN",
    };

    Speech.speak(messages[language], {
      language: speechLanguages[language],
      rate: 0.9,
    });
  };

  if (!ready || !preferencesReady) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.loading}>
          <Text style={styles.loadingText}>{t("appName")}...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.eyebrow}>NAMMAFLOW</Text>

        <Text style={styles.title}>{t("settings")}</Text>
        <Text style={styles.subtitle}>{t("languageDescription")}</Text>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>{t("appLanguage")}</Text>

          {languageOptions.map((option) => (
            <Pressable
              key={option.code}
              accessibilityRole="button"
              accessibilityState={{ selected: language === option.code }}
              onPress={() => setLanguage(option.code)}
              style={[
                styles.languageOption,
                language === option.code && styles.selectedLanguage,
              ]}
            >
              <View style={styles.optionCopy}>
                <Text style={styles.optionText}>{option.nativeName}</Text>
                <Text style={styles.description}>
                  {option.code === "en"
                    ? t("english")
                    : option.code === "kn"
                      ? t("kannada")
                      : t("hindi")}
                </Text>
              </View>

              <Text style={styles.check}>
                {language === option.code ? "✓" : ""}
              </Text>
            </Pressable>
          ))}
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>{t("voiceAlerts")}</Text>

          <View style={styles.settingRow}>
            <View style={styles.settingCopy}>
              <Text style={styles.optionText}>{t("voiceAlerts")}</Text>
              <Text style={styles.description}>{t("voiceDescription")}</Text>
            </View>

            <Switch
              value={voiceEnabled}
              onValueChange={toggleVoice}
              accessibilityLabel={t("voiceAlerts")}
            />
          </View>

          <Pressable
            style={[
              styles.primaryButton,
              !voiceEnabled && styles.disabledButton,
            ]}
            onPress={testVoice}
            disabled={!voiceEnabled}
            accessibilityRole="button"
          >
            <Text style={styles.primaryButtonText}>🔊 {t("testVoice")}</Text>
          </Pressable>
        </View>

        <View style={styles.aboutCard}>
          <Text style={styles.aboutTitle}>{t("appName")}</Text>
          <Text style={styles.aboutText}>{t("prototypeNotice")}</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: "#F4F7FB" },
  content: { padding: 20, paddingBottom: 35, gap: 16 },
  loading: { flex: 1, alignItems: "center", justifyContent: "center" },
  loadingText: { color: "#142B4A", fontSize: 14 },
  eyebrow: {
    color: "#2864E8",
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 2,
  },
  title: {
    color: "#142B4A",
    fontSize: 30,
    fontWeight: "800",
    marginTop: 2,
  },
  subtitle: {
    color: "#738198",
    fontSize: 13,
    lineHeight: 20,
    marginTop: -9,
  },
  card: {
    backgroundColor: "#FFFFFF",
    padding: 17,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: "#E5EAF2",
    gap: 13,
  },
  sectionTitle: {
    color: "#142B4A",
    fontSize: 16,
    fontWeight: "800",
    marginBottom: 2,
  },
  languageOption: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    padding: 12,
    borderRadius: 11,
    backgroundColor: "#F7F9FC",
  },
  selectedLanguage: {
    backgroundColor: "#EAF0FF",
    borderWidth: 1,
    borderColor: "#2864E8",
  },
  optionCopy: { flex: 1 },
  optionText: { color: "#142B4A", fontSize: 14, fontWeight: "600" },
  check: {
    color: "#2864E8",
    fontSize: 18,
    fontWeight: "800",
    marginLeft: 10,
  },
  settingRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 10,
  },
  settingCopy: { flex: 1, gap: 5 },
  description: { color: "#738198", fontSize: 12, lineHeight: 18 },
  primaryButton: {
    backgroundColor: "#142B4A",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 5,
  },
  disabledButton: { opacity: 0.5 },
  primaryButtonText: {
    color: "#FFFFFF",
    fontSize: 13,
    fontWeight: "700",
  },
  aboutCard: {
    backgroundColor: "#EAF0FF",
    padding: 17,
    borderRadius: 16,
    gap: 7,
  },
  aboutTitle: { color: "#142B4A", fontWeight: "800", fontSize: 14 },
  aboutText: { color: "#526783", fontSize: 12, lineHeight: 19 },
});
