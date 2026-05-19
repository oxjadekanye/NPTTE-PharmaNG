import { useState } from "react";
import { Pressable, StyleSheet, Text, TextInput, View, type TextInputProps } from "react-native";
import { NPTTEBrand } from "@/theme/branding";

type Props = TextInputProps & {
  containerStyle?: object;
};

export function PasswordInput({ containerStyle, style, ...props }: Props) {
  const [visible, setVisible] = useState(false);

  return (
    <View style={[styles.wrap, containerStyle]}>
      <TextInput
        {...props}
        style={[styles.input, style]}
        secureTextEntry={!visible}
        autoCapitalize="none"
        autoCorrect={false}
        placeholderTextColor={NPTTEBrand.colors.sovereign.muted}
      />
      <Pressable
        style={styles.toggle}
        onPress={() => setVisible((v) => !v)}
        accessibilityRole="button"
        accessibilityLabel={visible ? "Hide password" : "Show password"}
      >
        <Text style={styles.toggleText}>{visible ? "Hide" : "Show"}</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    position: "relative",
    marginBottom: NPTTEBrand.spacing.md,
  },
  input: {
    borderWidth: 1,
    borderColor: NPTTEBrand.colors.sovereign.border,
    borderRadius: NPTTEBrand.radius.sm,
    padding: 12,
    paddingRight: 64,
    color: NPTTEBrand.colors.sovereign.text,
    backgroundColor: NPTTEBrand.colors.sovereign.surface,
  },
  toggle: {
    position: "absolute",
    right: 12,
    top: 0,
    bottom: 0,
    justifyContent: "center",
  },
  toggleText: {
    color: NPTTEBrand.colors.sovereign.accent,
    fontSize: 13,
    fontWeight: "600",
  },
});
