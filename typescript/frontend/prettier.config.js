module.exports = {
  plugins: [
    "@ianvs/prettier-plugin-sort-imports",
    "prettier-plugin-tailwindcss",
  ],

  // @ianvs/prettier-plugin-sort-imports options:
  importOrder: [
    "<BUILT_IN_MODULES>",
    "",
    "^(react|next(.*))$",
    "",
    "<THIRD_PARTY_MODULES>",
    "",
    "^@/api/(.*)$",
    "",
    "^@/(.*)$",
    "",
    "^[../]",
    "^[./]",
  ],
  importOrderParserPlugins: ["typescript", "jsx", "decorators-legacy"],
  importOrderTypeScriptVersion: "5.4.5",

  // prettier-plugin-tailwindcss options:
  tailwindFunctions: [
    "clsx",
    "cn",
    "twMerge",
    "customTwMerge",
    "twJoin",
    "clsx",
  ],
};
