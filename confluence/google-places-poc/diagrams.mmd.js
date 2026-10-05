// Mermaid sources for the Confluence page (rendered to PNG by render.html).
window.DIAGRAMS = {
  overview: `flowchart LR
  U["User browser<br/>React POC"]
  K[("Kontent.ai Delivery API<br/>deliver.kontent.ai<br/>UAT 225b0999… / PROD 994226e6…<br/>read-only, no key")]
  A["POC host — AWS Lambda + Function URL<br/>ABE VPC, egress NAT 52.74.89.90<br/>serves the app, adds Google key"]
  G[("Google Places API (New)<br/>places.googleapis.com")]
  P["Google photo CDN<br/>lh3.googleusercontent.com"]
  U -- "A. GET /{env}/items<br/>template_generic, location" --> K
  U -- "B. /gplaces/v1/…<br/>searchText, places/{id}, photo media" --> A
  A -- "+ X-Goog-Api-Key" --> G
  G -. "302 photo redirect" .-> P
  P -. image .-> U`,
  sequence: `sequenceDiagram
  autonumber
  actor U as User (browser)
  participant K as Kontent Delivery API
  participant A as POC host (Lambda)
  participant G as Google Places API
  Note over U,G: Example: Savelberg (Kontent PROD)
  U->>K: GET /994226e6…/items?system.type=template_generic&limit=1000&depth=0
  K-->>U: vendor "Savelberg", location = location_d0131c6a
  U->>K: GET /994226e6…/items?system.type=location&limit=1000&depth=0
  K-->>U: address_line_1 "Oriental Residence Bangkok 110 Wireless Road…", no GPS, no hours
  U->>A: POST /gplaces/v1/places:searchText {textQuery "Savelberg, Oriental Residence Bangkok 110 Wireless Road… 10330, Thailand", regionCode TH, languageCode en, maxResultCount 5}
  A->>G: POST /v1/places:searchText + X-Goog-Api-Key
  G-->>A: 1 place: Oriental Residence Bangkok (hotel)
  A-->>U: 1 place: Oriental Residence Bangkok (hotel)
  Note over U: best is a hotel, so retry restaurant-only
  U->>A: POST /gplaces/v1/places:searchText same body + includedType restaurant
  A->>G: POST /v1/places:searchText + key
  G-->>A: Savelberg, 136/1 Soi Yen Akat 2 (fine_dining_restaurant)
  A-->>U: Savelberg, 136/1 Soi Yen Akat 2
  U->>A: GET /gplaces/v1/places/ChIJC8qDNCGf4jARR-fM5CgWoH4?languageCode=en
  A->>G: GET /v1/places/ChIJC8qDNCGf4jARR-fM5CgWoH4 + key
  G-->>A: address, lat/lng, phone +66 2 252 8001, website, hours, rating 4.6, VERY_EXPENSIVE, 10 photos
  A-->>U: place details
  U->>A: GET /gplaces/v1/places/ChIJC8q…/photos/…/media?maxWidthPx=320
  A->>G: GET photo media + key
  G-->>U: 302 to lh3.googleusercontent.com (image)
  Note over U: MEDIUM: name matches, address differs (moved), GPS, hours, phone, website = CMS empty, Google has it`,

}
