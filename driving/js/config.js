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
  // The official BW test covers both cars (B) and tractors / work vehicles (W).
  car: {
    name: "Car & Tractor", category: "BW test · Categories B & W", icon: "🚗",
    examSize: 40, passMark: 35, minutes: 45, enabled: true
  },
  motorcycle: {
    name: "Motorcycle", category: "AM test · Categories AM, A1, A2, A", icon: "🏍️",
    examSize: 40, passMark: 35, minutes: 45, enabled: true
  },
  // Truck and bus tests: 100 questions, 120 minutes, pass mark 74. Combined CD test: 140 questions, 180 minutes, pass mark 104.
  truck: {
    name: "Truck", category: "C test · Categories C1, C, CE", icon: "🚚",
    examSize: 100, passMark: 74, minutes: 120, enabled: true,
    focus: ["loads", "hours", "heavy", "profess"], focusShare: 0.6
  },
  bus: {
    name: "Bus", category: "D test · Categories D1, D, DE", icon: "🚌",
    examSize: 100, passMark: 74, minutes: 120, enabled: true,
    focus: ["passengers", "hours", "heavy", "profess"], focusShare: 0.6
  },
  cd: {
    name: "Truck & Bus", category: "CD test · combined truck and bus", icon: "🚛",
    examSize: 140, passMark: 104, minutes: 180, enabled: true,
    focus: ["loads", "passengers", "hours", "heavy", "profess"], focusShare: 0.6
  }
};

// ===== Question topics =====
window.TOPICS = {
  rules:      "Rules of the Road & Legal Matters",
  signs:      "Road Signs, Markings & Lights",
  risk:       "Managing Risk & Hazards",
  safe:       "Safe & Responsible Driving",
  vulnerable: "Vulnerable Road Users",
  control:    "Vehicle Control & Technical",
  moto:       "Motorcycle Riding",
  tractor:    "Tractors & Work Vehicles",
  hours:      "Drivers' Hours & Tachographs",
  heavy:      "Heavy Vehicle Safety & Control",
  profess:    "Licensing, CPC & Regulations",
  loads:      "Loads, Coupling & Truck Operation",
  passengers: "Passengers & Bus Operation"
};
