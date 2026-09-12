# Hinglish Dataset Leakage Analysis

## Overview
- **Total Overlapping Texts (Unique Strings):** 1447
- **Affected Train Rows:** 1545
- **Affected Validation Rows:** 1457

## Overlap Categories
- **Same-Label Overlaps:** 1412 (97.58%)
- **Conflicting-Label Overlaps:** 35 (2.42%)

## Intra-Split Duplication & Conflicts
### Train Split
- Texts appearing multiple times: 320
- Texts with conflicting labels (among duplicates): 108
### Validation Split
- Texts appearing multiple times: 13
- Texts with conflicting labels (among duplicates): 4

## Representative Conflicting Examples (up to 20)

**Text:** `kheln ke liy maidan ki nahi zaroorat hai toh sirf junoon ki cwc19 cwc19london wc2019 iccworldcup2019`
- Train instances: [{'id': '25314', 'label': '2'}]
- Validation instances: [{'id': '21609', 'label': '1'}]

**Text:** `logon ki kismat mein toh lutna hi likha hai ameer gareebon ko loott hai vyapari grahakon ko loott hai aur neta`
- Train instances: [{'id': '24193', 'label': '1'}, {'id': '43534', 'label': '0'}]
- Validation instances: [{'id': '24193', 'label': '1'}]

**Text:** `evm ghotal se sambandhit ye kitab bjp netao ne hi likhi hai uns kyu nhi puchhat`
- Train instances: [{'id': '30794', 'label': '1'}, {'id': '38615', 'label': '0'}]
- Validation instances: [{'id': '30794', 'label': '1'}]

**Text:** `dogl ko kabhi bhi bjp samil nahi karna chahiy wais bjp khuda hi samajhadar haiisn gujrat el`
- Train instances: [{'id': '7971', 'label': '2'}, {'id': '18587', 'label': '1'}]
- Validation instances: [{'id': '7971', 'label': '2'}]

**Text:** `global agenda sirf modi ji ke pas hai congress 72000 se vote kharidna chahti thi aur desh ke agend`
- Train instances: [{'id': '18131', 'label': '0'}, {'id': '22745', 'label': '1'}]
- Validation instances: [{'id': '18131', 'label': '0'}]

**Text:** `manzil mile na mile par haan kutt zarur bhoknt hain aur manzil pe jaan waalon ko bhonk bhonk ke r`
- Train instances: [{'id': '22467', 'label': '1'}, {'id': '34234', 'label': '2'}]
- Validation instances: [{'id': '34234', 'label': '2'}]

**Text:** `life jhand hai jcb ki kudi badi mast hai 😂🤣😂🤣😒🤦🏽‍♂️😭`
- Train instances: [{'id': '11330', 'label': '2'}, {'id': '38441', 'label': '1'}]
- Validation instances: [{'id': '11330', 'label': '2'}]

**Text:** `ye apn suna hi hoga ki maa-baap k karmo ka fal bacho ko bhugtna padta h aap logo k`
- Train instances: [{'id': '36141', 'label': '1'}, {'id': '36955', 'label': '0'}]
- Validation instances: [{'id': '36955', 'label': '0'}]

**Text:** `project ka pap khatam hua ab sala theori kaun sambhalega die 😭`
- Train instances: [{'id': '29849', 'label': '1'}, {'id': '38474', 'label': '0'}]
- Validation instances: [{'id': '38474', 'label': '0'}, {'id': '29849', 'label': '1'}]

**Text:** `zaman ne gham ke alawa kuch dekha nahi aajkal umme duniya se naya rishta jodn ki taak mein hai kaafir pre`
- Train instances: [{'id': '14873', 'label': '1'}, {'id': '26812', 'label': '2'}]
- Validation instances: [{'id': '26812', 'label': '2'}]

