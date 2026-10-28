import { useLanguage } from "@/constants/LanguageContext";
import { useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

const coaches = [
  { id: 1, occupancy: 85, people: 34, capacity: 40 },
  { id: 2, occupancy: 25, people: 10, capacity: 40 },
  { id: 3, occupancy: 55, people: 22, capacity: 40 },
  { id: 4, occupancy: 40, people: 16, capacity: 40 },
];

type CoachTranslationKey = "coach1" | "coach2" | "coach3" | "coach4";

function getCoachTranslationKey(id: number): CoachTranslationKey {
  return `coach${id}` as CoachTranslationKey;
}

function crowdColor(occupancy: number) {
  if (occupancy < 35) return "#16845B";
  if (occupancy < 70) return "#D18A16";
  return "#D84A4A";
}

export default function CoachesScreen() {
  const { t } = useLanguage();
  const [selectedCoach, setSelectedCoach] = useState<number | null>(null);

  const bestCoach = coaches.reduce((best, coach) =>
    coach.occupancy < best.occupancy ? coach : best,
  );

  function crowdLabel(occupancy: number) {
    if (occupancy < 35) return t("low");
    if (occupancy < 70) return t("medium");
    return t("high");
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.eyebrow}>
          {t("appName").toUpperCase()} · {t("coachDemo").toUpperCase()}
        </Text>

        <Text style={styles.title}>{t("selectCoach")}</Text>

        <Text style={styles.subtitle}>{t("leastCrowded")}</Text>

        <View style={styles.notice}>
          <Text style={styles.noticeTitle}>{t("demoLabel")}</Text>
          <Text style={styles.noticeText}>{t("estimatedDemoFootnote")}</Text>
        </View>

        <View style={styles.recommendation}>
          <Text style={styles.recommendationLabel}>
            {t("recommendedCoach").toUpperCase()}
          </Text>

          <Text style={styles.recommendationName}>
            {t(getCoachTranslationKey(bestCoach.id))}
          </Text>

          <Text style={styles.recommendationDetail}>
            {bestCoach.occupancy}% {t("occupancy")} · {bestCoach.people}/
            {bestCoach.capacity}
          </Text>

          <View style={styles.recommendationBadge}>
            <Text style={styles.recommendationBadgeText}>
              {t("leastCrowded").toUpperCase()}
            </Text>
          </View>
        </View>

        <Text style={styles.sectionTitle}>{t("crowdLevel")}</Text>

        {coaches.map((coach) => {
          const color = crowdColor(coach.occupancy);
          const isBest = coach.id === bestCoach.id;
          const isSelected = selectedCoach === coach.id;
          const coachName = t(getCoachTranslationKey(coach.id));

          return (
            <Pressable
              key={coach.id}
              accessibilityRole="button"
              accessibilityState={{ selected: isSelected }}
              onPress={() => setSelectedCoach(coach.id)}
              style={[styles.coachCard, isSelected && styles.selectedCard]}
            >
              <View style={styles.coachTop}>
                <View style={styles.trainIcon}>
                  <Text style={styles.trainEmoji}>🚇</Text>
                </View>

                <View style={styles.coachDetails}>
                  <Text style={styles.coachName}>{coachName}</Text>
                  <Text style={styles.peopleText}>
                    {coach.people} / {coach.capacity}
                  </Text>
                </View>

                <View style={styles.rightSide}>
                  <Text style={[styles.percent, { color }]}>
                    {coach.occupancy}%
                  </Text>

                  <Text style={[styles.crowdLabel, { color }]}>
                    {crowdLabel(coach.occupancy)}
                  </Text>
                </View>
              </View>

              <View
                style={styles.track}
                accessibilityLabel={`${coachName}: ${coach.occupancy}%`}
              >
                <View
                  style={[
                    styles.fill,
                    {
                      width: `${coach.occupancy}%`,
                      backgroundColor: color,
                    },
                  ]}
                />
              </View>

              {isBest && (
                <Text style={styles.bestLabel}>
                  ✓ {t("recommendedCoach")} — {t("leastCrowded")}
                </Text>
              )}

              {isSelected && (
                <Text style={styles.selectedLabel}>{t("selectedCoach")}</Text>
              )}
            </Pressable>
          );
        })}

        <Text style={styles.footer}>{t("estimatedDemoFootnote")}</Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: "#F4F7FB",
  },
  content: {
    padding: 20,
    paddingBottom: 35,
  },
  eyebrow: {
    color: "#2864E8",
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 1.5,
  },
  title: {
    color: "#142B4A",
    fontSize: 27,
    fontWeight: "800",
    marginTop: 10,
  },
  subtitle: {
    color: "#738198",
    fontSize: 13,
    lineHeight: 20,
    marginTop: 7,
  },
  notice: {
    backgroundColor: "#FFF0D4",
    borderRadius: 12,
    padding: 13,
    marginTop: 20,
  },
  noticeTitle: {
    color: "#88570C",
    fontSize: 12,
    fontWeight: "800",
  },
  noticeText: {
    color: "#88570C",
    fontSize: 11,
    lineHeight: 17,
    marginTop: 4,
  },
  recommendation: {
    backgroundColor: "#142B4A",
    borderRadius: 20,
    padding: 20,
    marginTop: 18,
    marginBottom: 25,
  },
  recommendationLabel: {
    color: "#BAC9DE",
    fontSize: 10,
    fontWeight: "700",
    letterSpacing: 1,
  },
  recommendationName: {
    color: "#FFFFFF",
    fontSize: 29,
    fontWeight: "800",
    marginTop: 9,
  },
  recommendationDetail: {
    color: "#D4DEEC",
    fontSize: 12,
    marginTop: 6,
  },
  recommendationBadge: {
    alignSelf: "flex-start",
    backgroundColor: "#DDF5E8",
    paddingHorizontal: 10,
    paddingVertical: 7,
    borderRadius: 8,
    marginTop: 14,
  },
  recommendationBadgeText: {
    color: "#16845B",
    fontSize: 9,
    fontWeight: "800",
  },
  sectionTitle: {
    color: "#142B4A",
    fontSize: 18,
    fontWeight: "800",
    marginBottom: 12,
  },
  coachCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 17,
    padding: 15,
    borderWidth: 1,
    borderColor: "#E5EAF2",
    marginBottom: 11,
  },
  selectedCard: {
    borderColor: "#2864E8",
    borderWidth: 2,
  },
  coachTop: {
    flexDirection: "row",
    alignItems: "center",
    gap: 11,
  },
  trainIcon: {
    width: 43,
    height: 43,
    borderRadius: 13,
    backgroundColor: "#EAF0FF",
    alignItems: "center",
    justifyContent: "center",
  },
  trainEmoji: {
    fontSize: 22,
  },
  coachDetails: {
    flex: 1,
  },
  coachName: {
    color: "#142B4A",
    fontSize: 14,
    fontWeight: "800",
  },
  peopleText: {
    color: "#738198",
    fontSize: 11,
    marginTop: 5,
  },
  rightSide: {
    alignItems: "flex-end",
  },
  percent: {
    fontSize: 17,
    fontWeight: "800",
  },
  crowdLabel: {
    fontSize: 11,
    fontWeight: "700",
    marginTop: 3,
  },
  track: {
    height: 7,
    borderRadius: 5,
    backgroundColor: "#EDF0F5",
    overflow: "hidden",
    marginTop: 15,
  },
  fill: {
    height: 7,
    borderRadius: 5,
  },
  bestLabel: {
    color: "#16845B",
    fontSize: 10,
    fontWeight: "700",
    marginTop: 10,
  },
  selectedLabel: {
    color: "#2864E8",
    fontSize: 10,
    fontWeight: "700",
    marginTop: 7,
  },
  footer: {
    color: "#738198",
    fontSize: 10,
    lineHeight: 16,
    textAlign: "center",
    marginTop: 15,
  },
});
