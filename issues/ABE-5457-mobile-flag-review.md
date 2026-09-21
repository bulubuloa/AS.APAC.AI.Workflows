# ABE-5457 — providers whose Mobile flag differs between the CMS and Roadside (prod, 16 Sep 2026)

For BA review before the backfill runs. **Question per row:** is this vendor really a mobile provider (has technicians with the app, takes Auto-mode jobs)?

Context: the CMS marks 687 of 752 roadside vendors as mobile, including call centres — that looks like a migration default. Rows marked in the CMS as mobile but that are call centres / dealers / office-only vendors should be corrected **in the CMS**, then the backfill copies the corrected value.

## A. CMS says mobile = YES, Roadside says NO — 317 providers (will be set to mobile unless corrected in CMS)

| # | Roadside ID | Roadside name | CMS name | Last sync status | BA decision |
|---|---|---|---|---|---|
| 1 | `2-0359` | Pound Yangyont | Pound Yangyont | Update From Benefit | |
| 2 | `2-0364` | Oh Key Service | Oh Key Service | Update From Benefit | |
| 3 | `2-0366` | Nisson Call Center | Nisson Call Center | Success | |
| 4 | `2-0367` | Chevrolet Call Center | Chevrolet Call Center | Success | |
| 5 | `2-0368` | Benz Star Assist | Benz Star Assist | Success | |
| 6 | `2-0369` | BMW Call Center | BMW Call Center | Success | |
| 7 | `2-0370` | Ford Roadside Assistance | Ford Roadside Assistance | Success | |
| 8 | `2-0371` | Toyota Call Center | Toyota Call Center | Success | |
| 9 | `2-0372` | Mazda Speed Line | Mazda Speed Line | Success | |
| 10 | `2-0373` | Aomni Charoenyont | Aomni Charoenyont | Success | |
| 11 | `2-0374` | Leon Thai Motorcycle | Leon Thai Motorcycle | Success | |
| 12 | `2-0375` | International SOS Thailand | International SOS Thailand | Success | |
| 13 | `2-0836` | Chatuporn Towing | Chatuporn Towing | Success | |
| 14 | `2-0839` | Charoen Kolakan Garage | Charoen Kolakan Garage | Update From Benefit | |
| 15 | `2-0841` | Kanjana Towing | Kanjana Towing | Update From Benefit | |
| 16 | `2-0842` | Praipraya Towing | Praipraya Towing | Success | |
| 17 | `2-0843` | Sol Towing | Sol Towing | Success | |
| 18 | `2-0845` | Autthawut Towing | Autthawut Towing | Update From Benefit | |
| 19 | `2-0846` | Somjai Key service | Somjai Key service | Success | |
| 20 | `2-0847` | Panda towing | Panda towing | Success | |
| 21 | `2-0848` | Weerapol Towing | Weerapol Towing | Success | |
| 22 | `2-0849` | Chang Noi Service | Chang Noi Service | Success | |
| 23 | `2-0850` | Phumin Service | Phumin Service | Success | |
| 24 | `2-0851` | Bhosuwan Service - BKK | Bhosuwan Service - BKK | Success | |
| 25 | `2-0852` | Charoen Pattani Towing (Pattani) | Charoen Pattani Towing (Pattani) | Update From Benefit | |
| 26 | `2-0853` | We Are Towing | We Are Towing | Success | |
| 27 | `2-0854` | Kay Wee Towing | Kay Wee Towing | Success | |
| 28 | `2-0855` | Leng Bungkarn Service | Leng Bungkarn Service | Success | |
| 29 | `2-0856` | Anongchat Nongmee | Anongchat Nongmee | Success | |
| 30 | `2-0857` | Chanachai Yont | Chanachai Yont | Success | |
| 31 | `2-0858` | Chansuda Service | Chansuda Service | Success | |
| 32 | `2-0859` | Mondial Assistance | Mondial Assistance | Success | |
| 33 | `2-0860` | Thep Phunga Towing | Thep Phunga Towing | Success | |
| 34 | `2-0861` | U.WiangSa Towing | U.WiangSa Towing | Success | |
| 35 | `2-0862` | Tor Charoen Yon | Tor Charoen Yon | Success | |
| 36 | `2-0863` | SaengChanChai Towin | SaengChanChai Towin | Success | |
| 37 | `2-0864` | Slide Non | Slide Non | Success | |
| 38 | `2-0865` | Sitthiporn Slide on | Sitthiporn Slide on | Success | |
| 39 | `2-0866` | Narong Chai Towing | Narong Chai Towing | Success | |
| 40 | `2-0867` | 247 Towing | 247 Towing | Success | |
| 41 | `2-0868` | Bangleave Towing | Bangleave Towing | Success | |
| 42 | `2-0869` | Rungruang Service Garage | Rungruang Service Garage | Update From Benefit | |
| 43 | `2-0870` | Bang Pakong Slide On | Bang Pakong Slide On | Success | |
| 44 | `2-0871` | Phet Locksmith | Phet Locksmith | Success | |
| 45 | `2-0872` | Nartsit Towing (Mahasarakam) | Nartsit Towing (Mahasarakam) | Success | |
| 46 | `2-0876` | BangPakong Slide On | BangPakong Slide On | Success | |
| 47 | `2-0877` | Charoen Pattani Towing (Yala) | Charoen Pattani Towing (Yala) | Update From Benefit | |
| 48 | `2-0878` | Dom Towing | Dom Towing | Success | |
| 49 | `2-0879` | Somkiat Towing (Samutsakorn) | Somkiat Towing (Samutsakorn) | Success | |
| 50 | `2-0880` | Charoen Pattani Towing (Narathiwas) | Charoen Pattani Towing (Narathiwas) | Update From Benefit | |
| 51 | `2-0881` | Bangkok Silde Car (Bang Sue) | Bangkok Silde Car (Bang Sue) | Success | |
| 52 | `2-0882` | Bangkok Silde Car | Bangkok Silde Car | Success | |
| 53 | `2-0884` | Anon Locksmith (Nonthaburi) | Anon Locksmith (Nonthaburi) | Success | |
| 54 | `2-0885` | O shin Towin | O shin Towin | Success | |
| 55 | `2-0886` | Sukhothai | Sukhothai | Success | |
| 56 | `2-0887` | Customer | Customer | Success | |
| 57 | `2-0888` | Mee Tyre Shop | Mee Tyre Shop | Success | |
| 58 | `2-0889` | Pak Chong Service | Pak Chong Service | Success | |
| 59 | `2-0890` | Laura Locksmith | Laura Locksmith | Success | |
| 60 | `2-0891` | Somboon Muaklek Towing | Somboon Muaklek Towing | Success | |
| 61 | `2-0892` | Saithong Towing | Saithong Towing | Success | |
| 62 | `2-0893` | Veeraphon Master Key | Veeraphon Master Key | Success | |
| 63 | `2-0894` | Tum Chumporn Locksmith | Tum Chumporn Locksmith | Success | |
| 64 | `2-0895` | Bangkok Yont Uttaradit | Bangkok Yont Uttaradit | Success | |
| 65 | `2-0896` | Pakij Yont | Pakij Yont | Success | |
| 66 | `2-0897` | Waen Pakchong Locksmith | Waen Pakchong Locksmith | Success | |
| 67 | `2-0898` | Mai Sriracha Locksmith | Mai Sriracha Locksmith | Success | |
| 68 | `2-0899` | Pradit Kanchang | Pradit Kanchang | Success | |
| 69 | `2-0901` | Chamnan Mechanical Shop | Chamnan Mechanical Shop | Success | |
| 70 | `2-0902` | Uthai Garage | Uthai Garage | Success | |
| 71 | `2-0903` | Ampai Mechanical Shop | Ampai Mechanical Shop | Success | |
| 72 | `2-0904` | Muang Thong Workshop | Muang Thong Workshop | Update From Benefit | |
| 73 | `2-0905` | Pattara Eak Towing | Pattara Eak Towing | Success | |
| 74 | `2-0906` | Duangjai Pimai Towing | Duangjai Pimai Towing | Update From Benefit | |
| 75 | `2-0907` | Grand Master Key Center | Grand Master Key Center | Success | |
| 76 | `2-0908` | Nikom Pattana Locksmith | Nikom Pattana Locksmith | Success | |
| 77 | `2-0909` | Or Ruamrudi Battery Shop | Or Ruamrudi Battery Shop | Success | |
| 78 | `2-0910` | Pichet Phuket Towing | Pichet Phuket Towing | Success | |
| 79 | `2-0911` | Tee Udon Locksmith | Tee Udon Locksmith | Success | |
| 80 | `2-0913` | Egg Chiangmai Locksmith | Egg Chiangmai Locksmith | Success | |
| 81 | `2-0914` | Sindhanayon Locksmith | Sindhanayon Locksmith | Success | |
| 82 | `2-0915` | Apidet Locksmith | Apidet Locksmith | Success | |
| 83 | `2-0916` | Thachpong Locksmith | Thachpong Locksmith | Update From Benefit | |
| 84 | `2-0917` | Lorling Trang Locksmith | Lorling Trang Locksmith | Success | |
| 85 | `2-0918` | Nathamond Service | Nathamond Service | Success | |
| 86 | `2-0919` | Pee Pee Krabi Locksmith | Pee Pee Krabi Locksmith | Success | |
| 87 | `2-0920` | Ban Daeng Locksmith | Ban Daeng Locksmith | Success | |
| 88 | `2-0921` | Dhep Nakorn Garage | Dhep Nakorn Garage | Success | |
| 89 | `2-0922` | Prayoon Service Loei | Prayoon Service Loei | Success | |
| 90 | `2-0923` | Rungrueng Garage | Rungrueng Garage | Success | |
| 91 | `2-0924` | Tavorn Mahasarakham Garage | Tavorn Mahasarakham Garage | Success | |
| 92 | `2-0925` | Koonpan Amnaj Locksmith | Koonpan Amnaj Locksmith | Success | |
| 93 | `2-0926` | Amnaj Clinic Garage | Amnaj Clinic Garage | Update From Benefit | |
| 94 | `2-0927` | Tap Locksmith | Tap Locksmith | Success | |
| 95 | `2-0928` | Go Maesai Locksmith | Go Maesai Locksmith | Success | |
| 96 | `2-0929` | Supawad Supaan Locksmith | Supawad Supaan Locksmith | Success | |
| 97 | `2-0930` | Saman Car Care | Saman Car Care | Success | |
| 98 | `2-0931` | Teng Tyre Lopburi | Teng Tyre Lopburi | Success | |
| 99 | `2-0932` | Gupai Nung Chaiyaphum | Gupai Nung Chaiyaphum | Success | |
| 100 | `2-0933` | Dong Service Garage | Dong Service Garage | Success | |
| 101 | `2-0934` | Tee Charoennakorn Locksmith | Tee Charoennakorn Locksmith | Success | |
| 102 | `2-0935` | Nikhom Service | Nikhom Service | Update From Benefit | |
| 103 | `2-0936` | Choksurath Pran Towing | Choksurath Pran Towing | Success | |
| 104 | `2-0937` | KoonJaeTong Tak Locksmith | KoonJaeTong Tak Locksmith | Success | |
| 105 | `2-0938` | Asia Lue Garage | Asia Lue Garage | Update From Benefit | |
| 106 | `2-0939` | Donsai Garage Samui | Donsai Garage Samui | Success | |
| 107 | `2-0940` | Boonsuk Garage Samui | Boonsuk Garage Samui | Success | |
| 108 | `2-0941` | Noo Ruen Locksmith | Noo Ruen Locksmith | Success | |
| 109 | `2-0942` | Ekarin Ubon Locksmith | Ekarin Ubon Locksmith | Success | |
| 110 | `2-0943` | KoonJaeTong Guang Locksmith | KoonJaeTong Guang Locksmith | Success | |
| 111 | `2-0944` | Kuwan Chiangrai Locksmith | Kuwan Chiangrai Locksmith | Success | |
| 112 | `2-0945` | Prayoon Locksmith Konsawan | Prayoon Locksmith Konsawan | Success | |
| 113 | `2-0946` | Song Locksmith | Song Locksmith | Update From Benefit | |
| 114 | `2-0947` | Meng Lampang Locksmith | Meng Lampang Locksmith | Success | |
| 115 | `2-0948` | Dee Kit Auto Air | Dee Kit Auto Air | Success | |
| 116 | `2-0949` | Dej Chanburi Locksmith | Dej Chanburi Locksmith | Success | |
| 117 | `2-0950` | Yong Chanburi Locksmith | Yong Chanburi Locksmith | Success | |
| 118 | `2-0951` | Tee Trat Locksmith | Tee Trat Locksmith | Success | |
| 119 | `2-0952` | Rungroj Uthai Locksmith | Rungroj Uthai Locksmith | Success | |
| 120 | `2-0953` | Pairoj Chainat Locksmith | Pairoj Chainat Locksmith | Success | |
| 121 | `2-0954` | Mig Chiangmai Locksmith | Mig Chiangmai Locksmith | Success | |
| 122 | `2-0955` | Chiangmai Garage | Chiangmai Garage | Success | |
| 123 | `2-0956` | Man Garage Payao | Man Garage Payao | Success | |
| 124 | `2-0957` | Likhit Payao Locksmith | Likhit Payao Locksmith | Success | |
| 125 | `2-0958` | Torh Sukhothai Locksmith | Torh Sukhothai Locksmith | Success | |
| 126 | `2-0959` | Thawatchai Prae Locksmith | Thawatchai Prae Locksmith | Success | |
| 127 | `2-0961` | Doctor Dee Tak Locksmith | Doctor Dee Tak Locksmith | Success | |
| 128 | `2-0962` | Samrit Kampaeng Locksmith | Samrit Kampaeng Locksmith | Success | |
| 129 | `2-0963` | Aun Lampang Locksmith | Aun Lampang Locksmith | Success | |
| 130 | `2-0964` | Odd Singhaburi Locksmith | Odd Singhaburi Locksmith | Success | |
| 131 | `2-0965` | Prince Chiangrai Locksmith | Prince Chiangrai Locksmith | Success | |
| 132 | `2-0966` | Samor Locksmith Saraburi | Samor Locksmith Saraburi | Update From Benefit | |
| 133 | `2-0967` | Jun Fah Locksmith | Jun Fah Locksmith | Success | |
| 134 | `2-0968` | Nimitra Ratchburi Locksmith | Nimitra Ratchburi Locksmith | Success | |
| 135 | `2-0969` | Tik Nakornpathom Locksmith | Tik Nakornpathom Locksmith | Success | |
| 136 | `2-0970` | Weechai Locksmith | Weechai Locksmith | Success | |
| 137 | `2-0971` | Egg Omnoi Locksmith | Egg Omnoi Locksmith | Success | |
| 138 | `2-0972` | Bang Pa In Towing | Bang Pa In Towing | Success | |
| 139 | `2-0973` | Chanchai Udon Locksmith | Chanchai Udon Locksmith | Success | |
| 140 | `2-0974` | Masterkey | Masterkey | Success | |
| 141 | `2-0975` | Kitdamrongchai Garage | Kitdamrongchai Garage | Update From Benefit | |
| 142 | `2-0976` | Bandit Locksmith | Bandit Locksmith | Success | |
| 143 | `2-0977` | Kuwanruen Surat Shop | Kuwanruen Surat Shop | Success | |
| 144 | `2-0978` | Quick Key Shop | Quick Key Shop | Update From Benefit | |
| 145 | `2-0979` | Wachira Towing | Wachira Towing | Update From Benefit | |
| 146 | `2-0980` | Supakit Charoenyon Gagage | Supakit Charoenyon Gagage | Success | |
| 147 | `2-0981` | Noil Sapanmai Locksmith | Noil Sapanmai Locksmith | Success | |
| 148 | `2-0982` | Udom Baanpai Locksmith | Udom Baanpai Locksmith | Success | |
| 149 | `2-0983` | Samai Nongbua Locksmith | Samai Nongbua Locksmith | Success | |
| 150 | `2-0984` | Poofah Nongbua Shop | Poofah Nongbua Shop | Success | |
| 151 | `2-0985` | Aood Loei Locksmith | Aood Loei Locksmith | Success | |
| 152 | `2-0986` | Noil Rasin Loei Locksmith | Noil Rasin Loei Locksmith | Success | |
| 153 | `2-0987` | So Technic Loei | So Technic Loei | Update From Benefit | |
| 154 | `2-0988` | Tee Kunjaetong Nongkhai | Tee Kunjaetong Nongkhai | Success | |
| 155 | `2-0989` | Sukanya Nongkhai shop | Sukanya Nongkhai shop | Success | |
| 156 | `2-0991` | Sridhep Nakornpanom Locksmith | Sridhep Nakornpanom Locksmith | Success | |
| 157 | `2-0992` | Em Nakornpanom Locksmith | Em Nakornpanom Locksmith | Success | |
| 158 | `2-0993` | Chachawan Renu Nakorn Shop | Chachawan Renu Nakorn Shop | Success | |
| 159 | `2-0994` | Torh Kanchang Mukdahan | Torh Kanchang Mukdahan | Success | |
| 160 | `2-0995` | Technic Yarnyont | Technic Yarnyont | Success | |
| 161 | `2-0996` | Nateetong Sarakam Locksmith | Nateetong Sarakam Locksmith | Success | |
| 162 | `2-0997` | Sanan Silk Kalasin | Sanan Silk Kalasin | Success | |
| 163 | `2-0998` | Sorh Koonjae Kalasin Locksmith | Sorh Koonjae Kalasin Locksmith | Success | |
| 164 | `2-1000` | Gen Roiet Locksmith | Gen Roiet Locksmith | Success | |
| 165 | `2-1001` | Solex Ubon Locksmith | Solex Ubon Locksmith | Success | |
| 166 | `2-1002` | Noom Yangyont | Noom Yangyont | Success | |
| 167 | `2-1003` | Chok Amnuay Ubon Shop | Chok Amnuay Ubon Shop | Success | |
| 168 | `2-1004` | Kittichai Dejudom Locksmith | Kittichai Dejudom Locksmith | Success | |
| 169 | `2-1005` | Wichai Sisaket Locksmith | Wichai Sisaket Locksmith | Success | |
| 170 | `2-1006` | Prasert Nanglong Locksmith | Prasert Nanglong Locksmith | Success | |
| 171 | `2-1007` | Egg Petchaboon Locksmith | Egg Petchaboon Locksmith | Success | |
| 172 | `2-1008` | Ohh Lomsak Locksmith | Ohh Lomsak Locksmith | Success | |
| 173 | `2-1009` | Koson Clinic Yont | Koson Clinic Yont | Success | |
| 174 | `2-1010` | Go Wah Nakorn Locksmith | Go Wah Nakorn Locksmith | Success | |
| 175 | `2-1011` | Pichai Garage | Pichai Garage | Success | |
| 176 | `2-1012` | Pasidh Pang Nga Locksmith | Pasidh Pang Nga Locksmith | Success | |
| 177 | `2-1013` | Udom Taimuang Locksmith | Udom Taimuang Locksmith | Success | |
| 178 | `2-1014` | Daeng Ranong Locksmith | Daeng Ranong Locksmith | Success | |
| 179 | `2-1015` | Guy Padrew Locksmith | Guy Padrew Locksmith | Success | |
| 180 | `2-1016` | Pued Nakornnayok Locksmith | Pued Nakornnayok Locksmith | Success | |
| 181 | `2-1017` | Rang Trat Locksmith | Rang Trat Locksmith | Success | |
| 182 | `2-1018` | Lop Garage | Lop Garage | Success | |
| 183 | `2-1019` | Go Doo Kamon Shop | Go Doo Kamon Shop | Success | |
| 184 | `2-1020` | Shine Tungsong Locksmith | Shine Tungsong Locksmith | Success | |
| 185 | `2-1021` | Chamnan Patong Locksmith | Chamnan Patong Locksmith | Success | |
| 186 | `2-1022` | Nung Sakaew Mobile | Nung Sakaew Mobile | Success | |
| 187 | `2-1023` | Solo Sakaew Locksmith | Solo Sakaew Locksmith | Success | |
| 188 | `2-1024` | Suwan Aran Lockmsith | Suwan Aran Lockmsith | Success | |
| 189 | `2-1025` | Namthip Baanchang Locksmith | Namthip Baanchang Locksmith | Success | |
| 190 | `2-1026` | Wichien Baan Pae Locksmith | Wichien Baan Pae Locksmith | Success | |
| 191 | `2-1027` | Jeab Service | Jeab Service | Success | |
| 192 | `2-1028` | Sithiwet Angthong Locksmith | Sithiwet Angthong Locksmith | Success | |
| 193 | `2-1029` | Jade Garage | Jade Garage | Success | |
| 194 | `2-1030` | Clinic Koonjae Noo | Clinic Koonjae Noo | Success | |
| 195 | `2-1031` | Maneerat Garage | Maneerat Garage | Update From Benefit | |
| 196 | `2-1032` | Kittiphol Phrachuab Service | Kittiphol Phrachuab Service | Success | |
| 197 | `2-1033` | Pornchai Maehongson Shop | Pornchai Maehongson Shop | Success | |
| 198 | `2-1034` | Goh Sangtong | Goh Sangtong | Success | |
| 199 | `2-1036` | Suwan Garage | Suwan Garage | Success | |
| 200 | `2-1037` | Grai Tong Towing | Grai Tong Towing | Success | |
| 201 | `2-1038` | Rungroj Towing | Rungroj Towing | Success | |
| 202 | `2-1039` | Kulkeaw Garage | Kulkeaw Garage | Success | |
| 203 | `2-1040` | Piya Pakchong Service | Piya Pakchong Service | Success | |
| 204 | `2-1041` | Petch Locksmith Cha Am | Petch Locksmith Cha Am | Success | |
| 205 | `2-1042` | Pong Dheparak | Pong Dheparak | Success | |
| 206 | `2-1043` | Sak Nan Locksmith | Sak Nan Locksmith | Success | |
| 207 | `2-1044` | Boonpaan Towing | Boonpaan Towing | Update From Benefit | |
| 208 | `2-1045` | Samak Towing | Samak Towing | Success | |
| 209 | `2-1046` | Pay Uttaradit Locksmith | Pay Uttaradit Locksmith | Success | |
| 210 | `2-1047` | Ja Sit Denchai Towing | Ja Sit Denchai Towing | Success | |
| 211 | `2-1048` | M.R. Towing | M.R. Towing | Success | |
| 212 | `2-1049` | Likhit Sisaket Towing | Likhit Sisaket Towing | Update From Benefit | |
| 213 | `2-1050` | Prayoon Towing | Prayoon Towing | Update From Benefit | |
| 214 | `2-1051` | Katha Chaiyaphum Garage | Katha Chaiyaphum Garage | Success | |
| 215 | `2-1052` | Nava Towing Rajapruk | Nava Towing Rajapruk | Success | |
| 216 | `2-1053` | Pongsakorn Service | Pongsakorn Service | Success | |
| 217 | `2-1054` | Bamroong Mechanic | Bamroong Mechanic | Success | |
| 218 | `2-1055` | Maha-Bho Rodyoke | Maha-Bho Rodyoke | Success | |
| 219 | `2-1056` | Volvo Group (Thailand) Co.,Ltd (Volvo Call Center) | Volvo Group (Thailand) Co.,Ltd (Volvo Call Center) | Success | |
| 220 | `2-1057` | Chang Key Nakhon Sawan | Chang Key Nakhon Sawan | Success | |
| 221 | `2-1407` | Yongyuth Service Towing | Yongyuth Service Towing | Success | |
| 222 | `2-1408` | Montee Towing & Slide car | Montee Towing & Slide car | Update From Benefit | |
| 223 | `2-1409` | Kabinburi Service | Kabinburi Service | Success | |
| 224 | `2-1410` | AG Battery Service | AG Battery Service | Update From Benefit | |
| 225 | `2-1411` | James Key Services | James Key Services | Success | |
| 226 | `2-1412` | NK Towing Service | NK Towing Service | Success | |
| 227 | `2-1413` | Ched Key Service | Ched Key Service | Success | |
| 228 | `2-1414` | Nueng Tyre service | Nueng Tyre service | Success | |
| 229 | `2-1415` | Keng Towing Service | Keng Towing Service | Success | |
| 230 | `2-1416` | Armeen Services | Armeen Services | Success | |
| 231 | `2-1418` | Bungkan Slide Car | Bungkan Slide Car | Success | |
| 232 | `2-1419` | Winai Transport | Winai Transport | Success | |
| 233 | `2-1420` | Nop Towing | Nop Towing | Success | |
| 234 | `2-1421` | Peak Towing Service | Peak Towing Service | Success | |
| 235 | `2-1422` | Doi Saken Service | Doi Saken Service | Update From Benefit | |
| 236 | `2-1423` | Anon LockSmith (Rama 3) | Anon LockSmith (Rama 3) | Success | |
| 237 | `2-1424` | Noom Rodyok Lupburi | Noom Rodyok Lupburi | Success | |
| 238 | `2-1425` | Thamarat Towing Service | Thamarat Towing Service | Success | |
| 239 | `2-1426` | Smartkey sale and service | Smartkey sale and service | Success | |
| 240 | `2-1427` | Cyber and Lock key service | Cyber and Lock key service | Success | |
| 241 | `2-1428` | Odd-Jeab Car Locksmith | Odd-Jeab Car Locksmith | Success | |
| 242 | `2-1429` | Mae Hong Son Towing | Mae Hong Son Towing | Update From Benefit | |
| 243 | `2-1430` | Oh Rodyok | Oh Rodyok | Success | |
| 244 | `2-1431` | Charoen Pattani Towing (Songkla) | Charoen Pattani Towing (Songkla) | Update From Benefit | |
| 245 | `2-1432` | New Slide-on | New Slide-on | Update From Benefit | |
| 246 | `2-1433` | Chawalit Maintenance | Chawalit Maintenance | Success | |
| 247 | `2-1434` | Bangswan Garage | Bangswan Garage | Update From Benefit | |
| 248 | `2-1435` | SL Auto Slide | SL Auto Slide | Success | |
| 249 | `2-1436` | Thongkham Service | Thongkham Service | Update From Benefit | |
| 250 | `2-1437` | Bhosuwan – Sa Kaeo | Bhosuwan – Sa Kaeo | Success | |
| 251 | `2-1438` | Key Stores (Pattani) | Key Stores (Pattani) | Success | |
| 252 | `2-1439` | Richco Harley Chiangmai | Richco Harley Chiangmai | Success | |
| 253 | `2-1441` | P.O. MotorCycle | P.O. MotorCycle | Success | |
| 254 | `2-1442` | Kheak Locksmith | Kheak Locksmith | Success | |
| 255 | `2-1443` | Chang Moo Key | Chang Moo Key | Success | |
| 256 | `2-1444` | Sanan Key | Sanan Key | Success | |
| 257 | `2-1445` | TJ Garage 2009 | TJ Garage 2009 | Success | |
| 258 | `2-1446` | Chang Somkid Key | Chang Somkid Key | Success | |
| 259 | `2-1447` | Posh Rodyok | Posh Rodyok | Success | |
| 260 | `2-1448` | Buengkan Locksmith | Buengkan Locksmith | Success | |
| 261 | `2-1449` | Narathiwat Key | Narathiwat Key | Success | |
| 262 | `2-1450` | Chang Chai key Maeklong | Chang Chai key Maeklong | Success | |
| 263 | `2-1451` | Nakhon Key | Nakhon Key | Success | |
| 264 | `2-1452` | Chang Air 108 Key | Chang Air 108 Key | Success | |
| 265 | `2-1453` | Chang Key Sam Ngam | Chang Key Sam Ngam | Success | |
| 266 | `2-1454` | Chang Ae Key | Chang Ae Key | Success | |
| 267 | `2-1455` | Teera Car Care | Teera Car Care | Success | |
| 268 | `2-1456` | Chang Vee Locksmith | Chang Vee Locksmith | Success | |
| 269 | `2-1457` | Sermsub Battery | Sermsub Battery | Success | |
| 270 | `2-1458` | Thung Song locksmith | Thung Song locksmith | Success | |
| 271 | `2-1459` | Chang John locksmith | Chang John locksmith | Success | |
| 272 | `2-1460` | Amnat locksmith | Amnat locksmith | Success | |
| 273 | `2-1461` | Chang Noom locksmith | Chang Noom locksmith | Success | |
| 274 | `2-1462` | Cha-am Locksmith | Cha-am Locksmith | Success | |
| 275 | `2-1463` | K Slide Car | K Slide Car | Success | |
| 276 | `2-1464` | Wara Slide on | Wara Slide on | Success | |
| 277 | `2-1465` | PT Chiang Rai | PT Chiang Rai | Update From Benefit | |
| 278 | `2-1466` | Bikestyle Transport | Bikestyle Transport | Success | |
| 279 | `2-1467` | Big key | Big key | Success | |
| 280 | `2-1468` | PK Rungrueng Slide Car | PK Rungrueng Slide Car | Update From Benefit | |
| 281 | `2-1469` | PNB Bigbike | PNB Bigbike | Success | |
| 282 | `2-1470` | Mongkhon Rodyok | Mongkhon Rodyok | Success | |
| 283 | `2-1472` | Nueng key shop | Nueng key shop | Success | |
| 284 | `2-1473` | Chang Aek Key | Chang Aek Key | Success | |
| 285 | `2-1474` | Anan Polcharoen | Anan Polcharoen | Success | |
| 286 | `2-1475` | Watcharin Wongwang | Watcharin Wongwang | Success | |
| 287 | `2-1476` | Sakda Chimmai | Sakda Chimmai | Success | |
| 288 | `2-1477` | Uasmarn Madadam | Uasmarn Madadam | Success | |
| 289 | `2-1479` | Phangnga Rodyok Rodslide | Phangnga Rodyok Rodslide | Success | |
| 290 | `2-1480` | Natthapong Rodyok | Natthapong Rodyok | Update From Benefit | |
| 291 | `2-1481` | Nakhonphanom Honda Cars | Nakhonphanom Honda Cars | Success | |
| 292 | `2-1482` | Chang key Ang Thong | Chang key Ang Thong | Success | |
| 293 | `2-1483` | Chang Key Ratchaburi | Chang Key Ratchaburi | Success | |
| 294 | `2-1484` | Surin Locksmith | Surin Locksmith | Success | |
| 295 | `2-1485` | Trang Lock Smith | Trang Lock Smith | Success | |
| 296 | `2-1688` | S.R.NAKHON BAN CAR SERVEICE CO.,LTD. | S.R.NAKHON BAN CAR SERVEICE CO.,LTD. | Success | |
| 297 | `2-1690` | Bhosuwan – Ladprao | Bhosuwan – Ladprao | Success | |
| 298 | `2-1691` | Bhosuwan - Bangkae | Bhosuwan - Bangkae | Success | |
| 299 | `2-1692` | Chayapol Service | Chayapol Service | Success | |
| 300 | `2-1693` | Artit Rodyok Rodslide_กทม. | Artit Rodyok Rodslide_กทม. | Success | |
| 301 | `2-1721` | Chatchai Amponviphut | Chatchai Amponviphut | Success | |
| 302 | `2-1722` | ห้างหุ้นส่วนสามัญดาวเรือง คาร์เซ็นเตอร์ | ห้างหุ้นส่วนสามัญดาวเรือง คาร์เซ็นเตอร์ | Success | |
| 303 | `2-1746` | Peerada Service | Peerada Service | Success | |
| 304 | `2-1749` | Siam Towing | Siam Towing | Success | |
| 305 | `2-1754` | Blacklock Service | Blacklock Service | Success | |
| 306 | `2-1766` | Nop Slide Service_กทม. | Nop Slide Service_กทม. | Success | |
| 307 | `2-1767` | Bhosuwan – Saraburi | Bhosuwan – Saraburi | Success | |
| 308 | `2-1769` | S.R.NAKHON BAN CAR SERVICE CO.LTD._กทม. | S.R.NAKHON BAN CAR SERVICE CO.LTD._กทม. | Success | |
| 309 | `2-1789` | Art Towing | Art Towing | Success | |
| 310 | `2-1790` | Maruay Towing-Slide | Maruay Towing-Slide | Success | |
| 311 | `2-1820` | Meechai Auto Garage | Meechai Auto Garage | Update From Benefit | |
| 312 | `2-1828` | Moot Suphan Danchang Commonrail | Moot Suphan Danchang Commonrail | Update From Benefit | |
| 313 | `2-1860` | Wogi | Wogi | Update From Benefit | |
| 314 | `2-1873` | COFF | COFF  | Create From Benefit | |
| 315 | `2-1874` | REC media | REC media CMS update | Create From Benefit | |
| 316 | `2-1876` | UNM vendor new update | UNM vendor new update | Update From Benefit | |
| 317 | `2-1879` | Chanitsara Test | Chanitsara Test | Create From Benefit | |

