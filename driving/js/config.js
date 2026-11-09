// ===== Site settings — edit these before going live =====
window.SITE = {
  name: "Theory Test Practice Ireland",
  // Your live address (used by the WhatsApp / Facebook share buttons).
  url: "https://tavion.ie/driving/",

  // Google AdSense. Leave adsenseClient empty to show grey "Ad space" placeholders.
  // Example: adsenseClient: "ca-pub-1234567890123456"
  adsenseClient: "",
  adSlots: {
    question: "", // ad unit shown on every question page
    results: "",  // ad unit on the results page
    home: ""      // ad unit on the home / topic pages
  }
};

// ===== Licence categories =====
// To add a new test later (e.g. truck), add an entry here, set enabled: true,
// and tag questions in questions.js with its key in their `tests` array.
window.TESTS = {
  car: {
    name: "Car", category: "Category B", icon: "🚗",
    examSize: 40, passMark: 35, minutes: 45, enabled: true
  },
  motorcycle: {
    name: "Motorcycle", category: "Categories AM, A1, A2, A", icon: "🏍️",
    examSize: 40, passMark: 35, minutes: 45, enabled: true
  },
  truck: { name: "Truck", category: "Categories C, C1", icon: "🚚", enabled: false },
  bus:   { name: "Bus",   category: "Categories D, D1", icon: "🚌", enabled: false },
  tractor: { name: "Tractor", category: "Category W", icon: "🚜", enabled: false }
};

// ===== Question topics =====
window.TOPICS = {
  rules:      "Rules of the Road & Legal Matters",
  signs:      "Road Signs, Markings & Lights",
  risk:       "Managing Risk & Hazards",
  safe:       "Safe & Responsible Driving",
  vulnerable: "Vulnerable Road Users",
  control:    "Vehicle Control & Technical",
  moto:       "Motorcycle Riding"
};
