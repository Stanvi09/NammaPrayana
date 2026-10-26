import { useLanguage } from "@/constants/LanguageContext";
import { useRouter } from "expo-router";
import {
  Pressable,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

const COLORS = {
  background: "#F4F7FB",
  navy: "#142B4A",
  blue: "#2864E8",
  green: "#16845B",
  red: "#D84A4A",
  muted: "#738198",
  white: "#FFFFFF",
  border: "#E5EAF2",
};

const coaches = [
  { id: 1, occupancy: 85 },
  { id: 2, occupancy: 25 },
  { id: 3, occupancy: 55 },
];

type CoachKey = "coach1" | "coach2" | "coach3";

export default function HomeScreen() {
  const router = useRouter();
  const { t } = useLanguage();

  function crowdLabel(occupancy: number) {
    if (occupancy < 35) return t("low");
    if (occupancy < 70) return t("medium");
    return t("high");
  }

  function crowdColor(occupancy: number) {
    if (occupancy < 35) return COLORS.green;
    if (occupancy < 70) return "#E9A126";
    return COLORS.red;
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.content}
      >
        <View style={styles.header}>
          <View style={styles.headerText}>
            <Text style={styles.eyebrow}>{t("tagline").toUpperCase()}</Text>
            <Text style={styles.logo}>
              Namma<Text style={styles.logoBlue}>Flow</Text>
            </Text>
            <Text style={styles.subtitle}>{t("tagline")}</Text>
          </View>

          <Pressable
            accessibilityRole="button"
            style={styles.languageButton}
            onPress={() => router.push("/settings")}
          >
            <Text style={styles.languageText}>文 {t("chooseLanguage")}</Text>
          </Pressable>
        </View>

        <View style={styles.sectionHeading}>
          <Text style={styles.sectionTitle}>{t("yourJourney")}</Text>
          <View style={styles.liveBadge}>
            <View style={styles.liveDot} />
            <Text style={styles.liveText}>{t("demoLabel").toUpperCase()}</Text>
          </View>
        </View>

        <View style={styles.delayCard}>
          <View style={styles.cardTop}>
            <View style={styles.stationInfo}>
              <Text style={styles.whiteMuted}>
                {t("nextTrain")} · {t("towardsMajestic")}
              </Text>
              <Text style={styles.station}>{t("kempegowda")}</Text>
              <Text style={styles.whiteMuted}>{t("interchangeStation")}</Text>
            </View>

            <View style={styles.trainIcon}>
              <Text style={styles.trainEmoji}>🚇</Text>
            </View>
          </View>

          <View style={styles.cardDivider} />

          <View style={styles.delayRow}>
            <View>
              <Text style={styles.whiteMuted}>{t("predictedDelay")}</Text>
              <Text style={styles.delayNumber}>
                6–9 <Text style={styles.delayUnit}>{t("minutes")}</Text>
              </Text>
            </View>

            <View style={styles.delayTag}>
              <Text style={styles.delayTagText}>⚠ {t("delayed")}</Text>
            </View>
          </View>

          <Text style={styles.cardFootnote}>{t("estimatedDemoFootnote")}</Text>
        </View>

        <Text style={styles.sectionTitle}>{t("yourNextMove")}</Text>

        <Pressable
          style={styles.leaveCard}
          onPress={() => router.push("/explore")}
        >
          <View style={styles.iconCircleGreen}>
            <Text style={styles.actionEmoji}>◷</Text>
          </View>

          <View style={styles.actionContent}>
            <Text style={styles.actionTitle}>{t("leaveNow")}</Text>
            <Text style={styles.actionDescription}>
              {t("leaveNowAssistant")}
            </Text>
            <Text style={styles.greenText}>{t("checkRoute")} →</Text>
          </View>
        </Pressable>

        <View style={styles.connectionCard}>
          <View style={styles.connectionHeader}>
            <Text style={styles.connectionIcon}>⚡</Text>
            <Text style={styles.actionTitle}>{t("connectionSaver")}</Text>
            <View style={styles.riskBadge}>
              <Text style={styles.riskText}>
                {t("connectionRiskMessage").toUpperCase()}
              </Text>
            </View>
          </View>

          <Text style={styles.actionDescription}>
            {t("connectionRiskMessage")}
          </Text>

          <Pressable
            style={styles.routeButton}
            onPress={() => router.push("/explore")}
          >
            <Text style={styles.routeButtonText}>{t("alternative1")} →</Text>
          </Pressable>
        </View>

        <View style={styles.coachHeading}>
          <View style={styles.coachHeadingText}>
            <Text style={styles.sectionTitle}>{t("bestCoach")}</Text>
            <Text style={styles.mutedSmall}>{t("leastCrowded")}</Text>
          </View>

          <Text style={styles.simulated}>{t("demo").toUpperCase()}</Text>
        </View>

        <View style={styles.coachList}>
          {coaches.map((coach) => {
            const color = crowdColor(coach.occupancy);
            const coachKey = `coach${coach.id}` as CoachKey;
            const isBest = coach.occupancy === 25;

            return (
              <View key={coach.id} style={styles.coachCard}>
                <View style={styles.coachIcon}>
                  <Text style={styles.coachEmoji}>🚆</Text>
                </View>

                <View style={styles.coachInfo}>
                  <Text style={styles.coachName}>{t(coachKey)}</Text>
                  <Text style={styles.mutedSmall}>
                    {crowdLabel(coach.occupancy)}
                  </Text>
                </View>

                <View style={styles.coachRight}>
                  <Text style={[styles.coachPercent, { color }]}>
                    {coach.occupancy}%
                  </Text>
                  <View style={styles.miniTrack}>
                    <View
                      style={[
                        styles.miniFill,
                        {
                          width: `${coach.occupancy}%`,
                          backgroundColor: color,
                        },
                      ]}
                    />
                  </View>
                </View>

                {isBest && (
                  <View style={styles.bestBadge}>
                    <Text style={styles.bestText}>
                      {t("recommendedCoach").toUpperCase()}
                    </Text>
                  </View>
                )}
              </View>
            );
          })}
        </View>

        <Pressable
          style={styles.viewCoachesButton}
          onPress={() => router.push("/coaches")}
        >
          <Text style={styles.viewCoachesText}>{t("viewCoaches")} →</Text>
        </Pressable>

        <Text style={styles.disclaimer}>{t("prototypeNotice")}</Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  content: {
    paddingHorizontal: 20,
    paddingTop: 12,
    paddingBottom: 25,
    gap: 15,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 5,
    gap: 10,
  },
  headerText: {
    flex: 1,
  },
  eyebrow: {
    fontSize: 9,
    letterSpacing: 1.5,
    color: COLORS.muted,
    fontWeight: "700",
  },
  logo: {
    fontSize: 29,
    fontWeight: "800",
    color: COLORS.navy,
    marginTop: 5,
  },
  logoBlue: {
    color: COLORS.blue,
  },
  subtitle: {
    color: COLORS.muted,
    fontSize: 12,
    marginTop: 2,
  },
  languageButton: {
    backgroundColor: COLORS.white,
    paddingHorizontal: 13,
    paddingVertical: 10,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  languageText: {
    fontWeight: "700",
    color: COLORS.navy,
    fontSize: 12,
  },
  sectionHeading: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 8,
  },
  sectionTitle: {
    color: COLORS.navy,
    fontSize: 18,
    fontWeight: "800",
  },
  liveBadge: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#DDF5E8",
    paddingHorizontal: 9,
    paddingVertical: 6,
    borderRadius: 20,
    gap: 5,
  },
  liveDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: COLORS.green,
  },
  liveText: {
    fontSize: 9,
    color: COLORS.green,
    fontWeight: "800",
  },
  delayCard: {
    backgroundColor: COLORS.navy,
    borderRadius: 23,
    padding: 21,
    marginBottom: 7,
  },
  cardTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 10,
  },
  stationInfo: {
    flex: 1,
  },
  whiteMuted: {
    color: "#BAC9DE",
    fontSize: 10,
    letterSpacing: 0.5,
    lineHeight: 18,
  },
  station: {
    color: COLORS.white,
    fontSize: 27,
    fontWeight: "800",
    marginVertical: 5,
  },
  trainIcon: {
    backgroundColor: "#FFFFFF1A",
    borderRadius: 17,
    width: 55,
    height: 55,
    alignItems: "center",
    justifyContent: "center",
  },
  trainEmoji: {
    fontSize: 29,
  },
  cardDivider: {
    height: 1,
    backgroundColor: "#FFFFFF25",
    marginVertical: 18,
  },
  delayRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 8,
  },
  delayNumber: {
    color: COLORS.white,
    fontSize: 38,
    fontWeight: "800",
    marginTop: 3,
  },
  delayUnit: {
    fontSize: 16,
    fontWeight: "500",
  },
  delayTag: {
    backgroundColor: "#4D3540",
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 10,
  },
  delayTagText: {
    color: "#FFB9B9",
    fontSize: 11,
    fontWeight: "700",
  },
  cardFootnote: {
    color: "#BAC9DE",
    fontSize: 10,
    lineHeight: 16,
    marginTop: 15,
  },
  leaveCard: {
    flexDirection: "row",
    gap: 13,
    padding: 16,
    backgroundColor: COLORS.white,
    borderRadius: 19,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  iconCircleGreen: {
    width: 43,
    height: 43,
    borderRadius: 14,
    backgroundColor: "#DDF5E8",
    alignItems: "center",
    justifyContent: "center",
  },
  actionEmoji: {
    fontSize: 25,
    color: COLORS.green,
  },
  actionContent: {
    flex: 1,
    gap: 6,
  },
  actionTitle: {
    fontSize: 15,
    fontWeight: "800",
    color: COLORS.navy,
    flexShrink: 1,
  },
  actionDescription: {
    fontSize: 12,
    lineHeight: 19,
    color: COLORS.muted,
  },
  greenText: {
    color: COLORS.green,
    fontSize: 12,
    fontWeight: "800",
    marginTop: 2,
  },
  connectionCard: {
    backgroundColor: "#FFF8F5",
    borderColor: "#F4DAD0",
    borderWidth: 1,
    borderRadius: 19,
    padding: 16,
    gap: 11,
  },
  connectionHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  connectionIcon: {
    fontSize: 20,
  },
  riskBadge: {
    backgroundColor: "#FCE4DE",
    paddingHorizontal: 8,
    paddingVertical: 5,
    borderRadius: 7,
    marginLeft: "auto",
    flexShrink: 1,
  },
  riskText: {
    fontSize: 9,
    color: COLORS.red,
    fontWeight: "800",
  },
  routeButton: {
    backgroundColor: COLORS.navy,
    padding: 12,
    borderRadius: 11,
    alignItems: "center",
    marginTop: 2,
  },
  routeButtonText: {
    color: COLORS.white,
    fontSize: 12,
    fontWeight: "700",
    textAlign: "center",
  },
  coachHeading: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: 4,
    gap: 8,
  },
  coachHeadingText: {
    flex: 1,
  },
  mutedSmall: {
    fontSize: 11,
    color: COLORS.muted,
    marginTop: 4,
  },
  simulated: {
    fontSize: 8,
    letterSpacing: 0.7,
    color: COLORS.muted,
    fontWeight: "800",
  },
  coachList: {
    gap: 9,
  },
  coachCard: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    backgroundColor: COLORS.white,
    padding: 11,
    borderRadius: 15,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  coachIcon: {
    width: 39,
    height: 39,
    borderRadius: 12,
    backgroundColor: "#EAF0FF",
    alignItems: "center",
    justifyContent: "center",
  },
  coachEmoji: {
    fontSize: 20,
  },
  coachInfo: {
    flex: 1,
  },
  coachName: {
    color: COLORS.navy,
    fontSize: 12,
    fontWeight: "800",
  },
  coachRight: {
    width: 55,
    gap: 5,
  },
  coachPercent: {
    fontSize: 11,
    fontWeight: "800",
    textAlign: "right",
  },
  miniTrack: {
    height: 5,
    borderRadius: 4,
    backgroundColor: "#EDF0F5",
    overflow: "hidden",
  },
  miniFill: {
    height: 5,
    borderRadius: 4,
  },
  bestBadge: {
    backgroundColor: "#DDF5E8",
    paddingHorizontal: 6,
    paddingVertical: 5,
    borderRadius: 6,
  },
  bestText: {
    color: COLORS.green,
    fontSize: 8,
    fontWeight: "800",
  },
  viewCoachesButton: {
    alignItems: "center",
    padding: 13,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.white,
  },
  viewCoachesText: {
    color: COLORS.blue,
    fontWeight: "700",
    fontSize: 12,
  },
  disclaimer: {
    color: COLORS.muted,
    fontSize: 10,
    lineHeight: 16,
    textAlign: "center",
    marginVertical: 5,
  },
});