**Text:** `tum jais log tv studio batkar bjp ki dalali karo total channel aur opposit ko gali g`
- Train instances: [{'id': '11328', 'label': '1'}, {'id': '12212', 'label': '0'}]
- Validation instances: [{'id': '12212', 'label': '0'}]

**Text:** `logon ko kam chor bana rahe hain ye log hamari mahnat ka paisa hai ais nahi udaya kart apn ghar k pai`
- Train instances: [{'id': '8692', 'label': '1'}, {'id': '41116', 'label': '0'}]
- Validation instances: [{'id': '8692', 'label': '1'}]

**Text:** `rassi jal gaya lekin aithan nahi gaya .. @ rahulgandhi ..52 hi kari ho bjp ke liyeinch inch ki ladai karog`
- Train instances: [{'id': '15876', 'label': '0'}, {'id': '27137', 'label': '1'}, {'id': '38088', 'label': '0'}]
- Validation instances: [{'id': '27137', 'label': '1'}, {'id': '38088', 'label': '0'}]

**Text:** `sir ye icc ke jyadatar event england hi kyu hote hai jabki ye fix hota hai ki har dusra match`
- Train instances: [{'id': '7931', 'label': '0'}, {'id': '34735', 'label': '1'}]
- Validation instances: [{'id': '34735', 'label': '1'}]

**Text:** `offic roop prash04 deepika006 snehal`
- Train instances: [{'id': '19961', 'label': '1'}, {'id': '23545', 'label': '2'}]
- Validation instances: [{'id': '19961', 'label': '1'}, {'id': '1393', 'label': '1'}]

**Text:** `gujju ko aadat hai paki pakai huye khane ki last time anna se pakwa ke jo roti lee baar soch rahe`
- Train instances: [{'id': '33403', 'label': '0'}]
- Validation instances: [{'id': '2975', 'label': '1'}]

**Text:** `super stupid secur user verifi everi point made miss tatkal book kind hire`
- Train instances: [{'id': '19726', 'label': '0'}]
- Validation instances: [{'id': '3497', 'label': '1'}]

**Text:** `baimaan tera ajay singh cheat baaj teri airlin saal chutiya banan ke liy baith ho jakar station bhi`
- Train instances: [{'id': '33175', 'label': '0'}, {'id': '42337', 'label': '1'}]
- Validation instances: [{'id': '42337', 'label': '1'}]

**Text:** `happi`
- Train instances: [{'id': '13014', 'label': '1'}, {'id': '16892', 'label': '2'}]
- Validation instances: [{'id': '16892', 'label': '2'}]

**Text:** `watersavingtipsbystramrahim dr msg water precious us sacha sauda sirsa`
- Train instances: [{'id': '13091', 'label': '2'}, {'id': '19830', 'label': '1'}]
- Validation instances: [{'id': '19830', 'label': '1'}]

## Representative Same-Label Examples (up to 20)

**Text:** `special ff special best friend follow - 's good launda sbki hlp krta h anyhw conditi`
- Train instances: [{'id': '9002', 'label': '2'}, {'id': '37267', 'label': '2'}]
- Validation instances: [{'id': '37267', 'label': '2'}]

**Text:** `iss bda kutta dalaal mc bc aadmi sport media mein koi nai isk jais dallon ko toh tihar jail`
- Train instances: [{'id': '17966', 'label': '0'}]
- Validation instances: [{'id': '17966', 'label': '0'}]

**Text:** `secularist sit outsid mandir bheek ka katora allah ke naam pe de de baba learn`
- Train instances: [{'id': '27414', 'label': '0'}]
- Validation instances: [{'id': '27414', 'label': '0'}]

**Text:** `'s wish best begin ( hope ) long journey gun probabl th`
- Train instances: [{'id': '29023', 'label': '2'}]
- Validation instances: [{'id': '29023', 'label': '2'}]

**Text:** `patrag kya naam hai us chu ye maulvi ka bharat ke musalman shri ram ko imam-e-hind ke naam se`
- Train instances: [{'id': '33239', 'label': '0'}]
- Validation instances: [{'id': '33239', 'label': '0'}]

