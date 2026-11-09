// Finicky config: routes links to a browser/profile based on the app that opened them.
// Linked to ~/.finicky.js by setup.zsh. Profile names are as shown in Chrome
// (see "profile.info_cache" in ~/Library/Application Support/Google/Chrome/Local State).

const fromApp = (bundleId) => (url, { opener }) => opener?.bundleId === bundleId;

export default {
  defaultBrowser: "Google Chrome",
  options: {
    hideIcon: true, // no menu bar icon; open Finicky.app to see config errors
  },
  handlers: [
    {
      // Slack -> work Chrome profile
      match: fromApp("com.tinyspeck.slackmacgap"),
      browser: { name: "Google Chrome", profile: "brandnewschool.com" },
    },
    {
      // Discord -> personal Chrome profile
      match: fromApp("com.hnc.Discord"),
      browser: { name: "Google Chrome", profile: "Person 1" },
    },
  ],
};
