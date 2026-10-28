import { Tabs } from "expo-router";
import { LanguageProvider } from "@/constants/LanguageContext";

export default function TabLayout() {
  return (
    <LanguageProvider>
      <Tabs screenOptions={{ headerShown: false }}>
        <Tabs.Screen name="index" options={{ title: "Home" }} />
        <Tabs.Screen name="explore" options={{ title: "Routes" }} />
        <Tabs.Screen name="coaches" options={{ title: "Coaches" }} />
        <Tabs.Screen name="settings" options={{ title: "Settings" }} />
      </Tabs>
    </LanguageProvider>
  );
}