**Text:** `siddiqui`
- Train instances: [{'id': '8254', 'label': '1'}, {'id': '8323', 'label': '1'}, {'id': '16441', 'label': '1'}, {'id': '21311', 'label': '1'}, {'id': '30815', 'label': '1'}, {'id': '41654', 'label': '1'}, {'id': '43082', 'label': '1'}]
- Validation instances: [{'id': '21311', 'label': '1'}]

**Text:** `tum 1963 se le ker aaj takk ye raaz apni g main chuppa k kaon bethay thaay teri aaj hi kabz k`
- Train instances: [{'id': '24468', 'label': '0'}]
- Validation instances: [{'id': '24468', 'label': '0'}]

**Text:** `sir g modi lehar nahi hai ye toh chu`
- Train instances: [{'id': '42115', 'label': '0'}]
- Validation instances: [{'id': '42115', 'label': '0'}]

**Text:** `love kee dia`
- Train instances: [{'id': '5825', 'label': '1'}]
- Validation instances: [{'id': '5825', 'label': '1'}]

**Text:** `abe kuch sharm karo tumhr jais baklol ke hisab se secur naam ki kou chiz hi nahi hai`
- Train instances: [{'id': '19631', 'label': '0'}, {'id': '30639', 'label': '0'}]
- Validation instances: [{'id': '30639', 'label': '0'}]

**Text:** `sabs pehl toh sare buddon ko nikal kar yuvaon ko lana padega sirf bait kar malai kh`
- Train instances: [{'id': '24211', 'label': '1'}]
- Validation instances: [{'id': '24211', 'label': '1'}]

**Text:** `kehena hai jo dil se kaho dilbar mere dil raho 😍 frogner park norway ❤️❤️`
- Train instances: [{'id': '38056', 'label': '1'}]
- Validation instances: [{'id': '38056', 'label': '1'}]

**Text:** `love khattar sahab haathi chale bazaar wife professor delhi school`
- Train instances: [{'id': '20551', 'label': '1'}]
- Validation instances: [{'id': '20551', 'label': '1'}]

**Text:** `sahi bat bole sirjijabtak hatayeng nahi vika nahi hoga tourism ko badhawaaur hindustan ka koibhi`
- Train instances: [{'id': '22320', 'label': '1'}]
- Validation instances: [{'id': '22320', 'label': '1'}]

**Text:** `isi sidra tum ko sharam nahi aati holnak waqiy pe b riyasat kar rahi ho imran charsi k ba`
- Train instances: [{'id': '42923', 'label': '0'}]
- Validation instances: [{'id': '42923', 'label': '0'}]

**Text:** `ye chutiy sachm kahas aata hai bc inko kaun pchta hai ye sb madarchod kch pta hai nai aajat khudki chu`
- Train instances: [{'id': '22048', 'label': '0'}]
- Validation instances: [{'id': '22048', 'label': '0'}]

**Text:** `sister buri baat aysa nahi boltey kisi ko chor taber pori bat`
- Train instances: [{'id': '11127', 'label': '1'}]
- Validation instances: [{'id': '11127', 'label': '1'}]

**Text:** `salut hy tumh dher sari duaayen`
- Train instances: [{'id': '7426', 'label': '2'}]
- Validation instances: [{'id': '7426', 'label': '2'}]

**Text:** `rashid abe bhagwa aatankwaadi hum aaj bhi yahan k raja hain suar sale bheek tumh dete h`
- Train instances: [{'id': '22970', 'label': '0'}]
- Validation instances: [{'id': '22970', 'label': '0'}]

**Text:** `chutiy stoner nahi hu na teri tarh kuch sungn ya fukn nahi jata lawd pata bhi nahi chalta ki`
- Train instances: [{'id': '5726', 'label': '0'}]
- Validation instances: [{'id': '5726', 'label': '0'}]