## B. Roadside says mobile = YES, CMS says NO — 10 providers (will be set to NOT mobile)

| # | Roadside ID | Roadside name | CMS name | Last sync status | BA decision |
|---|---|---|---|---|---|
| 1 | `2-0019` | Nop Slide Service | Nop Slide Service |  | |
| 2 | `2-0027` | Ex Towing Korat | Ex Towing Korat |  | |
| 3 | `2-0028` | Bamrungkid Towing | Bamrungkid Towing |  | |
| 4 | `2-0029` | U Oshin Towing | U Oshin Towing |  | |
| 5 | `2-0032` | Kengteesudkarnchang | Kengteesudkarnchang | Update From Benefit | |
| 6 | `2-0192` | PS slide car transport | PS slide car transport |  | |
| 7 | `2-0343` | Samutsakorn Honda Cars | Samutsakorn Honda Cars |  | |
| 8 | `2-0357` | Wut Rodyok Nakhon Si | Wut Rodyok Nakhon Si |  | |
| 9 | `2-0362` | Bas Rodyok Slide Car | Bas Rodyok Slide Car |  | |
| 10 | `2-1814` | Chang Phlat Slide Car | Chang Phlat Slide Car | Create From Benefit | |

## Likely wrong in the CMS (names suggest call centre / non-mobile) — please check first

| Roadside ID | Name |
|---|---|
| `2-0366` | Nisson Call Center |
| `2-0367` | Chevrolet Call Center |
| `2-0368` | Benz Star Assist |
| `2-0369` | BMW Call Center |
| `2-0370` | Ford Roadside Assistance |
| `2-0371` | Toyota Call Center |
| `2-0372` | Mazda Speed Line |
| `2-0375` | International SOS Thailand |
| `2-0859` | Mondial Assistance |
| `2-0907` | Grand Master Key Center |
| `2-1056` | Volvo Group (Thailand) Co.,Ltd (Volvo Call Center) |
