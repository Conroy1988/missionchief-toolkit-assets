    // Issue #133 clean-room live mission requirements matrix.
    // MissionChief's active mission DOM is authoritative. Unknown labels remain unresolved.
    const MISSION_REQUIREMENT_DEFINITIONS = Object.freeze([{"key":"police-helicopter-or-drone","label":"Police Helicopter or Drone","aliases":["Police Helicopter or Drone","Police Helicopters or Drones"],"types":[11,89,90,91],"equipment":["drone"]},{"key":"riv-or-major-foam","label":"RIV or Major Foam Tender","aliases":["RIV or Major Foam Tender","RIVs or Major Foam Tenders"],"types":[75,76]},{"key":"fire-engine-or-major-foam","label":"Fire Engine or Major Foam Tender","aliases":["Fire Engine or Major Foam Tender","Fire Engines or Major Foam Tenders"],"types":[0,1,16,17,26,37,38,47,75]},{"key":"fire-engine-riv-or-major-foam","label":"Fire Engine, RIV or Major Foam Tender","aliases":["Fire Engine, RIV or Major Foam Tender","Fire Engines, RIVs or Major Foam Tenders"],"types":[0,1,16,17,26,37,38,47,75,76]},{"key":"mountain-or-sar-4x4","label":"Mountain Rescue 4x4 or SAR 4x4","aliases":["Mountain Rescue 4x4 or SAR 4x4","Mountain Rescue 4x4s or SAR 4x4s"],"types":[93,99]},{"key":"rrv-or-specialist-paramedic","label":"RRV or Specialist Paramedic RRV","aliases":["RRV or Specialist Paramedic RRV","RRVs or Specialist Paramedic RRVs"],"types":[10,94,96]},{"key":"fire-engine-or-riv","label":"Fire Engine or RIV","aliases":["Fire Engine or RIV","Fire Engines or RIVs"],"types":[0,1,16,17,26,37,38,47,76]},{"key":"aerial-or-stairs","label":"Aerial Appliance or Rescue Stairs","aliases":["Aerial Appliance Truck or Rescue Stairs","Aerial Appliance Trucks or Rescue Stairs"],"types":[2,17,78]},{"key":"fire-rescue-aerial","label":"Fire, rescue or aerial appliance","aliases":["Fire engine, Rescue Support Vehicle or Aerial Appliance Truck","Fire engines, Rescue Support Vehicles or Aerial Appliance Trucks"],"types":[0,1,2,4,16,17,26,37,38,43,47]},{"key":"fire-or-rescue","label":"Fire Engine or Rescue Support Vehicle","aliases":["Fire engine or Rescue Support Vehicle","Fire engines or Rescue Support Vehicles"],"types":[0,1,4,16,17,26,37,38,43,47]},{"key":"police-or-arv","label":"Police Car or ARV","aliases":["Police Car or Armed Response Vehicle (ARV)","Police Cars or Armed Response Vehicles (ARVs)"],"types":[8,12,13,19,24,25,51,52,56,82,116]},{"key":"rsu-or-rescue-pump","label":"Rescue Support Unit or Rescue Pump","aliases":["Rescue Support Unit or Rescue Pump","Rescue Support Units or Rescue Pumps"],"types":[4,16,38,43]},{"key":"iccu-or-control","label":"ICCU or Ambulance Control Unit","aliases":["ICCU or Ambulance Control Unit","ICCU or Ambulance Control Units","ICCU or Ambulance Control Unit or Airfield Firefighting Command Vehicle","ICCU or Ambulance Control Units or Airfield Firefighting Command Vehicles"],"types":[15,31,44,77]},{"key":"hazmat-or-cbrn","label":"HazMat Unit or CBRN Vehicle","aliases":["HazMat Unit or CBRN Vehicle","HazMat Units or CBRN Vehicles"],"types":[7,32,39,48,49]},{"key":"boat-or-inland","label":"Inland Rescue Boat (Trailer)","aliases":["Boat Trailer or Inland Rescue Boat","Boat Trailers or Inland Rescue Boats","Inland Rescue Boat (Trailer)","Inland Rescue Boats (Trailer)","Inland Rescue Boat (Trailers)","Inland Rescue Boats (Trailers)"],"types":[67,74],"pair":true},{"key":"ilb-or-alb","label":"Seagoing Vessel","aliases":["ILB or ALB","ILBs or ALBs","Seagoing Vessel","Seagoing Vessels","ALB or ILB","ALBs or ILBs"],"types":[68,69]},{"key":"sar-support","label":"Operational Support or SAR Vehicle","aliases":["Operational Support Van, Trailer or Personal SAR Vehicle","Operational Support Vans, Trailers or Personal SAR Vehicles"],"types":[86,87,92],"pair":true},{"key":"fire-engine","label":"Fire Engine","aliases":["Fire engine","Fire engines"],"types":[0,1,16,17,26,37,38,47]},{"key":"aerial","label":"Aerial Appliance Truck","aliases":["Aerial Appliance Truck","Aerial Appliance Trucks"],"types":[2,17]},{"key":"fire-officer","label":"Fire Officer","aliases":["Fire Officer","Fire Officers","Fire Officer or Airfield Firefighting Command Vehicle","Fire Officers or Airfield Firefighting Command Vehicles"],"types":[3,15,44,77]},{"key":"basu","label":"Breathing Apparatus Support Unit (BASU)","aliases":["BASU","BASUs","Breathing Apparatus Support Unit","Breathing Apparatus Support Units"],"types":[14,39,46,49],"details":"Eligible vehicles: BASU, OSU, BASU Pod and OSU Pod. Prime Movers only count when paired with an eligible pod."},{"key":"water-carrier","label":"Water Carrier","aliases":["Water Carrier","Water Carriers"],"types":[6,26,36,41,50]},{"key":"drone","label":"Drone","aliases":["Drone","Drones"],"types":[89,90,91],"equipment":["drone"]},{"key":"control-van","label":"Control Van","aliases":["Control Van","Control Vans"],"types":[85]},{"key":"ambulance","label":"Ambulance","aliases":["Ambulance","Ambulances"],"types":[5,9]},{"key":"police-car","label":"Police Car","aliases":["Police car","Police cars"],"types":[8,12,13,19,24,25,51,52,56,82,116]},{"key":"hems","label":"HEMS","aliases":["HEMS"],"types":[9]},{"key":"critical-care-patient","label":"Critical Care","aliases":["Critical Care"],"group":"other","types":[],"countable":true,"patientCondition":true},{"key":"patient-transport","label":"Patient Transport","aliases":["Patient Transport"],"group":"other","types":[],"countable":true,"patientCondition":true},{"key":"police-helicopter","label":"Police Helicopter","aliases":["Police helicopter","Police helicopters","Policehelicopter","Policehelicopters"],"types":[11]},{"key":"armed-response","label":"Armed Response","aliases":["Armed Response","Armed Response Vehicle","Armed Response Vehicles"],"types":[13,25,52,56,82]},{"key":"dsu","label":"Dog Support Unit (DSU)","aliases":["Dog Support Unit (DSU)","Dog Support Units (DSUs)"],"types":[12,53]},{"key":"otl","label":"Operational Team Leader","aliases":["Operational Team Leader","Operational Team Leaders"],"types":[20,31,34]},{"key":"traffic-car","label":"Traffic Car","aliases":["Traffic Car","Traffic Cars"],"types":[24,25]},{"key":"atv-carrier","label":"ATV Carrier","aliases":["ATV Carrier","ATV Carriers"],"types":[30]},{"key":"primary-response","label":"Primary Response Vehicle","aliases":["Primary Response Vehicle","Primary Response Vehicles","PRV","PRVs"],"types":[27]},{"key":"secondary-response","label":"Secondary Response Vehicle","aliases":["Secondary Response Vehicle","Secondary Response Vehicles","SRV","SRVs"],"types":[28]},{"key":"welfare","label":"Welfare Vehicle","aliases":["Welfare Vehicle","Welfare Vehicles"],"types":[29,39,45,49,115]},{"key":"ambulance-officer","label":"Ambulance Officer","aliases":["Ambulance Officer","Ambulance Officers"],"types":[34]},{"key":"foam-unit","label":"Foam Unit","aliases":["Foam Unit","Foam Units"],"types":[35,36,37,38,42,75]},{"key":"mass-casualty","label":"Mass Casualty Equipment","aliases":["Mass Casualty Equipment"],"types":[33]},{"key":"mounted","label":"Mounted Unit","aliases":["Mounted Unit","Mounted Units"],"types":[55]},{"key":"4x4","label":"4x4 Vehicle","aliases":["4x4 Vehicle","4x4 Vehicles","4x4 Unit","4x4 Units"],"types":[66,73,93]},{"key":"coastguard-rope","label":"Coastguard Rope Rescue Unit","aliases":["Coastguard Rope Rescue Unit","Coastguard Rope Rescue Units"],"types":[59]},{"key":"flood-rescue","label":"Flood Rescue Unit","aliases":["Flood Rescue Unit","Flood Rescue Units"],"types":[61]},{"key":"crv","label":"CRV","aliases":["CRV","CRVs"],"types":[57,58,59]},{"key":"coastguard-commander","label":"Coastguard Commander","aliases":["Coastguard Commander","Coastguard Commanders"],"types":[60]},{"key":"ilb","label":"ILB","aliases":["ILB","ILBs"],"types":[68,69]},{"key":"coastguard-helicopter","label":"Coastguard Rescue Helicopter","aliases":["Coastguard Rescue Helicopter","Coastguard Rescue Helicopters"],"types":[64,65]},{"key":"alb","label":"ALB","aliases":["ALB","ALBs"],"types":[69]},{"key":"mud-decon","label":"Mud Decontamination Unit","aliases":["Mud Decontamination Unit","Mud Decontamination Units"],"types":[62]},{"key":"support-unit","label":"Support Unit","aliases":["Support Unit","Support Units"],"types":[63]},{"key":"rescue-watercraft","label":"Rescue Watercraft Trailer","aliases":["Rescue Watercraft (Trailer)","Rescue Watercraft (Trailers)"],"types":[70],"pair":true},{"key":"coastguard-mud","label":"Coastguard Mud Rescue Unit","aliases":["Coastguard Mud Rescue Unit","Coastguard Mud Rescue Units"],"types":[58]},{"key":"hovercraft","label":"Hovercraft Trailer","aliases":["Hovercraft (trailer)","Hovercrafts (trailer)"],"types":[71],"pair":true},{"key":"major-foam","label":"Major Foam Tender","aliases":["Major Foam Tender","Major Foam Tenders"],"types":[75]},{"key":"rescue-stair","label":"Rescue Stair","aliases":["Rescue Stair","Rescue Stairs"],"types":[78,2,17]},{"key":"airfield-command","label":"Airfield Firefighting Command Vehicle","aliases":["Airfield Firefighting Command Vehicle","Airfield Firefighting Command Vehicles"],"types":[77]},{"key":"airfield-operations","label":"Airfield Operations Vehicle","aliases":["Airfield Operations Vehicle","Airfield Operations Vehicles"],"types":[79,80]},{"key":"riv","label":"RIV","aliases":["RIV","RIVs"],"types":[76]},{"key":"medical-trailer","label":"Medical Equipment Trailer","aliases":["Medical equipment trailer","Medical equipment trailers"],"types":[81],"pair":true},{"key":"airfield-supervisor","label":"Airfield Operations Supervisor","aliases":["Airfield Operations Supervisor","Airfield Operations Supervisors"],"types":[80]},{"key":"armed-cell","label":"Armed Cell Van","aliases":["Armed Cell Van","Armed Cell Vans"],"types":[82]},{"key":"cycle-responder","label":"Medical Cycle Responder","aliases":["Medical cycle responder","Medical cycle responders"],"types":[83]},{"key":"midwife","label":"Community Midwife","aliases":["Community Midwife","Community Midwives","Community Midwifes"],"types":[95]},{"key":"specialist-paramedic","label":"Specialist Paramedic RRV","aliases":["Specialist Paramedic RRV","Specialist Paramedic RRVs"],"types":[96]},{"key":"rescue-dog","label":"Rescue Dog","aliases":["Rescue Dog","Rescue Dogs"],"types":[101,102]},{"key":"mountain-4x4","label":"Mountain Rescue 4x4","aliases":["Mountain Rescue 4x4","Mountain Rescue 4x4s"],"types":[99]},{"key":"road-rail","label":"Road Rail Unit","aliases":["Road Rail Unit","Road Rail Units"],"types":[107]},{"key":"eiu","label":"EIU","aliases":["EIU","EIUs"],"types":[108]},{"key":"eod-commander","label":"EOD Commander","aliases":["EOD Commander","EOD Commanders"],"types":[109]},{"key":"eod-response","label":"EOD Response Vehicle","aliases":["EOD Response Vehicle","EOD Response Vehicles"],"types":[110]},{"key":"eod-medium","label":"EOD Medium Equipment Van","aliases":["EOD Medium Equipment Van","EOD Medium Equipment Vans"],"types":[111]},{"key":"eod-heavy","label":"EOD Heavy Equipment Vehicle","aliases":["EOD Heavy Equipment Vehicle","EOD Heavy Equipment Vehicles"],"types":[112]},{"key":"marine-eod-response","label":"Marine EOD Response Vehicle","aliases":["Marine EOD Response Vehicle","Marine EOD Response Vehicles"],"types":[113]},{"key":"marine-eod-equipment","label":"Marine EOD Equipment Van","aliases":["Marine EOD Equipment Van","Marine EOD Equipment Vans"],"types":[114]},{"key":"public-order-level-1","label":"Level 1 Public Order Officer","aliases":["Level 1 Public Order Officer","Level 1 Public Order Officers"],"group":"staff","types":[],"countable":false},{"key":"public-order-level-2","label":"Level 2 Public Order Officer","aliases":["Level 2 Public Order Officer","Level 2 Public Order Officers"],"group":"staff","types":[],"training":["Level 2 Public Order Officer","Level 2 Public Order","level_2_public_order"],"countable":true,"arrAttributes":["level_2_public_order"]},{"key":"police-medic-personnel","label":"Police Medic","aliases":["Police Medic","Police Medics"],"group":"staff","types":[],"countable":false},{"key":"police-sergeant-personnel","label":"Police Sergeant","aliases":["Police Sergeant","Police Sergeants"],"group":"staff","types":[],"training":["Police Sergeant","Police Sergeant Training","police_sergeant"],"countable":true,"arrAttributes":["police_sergeant"],"requireExplicitTraining":true},{"key":"police-inspector-personnel","label":"Police Inspector","aliases":["Police Inspector","Police Inspectors"],"group":"staff","types":[],"countable":true,"training":["Police Inspector","Police Inspector Training","police_inspector"],"arrAttributes":["police_inspector"],"requireExplicitTraining":true},{"key":"railway-police-officer","label":"Railway Police Officer","aliases":["Railway Police Officer","Railway Police Officers"],"group":"staff","types":[108],"training":["Railway Police Officer","Railway Police","railway_police"],"countable":true,"requireExplicitTraining":true,"arrAttributes":["railway_police"]},{"key":"search-advisor-personnel","label":"Search Advisor","aliases":["Search Advisor","Search Advisors"],"group":"staff","types":[],"training":["Search Advisor","Search Advisor Training","Police Search Advisor Training","Coastguard Search Advisor Training","search_and_rescue"],"arrAttributes":["search_and_rescue"],"countable":true},{"key":"sar-commander-personnel","label":"SAR Commander","aliases":["SAR Commander","SAR Commanders"],"group":"staff","types":[85,100],"training":["SAR Commander","Search Management Training","search_and_rescue_command"],"arrAttributes":["search_and_rescue_command"],"countable":true},{"key":"firefighters","label":"Firefighters","aliases":["more firefighter","more firefighters","Firefighter","Firefighters"],"group":"staff","types":[0,1,2,3,4,6,7,14,15,16,17,18,23,26,35,36,37,38,39,40]},{"key":"armed-personnel","label":"Armed Response Personnel","aliases":["Armed Response Personnel (In Armed Vehicles)","Armed Response Personnel"],"group":"staff","types":[13,25,52,56,82]},{"key":"police-officers","label":"Police Officers","aliases":["Police Officer","Police Officers"],"group":"staff","types":[8,12,13,19,24,25,51,52,53,55,56,82,116]},{"key":"paramedics","label":"Paramedics","aliases":["Paramedic","Paramedics"],"group":"staff","types":[5,9,20,27,28,31,34,81,83,95,96]},{"key":"search-technicians","label":"Search Technicians","aliases":["Search Technician","Search Technicians"],"group":"staff","types":[86,87,92,93,99,101,102]},{"key":"water-resource","label":"Water","aliases":["Water","litres of water","liters of water"],"group":"other","bar":"water","types":[]},{"key":"foam-resource","label":"Foam","aliases":["Foam","litres of foam","liters of foam"],"group":"other","bar":"foam","types":[]},{"key":"pump-resource","label":"Pumping Capacity","aliases":["l/min pumping process","l/min pumping capacity","Pumping Capacity"],"group":"other","bar":"pump","types":[]},{"key":"fire-engine-2","group":"vehicles","aliases":["Fire engine","Fire engines"],"types":[0,1,16,17,26,37,38,47]},{"key":"fire-engine-or-riv-2","group":"vehicles","aliases":["Fire Engine or RIV","Fire Engines or RIVs"],"types":[0,1,16,17,26,37,38,47,76]},{"key":"aerial-appliance-truck","group":"vehicles","aliases":["Aerial Appliance Truck","Aerial Appliance Trucks"],"types":[2,17]},{"key":"aerial-appliance-truck-or-rescue-stairs","group":"vehicles","aliases":["Aerial Appliance Truck or Rescue Stairs","Aerial Appliance Trucks or Rescue Stairs"],"types":[2,17,78]},{"key":"fire-officer-2","group":"vehicles","aliases":["Fire Officer","Fire Officers"],"types":[3,15,44,77]},{"key":"rescue-support-unit-or-rescue-pump","group":"vehicles","aliases":["Rescue Support Unit or Rescue Pump","Rescue Support Units or Rescue Pumps"],"types":[4,16,38,43]},{"key":"fire-engine-rescue-support-vehicle-or-aerial-appliance-truck","group":"vehicles","aliases":["Fire engine, Rescue Support Vehicle or Aerial Appliance Truck","Fire engines, Rescue Support Vehicles or Aerial Appliance Trucks"],"types":[0,1,2,4,16,17,26,37,38,43,47]},{"key":"fire-engine-or-rescue-support-vehicle","group":"vehicles","aliases":["Fire engine or Rescue Support Vehicle","Fire engines or Rescue Support Vehicles"],"types":[0,1,4,16,17,26,37,38,43,47]},{"key":"basu-2","group":"vehicles","aliases":["BASU","BASUs"],"types":[14,39,46,49]},{"key":"water-carrier-2","group":"vehicles","aliases":["Water Carrier","Water Carriers"],"types":[6,26,36,41,50]},{"key":"drone-2","group":"vehicles","aliases":["Drone","Drones"],"types":[89,90,91],"equipment":["drone"]},{"key":"operational-support-van-trailer-or-personal-sar-vehicle","group":"vehicles","aliases":["Operational Support Van, Trailer or Personal SAR Vehicle"],"types":[86,87,92]},{"key":"control-van-2","group":"vehicles","aliases":["Control Van","Control Vans"],"types":[85]},{"key":"iccu-or-ambulance-control-unit","group":"vehicles","aliases":["ICCU or Ambulance Control Unit","ICCU or Ambulance Control Units"],"types":[15,31,44,77]},{"key":"hazmat-unit-or-cbrn-vehicle","group":"vehicles","aliases":["HazMat Unit or CBRN Vehicle","HazMat Units or CBRN Vehicles"],"types":[7,32,39,48,49]},{"key":"ambulance-2","group":"vehicles","aliases":["Ambulance","Ambulances"],"types":[5]},{"key":"police-car-2","group":"vehicles","aliases":["Police car","Police cars"],"types":[8,12,13,19,24,25,51,52,56,82,116]},{"key":"police-car-or-armed-response-vehicle","group":"vehicles","aliases":["Police Car or Armed Response Vehicle (ARV)","Police Cars or Armed Response Vehicles (ARVs)"],"types":[8,12,13,19,24,25,51,52,56,82,116]},{"key":"hems-2","group":"vehicles","aliases":["HEMS"],"types":[9]},{"key":"policehelicopter","group":"vehicles","aliases":["Policehelicopter","Policehelicopters"],"types":[11]},{"key":"armed-response-2","group":"vehicles","aliases":["Armed Response"],"types":[13,25,52,56,82]},{"key":"dog-support-unit","group":"vehicles","aliases":["Dog Support Unit (DSU)","Dog Support Units (DSUs)"],"types":[12,53]},{"key":"operational-team-leader","group":"vehicles","aliases":["Operational Team Leader","Operational Team Leaders"],"types":[20,31,34]},{"key":"traffic-car-2","group":"vehicles","aliases":["Traffic Car","Traffic Cars"],"types":[24,25]},{"key":"atv-carrier-2","group":"vehicles","aliases":["ATV Carrier","ATV Carriers"],"types":[30]},{"key":"primary-response-vehicle","group":"vehicles","aliases":["Primary Response Vehicle","Primary Response Vehicles","PRV","PRVs"],"types":[27]},{"key":"secondary-response-vehicle","group":"vehicles","aliases":["Secondary Response Vehicle","Secondary Response Vehicles","SRV","SRVs"],"types":[28]},{"key":"welfare-vehicle","group":"vehicles","aliases":["Welfare Vehicle","Welfare Vehicles"],"types":[29,39,45,49,115]},{"key":"ambulance-officer-2","group":"vehicles","aliases":["Ambulance Officer","Ambulance Officers"],"types":[34]},{"key":"foam-unit-2","group":"vehicles","aliases":["Foam Unit","Foam Units"],"types":[35,36,37,38,42,75]},{"key":"mass-casualty-equipment","group":"vehicles","aliases":["Mass Casualty Equipment"],"types":[33]},{"key":"mounted-unit","group":"vehicles","aliases":["Mounted Unit","Mounted Units"],"types":[55]},{"key":"4x4-vehicle","group":"vehicles","aliases":["4x4 Vehicle","4x4 Vehicles"],"types":[66,73,93]},{"key":"coastguard-rope-rescue-unit","group":"vehicles","aliases":["Coastguard Rope Rescue Unit","Coastguard Rope Rescue Units"],"types":[59]},{"key":"flood-rescue-unit","group":"vehicles","aliases":["Flood Rescue Unit","Flood Rescue Units"],"types":[61]},{"key":"crv-2","group":"vehicles","aliases":["CRV","CRVs"],"types":[57,58,59]},{"key":"coastguard-commander-2","group":"vehicles","aliases":["Coastguard Commander","Coastguard Commanders"],"types":[60]},{"key":"boat-trailer-or-inland-rescue-boat","group":"vehicles","aliases":["Boat Trailer or Inland Rescue Boat","Boat Trailers or Inland Rescue Boats"],"types":[67,74]},{"key":"ilb-or-alb-2","group":"vehicles","aliases":["ILB or ALB","ILBs or ALBs"],"types":[68,69]},{"key":"ilb-2","group":"vehicles","aliases":["ILB","ILBs"],"types":[68,69]},{"key":"coastguard-rescue-helicopter","group":"vehicles","aliases":["Coastguard Rescue Helicopter","Coastguard Rescue Helicopters"],"types":[64,65]},{"key":"alb-2","group":"vehicles","aliases":["ALB","ALBs"],"types":[69]},{"key":"mud-decontamination-unit","group":"vehicles","aliases":["Mud Decontamination Unit","Mud Decontamination Units"],"types":[62]},{"key":"support-unit-2","group":"vehicles","aliases":["Support Unit","Support Units"],"types":[63]},{"key":"rescue-watercraft-trailer","group":"vehicles","aliases":["Rescue Watercraft (Trailer)","Rescue Watercraft (Trailers)"],"types":[70]},{"key":"coastguard-mud-rescue-unit","group":"vehicles","aliases":["Coastguard Mud Rescue Unit","Coastguard Mud Rescue Units"],"types":[58]},{"key":"hovercraft-trailer","group":"vehicles","aliases":["Hovercraft (trailer)","hovercrafts (trailer)"],"types":[71]},{"key":"major-foam-tender","group":"vehicles","aliases":["Major Foam Tender","Major Foam Tenders"],"types":[75]},{"key":"rescue-stair-2","group":"vehicles","aliases":["Rescue Stair","Rescue Stairs"],"types":[78,2,17]},{"key":"airfield-firefighting-command-vehicle","group":"vehicles","aliases":["Airfield Firefighting Command Vehicle","Airfield Firefighting Command Vehicles"],"types":[77]},{"key":"airfield-operations-vehicle","group":"vehicles","aliases":["Airfield Operations Vehicle","Airfield Operations Vehicles"],"types":[79,80]},{"key":"riv-2","group":"vehicles","aliases":["RIV","RIVs"],"types":[76]},{"key":"medical-equipment-trailer","group":"vehicles","aliases":["Medical equipment trailer","Medical equipment trailers"],"types":[81]},{"key":"airfield-operations-supervisor","group":"vehicles","aliases":["Airfield Operations Supervisor","Airfield Operations Supervisors"],"types":[80]},{"key":"armed-cell-van","group":"vehicles","aliases":["Armed Cell Van","Armed Cell Vans"],"types":[82]},{"key":"medical-cycle-responder","group":"vehicles","aliases":["Medical cycle responder","Medical cycle responders"],"types":[83]},{"key":"community-midwife","group":"vehicles","aliases":["Community Midwife","Community Midwifes"],"types":[95]},{"key":"specialist-paramedic-rrv","group":"vehicles","aliases":["Specialist Paramedic RRV","Specialist Paramedic RRVs"],"types":[96]},{"key":"rescue-dog-2","group":"vehicles","aliases":["Rescue Dog","Rescue Dogs"],"types":[101,102]},{"key":"mountain-rescue-4x4","group":"vehicles","aliases":["Mountain Rescue 4x4"],"types":[99]},{"key":"road-rail-unit","group":"vehicles","aliases":["Road Rail Unit"],"types":[107]},{"key":"eiu-2","group":"vehicles","aliases":["EIU"],"types":[108]},{"key":"eod-commander-2","group":"vehicles","aliases":["EOD Commander","EOD Commanders"],"types":[109]},{"key":"eod-response-vehicle","group":"vehicles","aliases":["EOD Response Vehicle","EOD Response Vehicles"],"types":[110]},{"key":"eod-medium-equipment-van","group":"vehicles","aliases":["EOD Medium Equipment Van","EOD Medium Equipment Vans"],"types":[111]},{"key":"eod-heavy-equipment-vehicle","group":"vehicles","aliases":["EOD Heavy Equipment Vehicle","EOD Heavy Equipment Vehicles"],"types":[112]},{"key":"marine-eod-response-vehicle","group":"vehicles","aliases":["Marine EOD Response Vehicle","Marine EOD Response Vehicles"],"types":[113]},{"key":"marine-eod-equipment-van","group":"vehicles","aliases":["Marine EOD Equipment Van","Marine EOD Equipment Vans"],"types":[114]}].map(definition => Object.freeze({ group: 'vehicles', aliases: [], types: [], equipment: [], factors: {}, ...definition })));
    const MISSION_REQUIREMENT_PARSE_DEFINITIONS = Object.freeze([...MISSION_REQUIREMENT_DEFINITIONS].sort((left, right) => Math.max(...((right.aliases && right.aliases.length) ? right.aliases : ['']).map(value => String(value).length)) - Math.max(...((left.aliases && left.aliases.length) ? left.aliases : ['']).map(value => String(value).length))));

    function missionRequirementsEscapeRegex(value) {
        return String(value || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    function missionRequirementsNumber(value) {
        const digits = String(value ?? '').replace(/[^0-9-]/g, '');
        const number = Number.parseInt(digits, 10);
        return Number.isFinite(number) ? Math.max(0, number) : 0;
    }

    function missionRequirementsOptionalNumber(value) {
        const text = String(value ?? '').trim();
        if (!/\d/u.test(text)) return null;
        return missionRequirementsNumber(text);
    }

    function missionRequirementsCapacity(min = 0, max = min, known = null) {
        const safeMin = Math.max(0, Number(min) || 0);
        let safeMax = max === null || max === undefined ? null : Math.max(safeMin, Number(max) || 0);
        if (safeMax !== null && !Number.isFinite(safeMax)) safeMax = null;
        const exact = known === true ? true : known === false ? false : safeMax !== null && safeMin === safeMax;
        return { min: safeMin, max: safeMax, known: exact, value: safeMin };
    }

    function missionRequirementsCapacityText(capacity) {
        const value = missionRequirementsCapacity(capacity?.min ?? capacity?.value ?? 0, capacity?.max, capacity?.known);
        if (value.known || value.max === value.min) return value.min.toLocaleString('en-GB');
        if (value.max === null) return value.min > 0 ? `${value.min.toLocaleString('en-GB')}+` : '?';
        return `${value.min.toLocaleString('en-GB')}–${value.max.toLocaleString('en-GB')}`;
    }

    function missionRequirementsCoverageRow(requirement, selectedCapacity, respondingCapacity, onSiteCapacity = null, requiredCapacity = null) {
        const missing = Math.max(0, Number(requirement?.missing) || 0);
        const selected = missionRequirementsCapacity(selectedCapacity?.min ?? selectedCapacity?.value ?? 0, selectedCapacity?.max, selectedCapacity?.known);
        const responding = missionRequirementsCapacity(respondingCapacity?.min ?? respondingCapacity?.value ?? 0, respondingCapacity?.max, respondingCapacity?.known);
        const onSite = missionRequirementsCapacity(onSiteCapacity?.min ?? onSiteCapacity?.value ?? 0, onSiteCapacity?.max, onSiteCapacity?.known);
        const derivedRequiredMin = missing + onSite.min;
        const derivedRequiredMax = onSite.max === null ? null : missing + onSite.max;
        const required = requiredCapacity
            ? missionRequirementsCapacity(requiredCapacity?.min ?? requiredCapacity?.value ?? derivedRequiredMin, requiredCapacity?.max, requiredCapacity?.known)
            : missionRequirementsCapacity(derivedRequiredMin, derivedRequiredMax, onSite.known && derivedRequiredMax !== null && derivedRequiredMin === derivedRequiredMax);
        const fulfilledMin = onSite.min + responding.min + selected.min;
        const fulfilledMax = onSite.max === null || responding.max === null || selected.max === null
            ? null
            : onSite.max + responding.max + selected.max;
        const covered = required.max !== null && fulfilledMin >= required.max;
        const definitelyOpen = !covered && fulfilledMax !== null && fulfilledMax < required.min;
        const uncertain = !covered && !definitelyOpen;
        const stillMin = fulfilledMax === null ? 0 : Math.max(0, required.min - fulfilledMax);
        const stillMax = required.max === null ? null : Math.max(0, required.max - fulfilledMin);
        const stillKnown = covered || (stillMax !== null && stillMin === stillMax && required.known && onSite.known && responding.known && selected.known);
        const still = missionRequirementsCapacity(stillMin, stillMax, stillKnown);
        const partial = !covered && fulfilledMin > 0;
        return {
            ...requirement,
            required: required.min,
            requiredMin: required.min,
            requiredMax: required.max,
            requiredKnown: required.known,
            requiredText: missionRequirementsCapacityText(required),
            onSite: onSite.min,
            onSiteMin: onSite.min,
            onSiteMax: onSite.max,
            onSiteKnown: onSite.known,
            onSiteText: missionRequirementsCapacityText(onSite),
            responding: responding.min,
            respondingMin: responding.min,
            respondingMax: responding.max,
            respondingKnown: responding.known,
            respondingText: missionRequirementsCapacityText(responding),
            enRoute: responding.min,
            enRouteMin: responding.min,
            enRouteMax: responding.max,
            enRouteKnown: responding.known,
            enRouteText: missionRequirementsCapacityText(responding),
            selected: selected.min,
            selectedMin: selected.min,
            selectedMax: selected.max,
            selectedKnown: selected.known,
            selectedText: missionRequirementsCapacityText(selected),
            stillNeeded: still.max === null ? still.min : still.max,
            stillNeededMin: still.min,
            stillNeededMax: still.max,
            stillNeededKnown: still.known,
            stillNeededText: missionRequirementsCapacityText(still),
            covered,
            definitelyOpen,
            uncertain,
            partial,
            coverageKnown: covered || definitelyOpen
        };
    }

    function missionRequirementsCleanRemaining(value) {
        return String(value || '')
        .replace(/\b(?:we\s+need|needed|required)\b\s*:*/giu, ' ')
        .replace(/\s*[,;]\s*(?=[,;]|$)/gu, ' ')
        .replace(/^(?:\s|[,;.])+|(?:\s|[,;.])+$/gu, '')
        .replace(/\s+/gu, ' ')
        .trim();
    }

    function missionRequirementsFindDefinitionMatch(text, definition) {
        const aliases = Array.from(new Set([definition.label, ...(definition.aliases || [])]))
        .filter(Boolean)
        .sort((a, b) => b.length - a.length)
        .map(missionRequirementsEscapeRegex);
        if (!aliases.length) return null;
        const numberPattern = '(\\d{1,3}(?:[\\s,.]\\d{3})*|\\d+)';
        const labelPattern = aliases.join('|');
        const prefix = '(^|[,;]\\s*)';
        const suffix = '(?=\\s*(?:[,;]|$))';
        const before = new RegExp(
        `${prefix}\\s*(?:at\\s+least\\s+)?(?:x\\s*)?${numberPattern}\\s*(?:x\\s*)?(${labelPattern})${suffix}`,
            'iu'
        );
        const after = new RegExp(
        `${prefix}\\s*(${labelPattern})\\s*(?::|x)\\s*${numberPattern}${suffix}`,
            'iu'
        );
        const beforeMatch = before.exec(text);
        const afterMatch = after.exec(text);
        const candidates = [];
        if (beforeMatch) candidates.push({
        index: beforeMatch.index,
        length: beforeMatch[0].length,
        missing: missionRequirementsNumber(beforeMatch[2]),
        label: beforeMatch[3]
        });
        if (afterMatch) candidates.push({
        index: afterMatch.index,
        length: afterMatch[0].length,
        missing: missionRequirementsNumber(afterMatch[3]),
        label: afterMatch[2]
        });
        return candidates.sort((a, b) => a.index - b.index || b.length - a.length)[0] || null;
    }

    function missionRequirementsParseText(rawText, group = 'vehicles') { const normalized = missionRequirementsStripNonDemandMetadata(rawText, false) .replace(/\r/g, '') .replace(/\n+/g, '; ') .replace(/\s+/g, ' ') .trim(); if (!normalized) return { requirements: [], remaining: '' }; let working = normalized; const requirements = []; while (true) { let best = null; for (const definition of MISSION_REQUIREMENT_PARSE_DEFINITIONS) { if ((definition.group || 'vehicles') !== group) continue; const found = missionRequirementsFindDefinitionMatch(working, definition); if (!found) continue; if (!best || found.index < best.found.index || (found.index === best.found.index && found.length > best.found.length)) { best = { definition, found }; } } if (!best) break; requirements.push({ key: best.definition.key, requirement: best.definition.label, missing: best.found.missing, group, definition: best.definition, sourceIndex: best.found.index }); working = `${working.slice(0, best.found.index)}${' '.repeat(best.found.length)}${working.slice(best.found.index + best.found.length)}`; } requirements.sort((a, b) => a.sourceIndex - b.sourceIndex); requirements.forEach(requirement => { delete requirement.sourceIndex; }); return { requirements, remaining: missionRequirementsCleanRemaining(working) }; }

    function missionRequirementsElementText(element) {
        if (!element) return '';
        const rendered = typeof element.innerText === 'string' && element.innerText.trim()
        ? element.innerText
        : element.textContent;
        return String(rendered || '').replace(/\u00a0/gu, ' ').trim();
    }

    function missionRequirementsNormalizeGroup(value, fallback = 'vehicles') {
        const normalized = String(value || '').trim().toLowerCase();
        if (normalized === 'personnel' || normalized === 'staff') return 'staff';
        if (normalized === 'other' || normalized === 'resource' || normalized === 'resources') return 'other';
        if (normalized === 'vehicle' || normalized === 'vehicles') return 'vehicles';
        return fallback;
    }

    function missionRequirementsInferGroup(text, fallback = 'vehicles') {
        const normalized = String(text || '').toLowerCase();
        if (/\b(?:missing|required)\s+(?:personnel|staff)\b/.test(normalized)) return 'staff';
        if (/\b(?:officers?|firefighters?|paramedics?|technicians?|commanders?|sergeants?|inspectors?|medics?|advisors?)\b/.test(normalized)) return 'staff';
        if (/\b(?:litres?|liters?|water|foam|pumping\s+capacity|resources?)\b/.test(normalized)) return 'other';
        if (/\b(?:missing|required)\s+vehicles?\b/.test(normalized)) return 'vehicles';
        return fallback;
    }

    function missionRequirementsStripGroupHeading(text) {
        return String(text || '')
        .replace(/^\s*(?:missing|required)\s+(?:vehicles?|personnel|staff|other|resources?)\s*:?\s*/iu, '')
        .trim();
    }

    function missionRequirementsSplitTextSections(rawText, fallback = 'vehicles') {
        const text = String(rawText || '').replace(/\r/g, '').trim();
        if (!text) return [];
        const heading = /(?:^|[\n;])\s*(?:missing|required)\s+(vehicles?|personnel|staff|other|resources?)\s*:?\s*/giu;
        const matches = Array.from(text.matchAll(heading));
        if (!matches.length) return [{ group: missionRequirementsInferGroup(text, fallback), text }];
        const sections = [];
        const prefix = text.slice(0, matches[0].index).trim();
        if (prefix) sections.push({ group: missionRequirementsInferGroup(prefix, fallback), text: prefix });
        matches.forEach((match, index) => {
        const start = match.index + match[0].length;
        const end = index + 1 < matches.length ? matches[index + 1].index : text.length;
        const sectionText = text.slice(start, end).trim();
        if (!sectionText) return;
        sections.push({ group: missionRequirementsNormalizeGroup(match[1], fallback), text: sectionText });
        });
        return sections;
    }

    function missionRequirementsParseGenericText(rawText, group) { let working = missionRequirementsStripNonDemandMetadata(rawText, false).replace(/\r/g, '').replace(/\n+/g, '; ').trim(); if (!working) return { requirements: [], remaining: '' }; const number = '(\\d{1,3}(?:[\\s,.]\\d{3})*|\\d+)'; const patterns = [ { expression: new RegExp(`(^|[,;]\\s*)\\s*(?:at\\s+least\\s+)?(?:x\\s*)?${number}\\s*(?:x\\s*)?\\s+([^,;]+?)(?=\\s*(?:[,;]|$))`, 'giu'), quantity: 2, label: 3 }, { expression: new RegExp(`(^|[,;]\\s*)\\s*([^,;:]+?)\\s*(?::|x)\\s*${number}(?=\\s*(?:[,;]|$))`, 'giu'), quantity: 3, label: 2 } ]; const requirements = []; let serial = 0; for (const pattern of patterns) { pattern.expression.lastIndex = 0; let match; while ((match = pattern.expression.exec(working))) { const missing = missionRequirementsNumber(match[pattern.quantity]); const label = String(match[pattern.label] || '') .replace(/^\s*(?:and\s+)?(?:missing|required)\s+/iu, '') .replace(/\s+/g, ' ') .trim(); const sourceIndex = match.index; if (!missing || !label || missionRequirementsCatalogueModifier(label, String(missing), false).recognized) { working = `${working.slice(0, sourceIndex)}${' '.repeat(match[0].length)}${working.slice(sourceIndex + match[0].length)}`; pattern.expression.lastIndex = sourceIndex + match[0].length; continue; } const slug = label.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 48) || 'requirement'; requirements.push({ key: `unmapped-${slug}-${serial++}`, requirement: label, missing, group, definition: { key: `unmapped-${slug}`, label, aliases: [label], group, types: [], equipment: [], factors: {}, countable: false, generic: true }, sourceIndex }); working = `${working.slice(0, sourceIndex)}${' '.repeat(match[0].length)}${working.slice(sourceIndex + match[0].length)}`; pattern.expression.lastIndex = sourceIndex + match[0].length; } } requirements.sort((a, b) => a.sourceIndex - b.sourceIndex); requirements.forEach(requirement => { delete requirement.sourceIndex; }); return { requirements, remaining: missionRequirementsCleanRemaining(working) }; }

    function missionRequirementsParseSource(source) { const requirements = []; const unresolved = []; const parseSection = (rawText, requestedGroup) => { const group = missionRequirementsNormalizeGroup(requestedGroup, missionRequirementsInferGroup(rawText, 'vehicles')); const cleaned = missionRequirementsStripGroupHeading(rawText); const operational = missionRequirementsStripNonDemandMetadata(cleaned, false); if (!operational) return; const parsed = missionRequirementsParseText(operational, group); requirements.push(...parsed.requirements); const generic = missionRequirementsParseGenericText(parsed.remaining, group); requirements.push(...generic.requirements); if (generic.remaining) unresolved.push({ group, text: generic.remaining }); }; const allGroups = Array.from(source?.querySelectorAll?.('[data-requirement-type]') || []); const groupElements = allGroups.filter(element => { const closest = element.closest?.('#missing_text'); return !closest || closest === source; }); if (groupElements.length) { for (const element of groupElements) { const rawGroup = element.getAttribute?.('data-requirement-type') || element.dataset?.requirementType || 'vehicles'; parseSection(missionRequirementsElementText(element), rawGroup); } } else { const raw = missionRequirementsElementText(source); for (const section of missionRequirementsSplitTextSections(raw, 'vehicles')) parseSection(section.text, section.group); } return { requirements, unresolved }; }

    // Issue #183: merge the authoritative "Requirements for this Mission" catalogue into the live model.
    function missionRequirementsRangeMetadataKey(text) { const match = String(text || '').replace(/\s+/gu, ' ').match(/(?:^|[;])\s*Required\s+minimum\s+(.+?)(?:\s*(?::|—|-)\s*)?Between\s+\d[\d,.]*\s+and\s+\d[\d,.]*/iu); return match ? missionRequirementsCatalogueCapability(match[1])?.key || null : null; }
    function missionRequirementsReconcileCatalogue(parsed, catalogue, state = 'unavailable', expected = false) { const requirements = Array.from(parsed?.requirements || [], item => ({ ...item })); const exactKeys = new Set(requirements.filter(item => item?.statedRequirement !== false && missionRequirementsOptionalNumber(item?.missing) !== null).map(item => item.key)); const unresolved = Array.from(parsed?.unresolved || [], item => ({ ...item })).filter(item => { const key = missionRequirementsRangeMetadataKey(item?.text); return !key || !exactKeys.has(key); }); const byKey = new Map(requirements.map((item, index) => [item.key, index])); for (const item of catalogue?.requirements || []) { const baseline = missionRequirementsOptionalNumber(item?.baseline ?? item?.missing); if (baseline === null) continue; const probability = missionRequirementsOptionalNumber(item.probability) ?? 100; const availabilityOnly = item.availabilityOnly === true; const conditional = probability < 100 || availabilityOnly; const index = byKey.get(item.key); if (index !== undefined) { requirements[index] = { ...requirements[index], catalogueDerived: true, catalogueBaseline: baseline, catalogueProbability: probability, catalogueAvailabilityOnly: availabilityOnly, catalogueConditional: conditional }; continue; } if (conditional && index === undefined) continue; const requirement = { ...item, missing: baseline, baseline, statedRequirement: false, catalogueDerived: true, catalogueProbability: probability, catalogueAvailabilityOnly: availabilityOnly, catalogueConditional: conditional, requirementSource: catalogue?.stale ? 'Cached mission info' : 'Mission info' }; byKey.set(requirement.key, requirements.length); requirements.push(requirement); } const unresolvedSeen = new Set(unresolved.map(item => String(item?.text || '').toLowerCase())); for (const item of catalogue?.unresolved || []) { if (item?.classification === 'informational') continue; const rangeKey = missionRequirementsRangeMetadataKey(`${item?.label || ''} — ${item?.value || ''}`); if (rangeKey && exactKeys.has(rangeKey)) continue; const cleanLabel = missionRequirementsSafeDiagnostic(item?.label || 'Unmapped requirement', 180); const cleanValue = missionRequirementsSafeDiagnostic(item?.value || '', 180); const text = item?.classification === 'operational' ? `${cleanLabel}${cleanValue ? ` — ${cleanValue}` : ''}` : `Mission info: ${cleanLabel}${cleanValue ? ` — ${cleanValue}` : ''}`; if (!unresolvedSeen.has(text.toLowerCase())) { unresolved.push({ group: item?.group || 'other', text, catalogueDerived: true }); unresolvedSeen.add(text.toLowerCase()); } } if (!catalogue && expected) { const text = state === 'loading' || state === 'idle' ? 'Loading Requirements for this Mission…' : 'Requirements for this Mission could not be loaded; verify the mission information manually.'; if (!unresolvedSeen.has(text.toLowerCase())) unresolved.push({ group: 'other', text, authoritativePending: state === 'loading' || state === 'idle' }); } else if (catalogue?.stale) unresolved.push({ group: 'other', text: 'Using cached Requirements for this Mission; verify conditional requirements manually.', catalogueDerived: true }); return { requirements, unresolved }; }



    // Issue #181: patient-derived ambulance demand.
    // Issue #186: broader live patient scope and direct patient conditions.
    const MISSION_REQUIREMENTS_PATIENT_TRANSITION_MS = 1400; const MISSION_REQUIREMENTS_PATIENT_SNAPSHOT_LIMIT = 32; const missionRequirementsPatientSnapshots = new Map();
    function missionRequirementsPatientContext(candidate) { const root = missionRequirementsCandidateRoot(candidate) || candidate?.root || candidate?.mount; const doc = candidate?.source?.ownerDocument || root?.ownerDocument || candidate?.mount?.ownerDocument || null; const windowSelector = '#lightbox_box, #lightbox, .lightbox_content, .modal-body, .modal, [role="dialog"], .ui-dialog-content, .ui-dialog'; const missionSelector = '#mission_form, form[action*="/missions/"], #mission_content, .mission_content, [data-mission-content]'; const scopes = []; const addScope = scope => { if (scope?.querySelector && !scopes.includes(scope)) scopes.push(scope); }; const candidateNodes = [candidate?.source, root, candidate?.root, candidate?.mount].filter(Boolean); candidateNodes.forEach(addScope); for (const node of candidateNodes) { addScope(node.closest?.(missionSelector)); addScope(node.closest?.(windowSelector)); } const findLocal = selector => { for (const scope of scopes) { if (scope.matches?.(selector)) return scope; const found = scope.querySelector?.(selector); if (found?.isConnected !== false) return found; } return null; }; let patientText = findLocal('#patient_button_text'); let patientForm = findLocal('#patient_button_form'); const activeWindow = candidateNodes.map(node => node.closest?.(windowSelector)).find(Boolean) || null; const pickDocumentNode = selector => { if (!doc?.querySelectorAll) return null; const nodes = Array.from(doc.querySelectorAll(selector) || []).filter(node => node?.isConnected !== false); if (activeWindow) { const local = nodes.filter(node => activeWindow === node || activeWindow.contains?.(node) || node.closest?.(windowSelector) === activeWindow); if (local.length === 1) return local[0]; if (local.length > 1) return local.find(node => root?.contains?.(node)) || local[0]; } if (nodes.length === 1) return nodes[0]; return nodes.find(node => root?.contains?.(node)) || null; }; if (!patientText) patientText = pickDocumentNode('#patient_button_text'); if (!patientForm) patientForm = pickDocumentNode('#patient_button_form'); if (!patientForm && patientText) patientForm = patientText.closest?.('#patient_button_form') || patientText.parentNode || null; if (!patientText && patientForm) patientText = patientForm.querySelector?.('#patient_button_text') || null; const detailPattern = /\b(?:critical\s+care\s+required|hems\s+required|requires\s+transport|ambulance\s+with\s+the\s+patient|critical\s+care\s+with\s+the\s+patient)\b/iu; let detailScope = null; let current = patientForm?.parentNode || patientText?.parentNode || null; while (current && current !== doc) { if (detailPattern.test(missionRequirementsElementText(current))) { detailScope = current; break; } if (activeWindow && current === activeWindow) break; current = current.parentNode; } if (!detailScope) { for (const scope of [activeWindow, ...scopes]) { if (scope && detailPattern.test(missionRequirementsElementText(scope))) { detailScope = scope; break; } } } return { root, doc, activeWindow, patientText, patientForm, detailScope }; }
    function missionRequirementsPatientCount(candidate) { const context = missionRequirementsPatientContext(candidate); const patientText = context.patientText; const patientForm = context.patientForm; const holder = patientText || patientForm; if (!holder) return { present: false, known: true, count: 0, source: 'absent', text: '' }; const attributeNames = ['data-patient-count', 'data-patient-total', 'data-patients', 'patient_count', 'patients_count']; for (const scope of Array.from(new Set([patientText, patientForm].filter(Boolean)))) { for (const name of attributeNames) { const value = missionRequirementsOptionalNumber(scope?.getAttribute?.(name)); if (value !== null) return { present: true, known: true, count: value, source: name, text: missionRequirementsElementText(holder) }; } for (const value of [scope?.dataset?.patientCount, scope?.dataset?.patientTotal, scope?.dataset?.patients]) { const parsed = missionRequirementsOptionalNumber(value); if (parsed !== null) return { present: true, known: true, count: parsed, source: 'dataset', text: missionRequirementsElementText(holder) }; } } const strong = patientText?.querySelector?.('strong') || patientForm?.querySelector?.('#patient_button_text strong, strong') || null; const parseTotal = value => { const match = String(value || '').replace(/\u00a0/gu, ' ').match(/\b(\d{1,3}(?:[\s,.]\d{3})*)\s+patients?\b/iu); return match ? missionRequirementsNumber(match[1]) : null; }; const strongCount = parseTotal(missionRequirementsElementText(strong)); if (strongCount !== null) return { present: true, known: true, count: strongCount, source: 'patient-total-strong', text: missionRequirementsElementText(holder) }; const text = missionRequirementsElementText(holder); const textCount = parseTotal(text); if (textCount !== null) return { present: true, known: true, count: textCount, source: 'patient-summary-text', text }; return { present: true, known: false, count: null, source: 'patient-summary-unresolved', text }; }
    function missionRequirementsPatientFlag(text, labelPattern) { const expression = new RegExp(`${labelPattern}\\s*:?\\s*(yes|no)`, 'giu'); let yes = 0; let no = 0; let match; while ((match = expression.exec(text))) { if (String(match[1]).toLowerCase() === 'yes') yes += 1; else no += 1; } return { known: yes + no > 0, yes, no, total: yes + no }; }
    function missionRequirementsPatientDetails(candidate) { const context = missionRequirementsPatientContext(candidate); const text = missionRequirementsElementText(context.detailScope); const normalized = String(text || '').replace(/\u00a0/gu, ' ').replace(/\s+/gu, ' ').trim(); const flags = { criticalCareRequired: missionRequirementsPatientFlag(normalized, 'critical\\s+care\\s+required'), hemsRequired: missionRequirementsPatientFlag(normalized, 'hems\\s+required'), transportRequired: missionRequirementsPatientFlag(normalized, 'requires\\s+transport'), ambulanceWithPatient: missionRequirementsPatientFlag(normalized, 'ambulance\\s+with\\s+the\\s+patient'), criticalCareWithPatient: missionRequirementsPatientFlag(normalized, 'critical\\s+care\\s+with\\s+the\\s+patient') }; return { present: Object.values(flags).some(flag => flag.known), text: normalized, ...flags }; }
    function missionRequirementsPatientSnapshotPrune(now = Date.now()) { for (const [key, snapshot] of missionRequirementsPatientSnapshots) { if (now - (Number(snapshot?.updatedAt) || 0) > 60000) missionRequirementsPatientSnapshots.delete(key); } if (missionRequirementsPatientSnapshots.size <= MISSION_REQUIREMENTS_PATIENT_SNAPSHOT_LIMIT) return; const ordered = Array.from(missionRequirementsPatientSnapshots.entries()).sort((left, right) => (Number(left[1]?.updatedAt) || 0) - (Number(right[1]?.updatedAt) || 0)); for (const [key] of ordered.slice(0, missionRequirementsPatientSnapshots.size - MISSION_REQUIREMENTS_PATIENT_SNAPSHOT_LIMIT)) missionRequirementsPatientSnapshots.delete(key); }
    function missionRequirementsPatientState(record, now = Date.now()) { const candidate = record?.candidate || record; const missionIdentity = missionRequirementsMissionIdentity(candidate, record?.source || candidate?.source); const countState = missionRequirementsPatientCount(candidate); const details = missionRequirementsPatientDetails(candidate); const current = { ...countState, details }; const key = missionIdentity > 0 ? String(missionIdentity) : ''; if (current.present || details.present) { if (record?.patientTransitionTimer) runtimeClearTimeout(record.patientTransitionTimer); if (record) record.patientTransitionTimer = null; if (key) missionRequirementsPatientSnapshots.set(key, { state: { ...current }, updatedAt: now }); missionRequirementsPatientSnapshotPrune(now); return { ...current, missionIdentity, transitional: false }; } const snapshot = key ? missionRequirementsPatientSnapshots.get(key) : null; const age = snapshot ? now - (Number(snapshot.updatedAt) || 0) : Number.POSITIVE_INFINITY; if (snapshot?.state && age >= 0 && age < MISSION_REQUIREMENTS_PATIENT_TRANSITION_MS) { if (record && !record.patientTransitionTimer) { const wait = Math.max(20, MISSION_REQUIREMENTS_PATIENT_TRANSITION_MS - age + 20); record.patientTransitionTimer = runtimeSetTimeout(() => { record.patientTransitionTimer = null; missionRequirementsScheduleRecord(record); }, wait); } return { ...snapshot.state, missionIdentity, transitional: true }; } if (key && snapshot) missionRequirementsPatientSnapshots.delete(key); if (record?.patientTransitionTimer) runtimeClearTimeout(record.patientTransitionTimer); if (record) record.patientTransitionTimer = null; return { ...current, missionIdentity, transitional: false }; }
    function missionRequirementsReconcilePatientDemand(parsed, patientState) { const requirements = Array.from(parsed?.requirements || []).map(requirement => ({ ...requirement })); const unresolved = Array.from(parsed?.unresolved || []).map(item => ({ ...item })); const details = patientState?.details || {}; const patientPresent = patientState?.present === true || patientState?.transitional === true; const patientKnown = patientState?.known === true && Number.isFinite(Number(patientState?.count)); const patientCount = patientKnown ? Math.max(0, Number(patientState.count) || 0) : null; const mergeVehicleDemand = (key, label, required, known, sourceName) => { const definition = MISSION_REQUIREMENT_DEFINITIONS.find(item => item.key === key); if (!definition) return; const indexes = requirements.map((requirement, index) => requirement.key === key ? index : -1).filter(index => index >= 0); const rows = indexes.map(index => requirements[index]); const statedMissing = rows.reduce((maximum, requirement) => Math.max(maximum, Math.max(0, Number(requirement?.missing) || 0)), 0); for (const duplicateIndex of indexes.slice(1).reverse()) requirements.splice(duplicateIndex, 1); const index = indexes.length ? indexes[0] : requirements.length; const base = rows[0] || { key, requirement: label, missing: required ?? 0, group: 'vehicles', definition }; const row = { ...base, missing: rows.length ? statedMissing : (required ?? 0), group: 'vehicles', definition, patientDerived: true, patientCountKnown: known, patientRequired: required, statedRequirement: rows.length > 0, requirementSource: sourceName }; if (index < requirements.length) requirements[index] = row; else requirements.push(row); }; if (patientPresent && (!patientKnown || patientCount > 0)) { mergeVehicleDemand('ambulance', 'Ambulance', patientCount, patientKnown, 'Patients'); if (!patientKnown && !unresolved.some(item => item?.patientDerived)) unresolved.push({ group: 'vehicles', text: 'Patient total is present but could not be determined.', patientDerived: true }); } const hemsRequired = Math.max(0, Number(details?.hemsRequired?.yes) || 0); if (hemsRequired > 0) mergeVehicleDemand('hems', 'HEMS', hemsRequired, true, 'Patient details'); const mergeCondition = (key, label, requiredFlag, fulfilledFlag) => { const required = Math.max(0, Number(requiredFlag?.yes) || 0, Number(fulfilledFlag?.yes) || 0); if (!required) return; const definition = MISSION_REQUIREMENT_DEFINITIONS.find(item => item.key === key) || { key, label, aliases: [label], group: 'other', types: [], countable: true, patientCondition: true }; const indexes = requirements.map((requirement, index) => requirement.key === key ? index : -1).filter(index => index >= 0); const rows = indexes.map(index => requirements[index]); for (const duplicateIndex of indexes.slice(1).reverse()) requirements.splice(duplicateIndex, 1); const index = indexes.length ? indexes[0] : requirements.length; const existingRequired = rows.reduce((maximum, requirement) => Math.max(maximum, Math.max(0, Number(requirement?.missing) || 0)), 0); const row = { ...(rows[0] || {}), key, requirement: label, missing: Math.max(existingRequired, required), group: 'other', definition, patientDerived: true, patientCondition: true, patientConditionRequired: Math.max(existingRequired, required), patientConditionFulfilled: Math.max(0, Number(fulfilledFlag?.yes) || 0), patientConditionFulfilledKnown: fulfilledFlag?.known === true, statedRequirement: rows.length > 0, requirementSource: 'Patient details' }; if (index < requirements.length) requirements[index] = row; else requirements.push(row); }; mergeCondition('critical-care-patient', 'Critical Care', details?.criticalCareRequired, details?.criticalCareWithPatient); mergeCondition('patient-transport', 'Patient Transport', details?.transportRequired, details?.ambulanceWithPatient); return { requirements, unresolved, patientState }; }
function missionRequirementsVehicleType(element) { const scopes = []; const addScope = scope => { if (scope && !scopes.includes(scope)) scopes.push(scope); }; addScope(element); addScope(element?.closest?.('tr')); addScope(element?.closest?.('[vehicle_type_id], [data-vehicle-type-id], [data-vehicle_type_id]')); const read = scope => missionRequirementsOptionalNumber( scope?.getAttribute?.('vehicle_type_id') ?? scope?.getAttribute?.('data-vehicle-type-id') ?? scope?.getAttribute?.('data-vehicle_type_id') ?? scope?.dataset?.vehicleTypeId ?? scope?.dataset?.vehicle_type_id ); for (const scope of scopes) { const direct = read(scope); if (direct !== null && direct >= 0) return direct; const nested = scope?.querySelector?.('[vehicle_type_id], [data-vehicle-type-id], [data-vehicle_type_id]'); const nestedType = read(nested); if (nestedType !== null && nestedType >= 0) return nestedType; } const vehicleId = missionRequirementsVehicleId(element); const custom = vehicleId >= 0 && typeof customVehicleClassificationForId === 'function' ? customVehicleClassificationForId(vehicleId) : null; const customType = missionRequirementsOptionalNumber(custom?.baseTypeId); return customType !== null && customType >= 0 ? customType : -1; }

    function missionRequirementsVehicleId(element) {
        const scopes = Array.from(new Set([element, element?.closest?.('tr')].filter(Boolean)));
        const attributes = ['vehicle_id', 'data-vehicle-id', 'data-vehicle_id'];
        for (const scope of scopes) {
        for (const raw of [scope?.value, scope?.getAttribute?.('value'), scope?.dataset?.vehicleId, scope?.dataset?.vehicle_id]) {
            const value = Number.parseInt(raw, 10);
            if (Number.isFinite(value) && value >= 0) return value;
        }
        for (const attribute of attributes) {
            const value = Number.parseInt(scope?.getAttribute?.(attribute), 10);
            if (Number.isFinite(value) && value >= 0) return value;
        }
        const idMatch = String(scope?.id || '').match(/(?:^|[_-])vehicle[_-]?(\d+)(?:$|[_-])/iu);
        if (idMatch) return Number(idMatch[1]);
        const link = scope?.matches?.('a[href*="/vehicles/"]') ? scope : scope?.querySelector?.('a[href*="/vehicles/"]');
        const hrefMatch = String(link?.getAttribute?.('href') || link?.href || '').match(/\/vehicles\/(\d+)(?:\/|$)/u);
        if (hrefMatch) return Number(hrefMatch[1]);
        }
        return -1;
    }

    function missionRequirementsEquipmentTypes(element) {
        const values = new Set();
        const add = raw => String(raw || '').split(',').map(value => value.trim().toLowerCase()).filter(Boolean).forEach(value => values.add(value));
        const scopes = Array.from(new Set([element, element?.closest?.('tr')].filter(Boolean)));
        for (const scope of scopes) {
        add(scope?.dataset?.equipmentType);
        add(scope?.dataset?.equipmentTypes);
        add(scope?.getAttribute?.('data-equipment-type'));
        add(scope?.getAttribute?.('data-equipment-types'));
        scope?.querySelectorAll?.('[data-equipment-type], [data-equipment-types]').forEach(node => {
            add(node.getAttribute('data-equipment-type'));
            add(node.getAttribute('data-equipment-types'));
        });
        }
        return values;
    }

function missionRequirementsCapabilityLabel(value) { return String(value || '') .replace(/\u00a0/gu, ' ') .replace(/&/gu, ' and ') .replace(/\([^)]*\)/gu, ' ') .replace(/[^a-z0-9]+/giu, ' ') .replace(/\s+/gu, ' ') .trim() .toLowerCase(); } function missionRequirementsMetadataValues(element, kind = 'labels') { const values = new Set(); const add = raw => String(raw || '').split(/[,;|]/u).map(missionRequirementsCapabilityLabel).filter(Boolean).forEach(value => values.add(value)); const row = element?.closest?.('tr') || element; const scopes = Array.from(new Set([element, row].filter(Boolean))); const attributes = kind === 'training' ? ['data-personnel-training', 'data-training', 'data-trainings', 'data-education', 'data-educations', 'data-education-name', 'data-education-key', 'data-filterable-by'] : ['data-mcms-custom-vehicle-category', 'data-custom-vehicle-category', 'data-vehicle-category', 'data-vehicle-type-name', 'data-vehicle-type']; for (const scope of scopes) { for (const attribute of attributes) add(scope?.getAttribute?.(attribute)); scope?.querySelectorAll?.(attributes.map(attribute => `[${attribute}]`).join(', ')).forEach(node => attributes.forEach(attribute => add(node.getAttribute?.(attribute)))); } if (kind === 'labels') { const typeCell = row?.querySelector?.('[data-column="vehicle-type"], [data-vehicle-type-name], td:nth-of-type(2)'); add(missionRequirementsElementText(typeCell)); const vehicleId = missionRequirementsVehicleId(element); const custom = vehicleId >= 0 && typeof customVehicleClassificationForId === 'function' ? customVehicleClassificationForId(vehicleId) : null; add(custom?.category); } return values; } function missionRequirementsDefinitionTokens(definition, property = 'aliases') { const raw = property === 'training' ? Array.from(definition?.training || []) : [definition?.label, ...(definition?.aliases || [])]; return new Set(raw.map(missionRequirementsCapabilityLabel).filter(Boolean)); } function missionRequirementsDefinitionMatchesValues(definition, values, property = 'aliases') { if (!values?.size) return false; const tokens = missionRequirementsDefinitionTokens(definition, property); for (const value of values) if (tokens.has(value)) return true; return false; } function missionRequirementsKnownDefinitionKeys(labels) { const keys = new Set(); for (const definition of MISSION_REQUIREMENT_DEFINITIONS) { if ((definition?.group || 'vehicles') === 'staff') continue; if (missionRequirementsDefinitionMatchesValues(definition, labels)) keys.add(definition.key); } return keys; }
function missionRequirementsPositiveCapabilityValue(raw) { if (raw === null || raw === undefined) return false; const value = String(raw).trim().toLowerCase(); if (!value || ['0', 'false', 'no', 'off', 'null', 'undefined'].includes(value)) return false; const numeric = Number(value.replace(/,/gu, '')); return Number.isFinite(numeric) ? numeric > 0 : true; }
function missionRequirementsArrCapabilityState(element, candidate = null, vehicleId = -1) { const values = new Set(); const counts = new Map(); let authoritative = false; const attributes = Array.from(new Set(MISSION_REQUIREMENT_DEFINITIONS.flatMap(definition => Array.from(definition?.arrAttributes || [])).map(attribute => String(attribute || '').trim()).filter(attribute => /^[a-z0-9_:-]+$/iu.test(attribute)))); if (!attributes.length) return { values, counts, authoritative }; const inspect = scope => { if (!scope?.getAttribute) return; let present = false; for (const attribute of attributes) { const raw = scope.getAttribute(attribute); if (raw === null || raw === undefined) continue; present = true; if (!missionRequirementsPositiveCapabilityValue(raw)) continue; const token = missionRequirementsCapabilityLabel(attribute); const numeric = missionRequirementsOptionalNumber(raw); const count = numeric === null ? 1 : Math.max(0, numeric); values.add(token); if (count > 0) counts.set(token, Math.max(counts.get(token) || 0, count)); } if (present) authoritative = true; }; const inspectTree = scope => { if (!scope) return; inspect(scope); const selector = attributes.map(attribute => `[${attribute}]`).join(', '); for (const node of Array.from(scope.querySelectorAll?.(selector) || [])) inspect(node); }; const row = element?.matches?.('tr') ? element : element?.closest?.('tr') || null; inspectTree(element); if (row && row !== element) inspectTree(row); const numericVehicleId = Number(vehicleId); if (Number.isFinite(numericVehicleId) && numericVehicleId >= 0) { const selector = `.vehicle_checkbox[value="${numericVehicleId}"], input[value="${numericVehicleId}"][vehicle_type_id], [data-vehicle-id="${numericVehicleId}"], [vehicle_id="${numericVehicleId}"]`; const scopes = Array.from(new Set([candidate?.root, candidate?.mount, candidate?.source?.ownerDocument, row?.ownerDocument, element?.ownerDocument].filter(scope => scope?.querySelectorAll))); for (const scope of scopes) for (const node of Array.from(scope.querySelectorAll(selector) || [])) inspectTree(node); } if (element?.matches?.('.vehicle_checkbox') || element?.classList?.contains?.('vehicle_checkbox') || (typeof element?.checked === 'boolean' && element?.getAttribute?.('vehicle_type_id') !== null)) authoritative = true; return { values, counts, authoritative }; }


const MISSION_REQUIREMENTS_DEFAULT_STAFF_BY_TYPE = Object.freeze({"0":[1,9],"1":[1,5],"2":[1,3],"3":[1,3],"4":[1,5],"5":[1,2],"6":[1,3],"7":[1,6],"8":[1,2],"9":[3,5],"12":[1,2],"13":[1,4],"14":[1,3],"15":[1,6],"16":[1,9],"17":[1,6],"18":[1,1],"19":[1,3],"20":[1,1],"23":[1,12],"24":[1,2],"25":[1,2],"26":[1,3],"27":[1,2],"28":[1,2],"31":[1,2],"34":[1,1],"35":[1,2],"36":[1,2],"37":[2,9],"38":[2,9],"39":[1,6],"40":[1,2],"51":[1,9],"52":[1,9],"53":[1,4],"55":[1,8],"56":[1,6],"81":[0,0],"82":[1,2],"83":[1,1],"85":[1,3],"86":[1,3],"87":[0,0],"92":[1,1],"93":[1,1],"95":[1,2],"96":[1,2],"99":[1,4],"100":[1,3],"101":[1,1],"102":[1,1],"116":[1,5]});
function missionRequirementsDefaultStaffCapacity(typeId, element = null, record = null) { const range = MISSION_REQUIREMENTS_DEFAULT_STAFF_BY_TYPE[typeId] || MISSION_REQUIREMENTS_DEFAULT_STAFF_BY_TYPE[String(typeId)]; if (!Array.isArray(range) || range.length < 2) return null; const row = element?.closest?.('tr') || element; const scopes = Array.from(new Set([element, row].filter(Boolean))); const overrideAttributes = ['data-max-personnel-override', 'data-personnel-max-override', 'data-max-crew-override']; let maximumOverride = missionRequirementsOptionalNumber(record?.['max_' + 'personnel_override'] ?? record?.maxPersonnelOverride ?? record?.personnel_max_override ?? record?.personnelMaxOverride); for (const scope of scopes) { if (maximumOverride !== null) break; for (const attribute of overrideAttributes) { const value = missionRequirementsOptionalNumber(scope?.getAttribute?.(attribute)); if (value !== null) { maximumOverride = value; break; } } } const minimum = Math.max(0, Number(range[0]) || 0); const configuredMaximum = Math.max(minimum, Number(range[1]) || 0); const maximum = maximumOverride === null ? configuredMaximum : Math.max(minimum, maximumOverride); return missionRequirementsCapacity(minimum, maximum, minimum === maximum); }

    function missionRequirementsVehicleApiRecord(vehicleId) { const id = Number(vehicleId); if (!Number.isFinite(id) || id < 0) return null; return personalVehicleApiCache.get(String(id)) || personalVehicleApiCache.get(id) || null; }
    function missionRequirementsVehicleApiStaff(record) { const assigned = missionRequirementsOptionalNumber(record?.assigned_personnel_count ?? record?.assignedPersonnelCount ?? record?.personnel_count ?? (Array.isArray(record?.personnel) ? record.personnel.length : null) ?? (Array.isArray(record?.assigned_personnel) ? record.assigned_personnel.length : null)); if (assigned === null) return null; return missionRequirementsCapacity(assigned, assigned, true); }
    function missionRequirementsEnsureSharedVehicleData() { if (vehicleApiReady || vehicleApiFetchPromise) return; Promise.resolve(refreshPersonalVehicleData(false)).then(ready => { if (ready && !runtime.destroyed && state.missionRequirements) scheduleMissionRequirementsScan(0); }).catch(() => {}); }
    function missionRequirementsResolvedVehicleType(vehicleId, element) { const detected = missionRequirementsVehicleType(element); if (detected >= 0) return detected; const record = missionRequirementsVehicleApiRecord(vehicleId); const recordType = missionRequirementsOptionalNumber(record?.vehicle_type ?? record?.vehicleType ?? record?.vehicle_type_id ?? record?.vehicleTypeId); return recordType === null ? -1 : recordType; }
    function missionRequirementsResolvedStaffCapacity(vehicleId, typeId, element, mode = '') { const operational = missionRequirementsOperationalCrewCapacity(element, mode); if (operational) return operational; const native = missionRequirementsStaffCapacity(element); if (native?.known) return native; const record = missionRequirementsVehicleApiRecord(vehicleId); const exact = missionRequirementsVehicleApiStaff(record); if (exact) return exact; missionRequirementsEnsureSharedVehicleData(); return native || missionRequirementsDefaultStaffCapacity(typeId, element, record); }


function missionRequirementsLinkedTrainingValues(candidate, vehicleId, element) {
        const values = missionRequirementsMetadataValues(element, 'training');
        const numericVehicleId = Number(vehicleId);
        if (!Number.isFinite(numericVehicleId) || numericVehicleId < 0) return values;
        const row = element?.matches?.('tr') ? element : element?.closest?.('tr') || null;
        const selector = `.vehicle_checkbox[value="${numericVehicleId}"], input[value="${numericVehicleId}"][vehicle_type_id], [data-vehicle-id="${numericVehicleId}"], [vehicle_id="${numericVehicleId}"]`;
        const scopes = Array.from(new Set([
            candidate?.root,
            candidate?.mount,
            candidate?.source?.ownerDocument,
            row?.ownerDocument,
            element?.ownerDocument
        ].filter(scope => scope?.querySelectorAll)));
        for (const scope of scopes) {
            for (const node of Array.from(scope.querySelectorAll(selector) || [])) {
                for (const qualification of missionRequirementsMetadataValues(node, 'training')) values.add(qualification);
                const linkedRow = node?.matches?.('tr') ? node : node?.closest?.('tr') || null;
                const badges = Array.from(String(linkedRow?.textContent || linkedRow?.innerText || '').matchAll(/\[([^\]]+)\]/gu))
                    .map(match => missionRequirementsCapabilityLabel(match[1]))
                    .filter(Boolean);
                for (const badge of badges) values.add(badge);
            }
        }
        return values;
    }
    function missionRequirementsDirectTrainingValues(element) { const values = new Set(); const add = raw => { const visit = value => { if (Array.isArray(value)) return value.forEach(visit); if (value && typeof value === 'object') return ['key', 'name', 'caption', 'title', 'education', 'training'].forEach(field => visit(value[field])); String(value || '').split(/[,;|]/u).map(missionRequirementsCapabilityLabel).filter(Boolean).forEach(value => values.add(value)); }; visit(raw); }; const attributes = ['data-personnel-training', 'data-training', 'data-trainings', 'data-education', 'data-educations', 'data-education-name', 'data-education-key', 'data-filterable-by']; for (const attribute of attributes) add(element?.getAttribute?.(attribute)); return values; }
    function missionRequirementsQualifiedStaffCounts(candidate, vehicleId, element, arrState = null) { const totals = new Map(); const seenNodes = new Set(); const seenEntities = new Map(); const definitions = MISSION_REQUIREMENT_DEFINITIONS.filter(definition => (definition?.group || 'vehicles') === 'staff' && definition.requireExplicitTraining === true); const add = (definition, count, identity = null, mode = 'sum') => { const numeric = Math.max(0, Number(count) || 0); if (!numeric) return; if (identity !== null) { const identities = seenEntities.get(definition.key) || new Set(); if (identities.has(identity)) return; identities.add(identity); seenEntities.set(definition.key, identities); } const current = totals.get(definition.key) || 0; totals.set(definition.key, mode === 'max' ? Math.max(current, numeric) : current + numeric); }; for (const [token, count] of arrState?.counts || []) for (const definition of definitions) { const tokens = new Set(Array.from(definition.arrAttributes || []).map(missionRequirementsCapabilityLabel).filter(Boolean)); if (tokens.has(token)) add(definition, count, `arr:${definition.key}`, 'max'); } const inspect = node => { if (!node || seenNodes.has(node)) return; seenNodes.add(node); const values = missionRequirementsDirectTrainingValues(node); if (!values.size) return; const explicit = missionRequirementsOptionalNumber(node.getAttribute?.('data-qualified-personnel-count') ?? node.getAttribute?.('data-personnel-count') ?? node.getAttribute?.('data-assigned-personnel-count') ?? node.getAttribute?.('data-count')); const identity = node.getAttribute?.('data-personnel-id') ?? node.getAttribute?.('personnel_id') ?? node.getAttribute?.('data-person-id') ?? null; for (const definition of definitions) if (missionRequirementsDefinitionMatchesValues(definition, values, 'training')) add(definition, explicit ?? 1, identity === null ? node : `person:${identity}`); }; const inspectTree = scope => { inspect(scope); const selector = '[data-personnel-training], [data-training], [data-trainings], [data-education], [data-educations], [data-education-name], [data-education-key], [data-filterable-by]'; for (const node of Array.from(scope?.querySelectorAll?.(selector) || [])) inspect(node); }; const row = element?.matches?.('tr') ? element : element?.closest?.('tr') || null; inspectTree(element); if (row && row !== element) inspectTree(row); const numericVehicleId = Number(vehicleId); if (Number.isFinite(numericVehicleId) && numericVehicleId >= 0) { const selector = `.vehicle_checkbox[value="${numericVehicleId}"], input[value="${numericVehicleId}"][vehicle_type_id], [data-vehicle-id="${numericVehicleId}"], [vehicle_id="${numericVehicleId}"]`; const scopes = Array.from(new Set([candidate?.root, candidate?.mount, candidate?.source?.ownerDocument, row?.ownerDocument, element?.ownerDocument].filter(scope => scope?.querySelectorAll))); for (const scope of scopes) for (const node of Array.from(scope.querySelectorAll(selector) || [])) inspectTree(node); const record = missionRequirementsVehicleApiRecord(numericVehicleId); const people = [record?.personnel, record?.assigned_personnel, record?.assignedPersonnel, record?.crew, record?.staff].find(Array.isArray) || []; people.forEach((person, index) => { const values = new Set(); const ingest = raw => { const visit = value => { if (Array.isArray(value)) return value.forEach(visit); if (value && typeof value === 'object') return ['key', 'name', 'caption', 'title', 'education', 'training'].forEach(field => visit(value[field])); String(value || '').split(/[,;|]/u).map(missionRequirementsCapabilityLabel).filter(Boolean).forEach(value => values.add(value)); }; visit(raw); }; ['education', 'educations', 'training', 'trainings', 'schooling', 'schoolings', 'qualifications'].forEach(field => ingest(person?.[field])); const identity = person?.id ?? person?.personnel_id ?? person?.personnelId ?? index; for (const definition of definitions) if (missionRequirementsDefinitionMatchesValues(definition, values, 'training')) add(definition, 1, `api:${identity}`); }); } return new Map(Array.from(totals, ([key, count]) => [key, missionRequirementsCapacity(count, count, true)])); }

    function missionRequirementsOperationalCrewCapacity(element, mode = '') { const row = element?.matches?.('tr') ? element : element?.closest?.('tr') || null; if (!row || !['responding', 'onsite'].includes(mode)) return null; const selector = mode === 'onsite' ? '#mission_vehicle_at_mission, tbody#mission_vehicle_at_mission' : '#mission_vehicle_driving, tbody#mission_vehicle_driving'; if (!row.closest?.(selector)) return null; const crewCell = row.querySelector?.('td:nth-of-type(5)[sortvalue]'); const value = missionRequirementsOptionalNumber(crewCell?.getAttribute?.('sortvalue')); return value === null ? null : missionRequirementsCapacity(value, value, true); }
    function missionRequirementsRespondingCrewCapacity(element) { return missionRequirementsOperationalCrewCapacity(element, 'responding'); }

    function missionRequirementsStaffCapacity(element) {
        const row = element?.closest?.('tr') || element;
        const semanticSelectors = [
            '[data-personnel-count]',
            '[data-current-personnel]',
            '[data-assigned-personnel-count]',
            '[data-assigned_personnel_count]',
            '[assigned_personnel_count]',
            '[data-min-personnel]',
            '[data-max-personnel]',
            '[data-min-crew]',
            '[data-max-crew]',
            '[data-column="crew"]',
            '[data-column="personnel"]',
            '[data-column="staff"]'
        ];
        let crewCell = null;
        for (const selector of semanticSelectors) {
            crewCell = row?.querySelector?.(selector) || null;
            if (crewCell) break;
        }
        const scopes = Array.from(new Set([element, row, crewCell].filter(Boolean)));
        const exactAttributes = ['data-personnel-count', 'data-current-personnel', 'data-assigned-personnel-count', 'data-assigned_personnel_count', 'assigned_personnel_count', 'data-personnel', 'data-staff', 'data-crew'];
        for (const scope of scopes) {
            for (const attribute of exactAttributes) {
                const value = missionRequirementsOptionalNumber(scope.getAttribute?.(attribute));
                if (value !== null) return missionRequirementsCapacity(value, value, true);
            }
        }
        let min = null;
        let max = null;
        for (const scope of scopes) {
            if (min === null) min = missionRequirementsOptionalNumber(scope.getAttribute?.('data-min-personnel') ?? scope.getAttribute?.('data-min-crew'));
            if (max === null) max = missionRequirementsOptionalNumber(scope.getAttribute?.('data-max-personnel') ?? scope.getAttribute?.('data-max-crew'));
        }
        if (min !== null || max !== null) return missionRequirementsCapacity(min ?? 0, max, min !== null && max !== null && min === max);
        const parseCrewText = cell => {
            const text = String(cell?.textContent || '').trim();
            const currentMaximum = text.match(/(\d[\d,.]*)\s*\/\s*(\d[\d,.]*)/u);
            if (currentMaximum) {
                const current = missionRequirementsNumber(currentMaximum[1]);
                return missionRequirementsCapacity(current, current, true);
            }
            const bounded = text.match(/(\d[\d,.]*)\s*(?:-|–|to)\s*(\d[\d,.]*)/iu);
            if (bounded) return missionRequirementsCapacity(missionRequirementsNumber(bounded[1]), missionRequirementsNumber(bounded[2]), false);
            return null;
        };
        const semanticTextCapacity = parseCrewText(crewCell);
        if (semanticTextCapacity) return semanticTextCapacity;
        for (const cell of Array.from(row?.querySelectorAll?.('td, th') || [])) {
            const capacity = parseCrewText(cell);
            if (capacity) return capacity;
        }
        if (crewCell) {
            const visible = missionRequirementsOptionalNumber(String(crewCell.textContent || '').trim());
            if (visible !== null) return missionRequirementsCapacity(visible, visible, true);
            const sortValue = missionRequirementsOptionalNumber(crewCell.getAttribute?.('sortvalue'));
            if (sortValue !== null) return missionRequirementsCapacity(sortValue, sortValue, true);
        }
        return null;
    } function missionRequirementsOperationalSelectors(mode) { if (mode === 'selected') return ['#vehicle_show_table_body_all .vehicle_checkbox:checked, #occupied .vehicle_checkbox:checked, .vehicle_checkbox:checked']; if (mode === 'onsite') return ['#mission_vehicle_at_mission tbody tr', 'tbody#mission_vehicle_at_mission > tr', '#mission_vehicle_at_mission > tr', '[data-mcms-vehicle-state="onsite"]']; return ['#mission_vehicle_driving tbody tr', 'tbody#mission_vehicle_driving > tr', '#mission_vehicle_driving > tr', '[data-mcms-vehicle-state="responding"]']; }
function missionRequirementsOperationalWindowScopes(candidate, context = missionRequirementsPatientContext(candidate)) { const windowSelector = '#lightbox_box, #lightbox, .lightbox_content, .modal-body, .modal, [role="dialog"], .ui-dialog-content, .ui-dialog'; const scopes = []; const addChain = origin => { let current = origin?.closest?.(windowSelector) || null; while (current && !scopes.includes(current)) { scopes.push(current); const parent = current.parentElement || current.parentNode; current = parent?.closest?.(windowSelector) || null; } }; [candidate?.root, candidate?.mount, candidate?.source, missionRequirementsCandidateRoot(candidate), context?.activeWindow].forEach(addChain); if (context?.activeWindow && !scopes.includes(context.activeWindow)) scopes.unshift(context.activeWindow); return scopes; }
function missionRequirementsOperationalCanonicalStateContainer(element, mode) {
        if (mode === 'selected') return null;
        const row = element?.matches?.('tr') ? element : element?.closest?.('tr') || element;
        if (!row) return null;
        const selectors = mode === 'onsite'
            ? ['#mission_vehicle_at_mission', 'tbody#mission_vehicle_at_mission']
            : ['#mission_vehicle_driving', 'tbody#mission_vehicle_driving'];
        for (const selector of selectors) {
            if (row.matches?.(selector)) return row;
            const container = row.closest?.(selector);
            if (container) return container;
        }
        return null;
    }

    function missionRequirementsOperationalElementActive(element, candidate, context = missionRequirementsPatientContext(candidate), mode = '') {
        if (!element || element.isConnected === false) return false;
        if (mode === 'selected' && typeof element.checked === 'boolean' && !element.checked) return false;
        const row = element.matches?.('tr') ? element : element.closest?.('tr') || element;
        const expectedMission = missionRequirementsMissionIdentity(candidate, candidate?.source);
        const canonicalContainer = missionRequirementsOperationalCanonicalStateContainer(row, mode);
        const candidateRoot = missionRequirementsCandidateRoot(candidate) || candidate?.root || candidate?.mount;
        const canonicalId = mode === 'onsite' ? 'mission_vehicle_at_mission' : 'mission_vehicle_driving';
        const documentCanonical = mode === 'selected' ? null : context?.doc?.getElementById?.(canonicalId);
        const pathname = String(context?.doc?.defaultView?.location?.pathname || '');
        const pathMission = missionRequirementsOptionalNumber(pathname.match(/\/missions\/(\d+)/u)?.[1]);
        const canonicalOwned = Boolean(canonicalContainer && (
            context?.activeWindow?.contains?.(row)
            || candidateRoot?.contains?.(row)
            || candidate?.root?.contains?.(row)
            || candidate?.mount?.contains?.(row)
            || (
                expectedMission > 0
                && pathMission === expectedMission
                && documentCanonical
                && (documentCanonical === canonicalContainer || documentCanonical.contains?.(row))
            )
        ));
        if (mode !== 'selected' && !canonicalOwned && !isVisible(element)) return false;
        if (context.activeWindow && !(
            context.activeWindow === row
            || context.activeWindow.contains?.(row)
            || row.closest?.('#lightbox_box, #lightbox, .lightbox_content, .modal-body, .modal, [role="dialog"], .ui-dialog-content, .ui-dialog') === context.activeWindow
        )) return false;
        const explicitMission = missionRequirementsOptionalNumber(row?.getAttribute?.('data-mission-id') ?? row?.dataset?.missionId);
        if (expectedMission > 0 && explicitMission !== null && explicitMission !== expectedMission) return false;
        const missionRoot = row.closest?.('#mission_form, form[action*="/missions/"], #mission_content, .mission_content, [data-mission-content]');
        if (expectedMission > 0 && missionRoot) {
            const actualMission = missionRequirementsMissionIdentity({ root: missionRoot, mount: missionRoot }, null);
            if (actualMission > 0 && actualMission !== expectedMission) return false;
        }
        return true;
    }
const MISSION_REQUIREMENTS_TRACTIVE_TYPES = Object.freeze({"84":[0,1,4],"87":[85,86,89,94],"88":[85,86,89,94]});
function missionRequirementsCollectUnits(candidate, mode) { const root = candidate?.root; const context = missionRequirementsPatientContext(candidate); const doc = context.doc || candidate?.source?.ownerDocument || root?.ownerDocument; if (!root?.querySelectorAll && !doc?.querySelectorAll) return []; const selectors = missionRequirementsOperationalSelectors(mode); const windowScopes = missionRequirementsOperationalWindowScopes(candidate, context); const anchorSelector = mode === 'selected' ? '#vehicle_show_table_body_all, #occupied, .vehicle_checkbox' : mode === 'onsite' ? '#mission_vehicle_at_mission, [data-mcms-vehicle-state="onsite"]' : '#mission_vehicle_driving, [data-mcms-vehicle-state="responding"]'; let activeWindow = context.activeWindow || null; for (const scope of windowScopes) { if (scope?.querySelector?.(anchorSelector)) { activeWindow = scope; break; } } const operationalContext = { ...context, activeWindow }; const elements = []; const seenElements = new Set(); const localScopes = Array.from(new Set([root, candidate?.mount, activeWindow, ...windowScopes].filter(scope => scope?.querySelectorAll))); const search = scope => { for (const selector of selectors) { for (const element of Array.from(scope?.querySelectorAll?.(selector) || [])) { if (seenElements.has(element) || !missionRequirementsOperationalElementActive(element, candidate, operationalContext, mode)) continue; seenElements.add(element); elements.push(element); } } }; localScopes.forEach(search); if (!elements.length && doc?.querySelectorAll && !localScopes.includes(doc)) search(doc); const units = new Map(); elements.forEach((element, index) => { const row = element.matches?.('tr') ? element : element.closest?.('tr'); const vehicleElement = mode === 'selected' ? element : (element.querySelector?.('[vehicle_type_id], [data-vehicle-type-id], [data-vehicle_type_id], [data-vehicle-id], a[href*="/vehicles/"]') || element); const vehicleId = missionRequirementsVehicleId(vehicleElement); const typeId = missionRequirementsResolvedVehicleType(vehicleId, vehicleElement); const tractiveId = missionRequirementsOptionalNumber(vehicleElement?.getAttribute?.('tractive_vehicle_id') ?? vehicleElement?.getAttribute?.('data-tractive-vehicle-id') ?? row?.getAttribute?.('tractive_vehicle_id') ?? row?.getAttribute?.('data-tractive-vehicle-id') ?? row?.dataset?.tractiveVehicleId); const trailerId = missionRequirementsOptionalNumber(vehicleElement?.getAttribute?.('trailer_id') ?? vehicleElement?.getAttribute?.('data-trailer-id') ?? row?.getAttribute?.('trailer_id') ?? row?.getAttribute?.('data-trailer-id') ?? row?.dataset?.trailerId); const tractiveRandom = String(vehicleElement?.getAttribute?.('tractive_random') ?? vehicleElement?.getAttribute?.('data-tractive-random') ?? row?.getAttribute?.('tractive_random') ?? row?.getAttribute?.('data-tractive-random') ?? row?.dataset?.tractiveRandom ?? '') === '1'; const explicitTractiveType = missionRequirementsOptionalNumber(vehicleElement?.getAttribute?.('tractive_vehicle_type_id') ?? vehicleElement?.getAttribute?.('data-tractive-vehicle-type-id') ?? row?.getAttribute?.('tractive_vehicle_type_id') ?? row?.getAttribute?.('data-tractive-vehicle-type-id') ?? row?.dataset?.tractiveVehicleTypeId); const compatibleTractiveTypes = explicitTractiveType !== null ? [explicitTractiveType] : (tractiveRandom ? Array.from(MISSION_REQUIREMENTS_TRACTIVE_TYPES[typeId] || MISSION_REQUIREMENTS_TRACTIVE_TYPES[String(typeId)] || []) : []); let contributionKey = vehicleId >= 0 ? `vehicle:${vehicleId}` : `element:${index}`; const pairedId = tractiveId !== null && tractiveId >= 0 ? tractiveId : trailerId; if (vehicleId >= 0 && pairedId !== null && pairedId >= 0) contributionKey = `pair:${Math.min(vehicleId, pairedId)}:${Math.max(vehicleId, pairedId)}`; const identityKey = vehicleId >= 0 ? `vehicle:${vehicleId}` : contributionKey; const labels = missionRequirementsMetadataValues(vehicleElement, 'labels'); const training = missionRequirementsLinkedTrainingValues(candidate, vehicleId, vehicleElement); const knownDefinitionKeys = missionRequirementsKnownDefinitionKeys(labels); const arrCapabilityState = missionRequirementsArrCapabilityState(vehicleElement, candidate, vehicleId); for (const capability of arrCapabilityState.values) { training.add(capability); for (const definition of MISSION_REQUIREMENT_DEFINITIONS) { const attributes = Array.from(definition?.arrAttributes || []).map(missionRequirementsCapabilityLabel).filter(Boolean); if (attributes.includes(capability)) knownDefinitionKeys.add(definition.key); } } const qualificationCounts = missionRequirementsQualifiedStaffCounts(candidate, vehicleId, vehicleElement, arrCapabilityState); const unit = { typeId, vehicleId, tractiveId, tractiveRandom, compatibleTractiveTypes: new Set(compatibleTractiveTypes), equipment: missionRequirementsEquipmentTypes(vehicleElement), staff: missionRequirementsResolvedStaffCapacity(vehicleId, typeId, vehicleElement, mode), labels, training, qualificationCounts, arrCapabilities: arrCapabilityState.values, arrCapabilityCounts: arrCapabilityState.counts, arrCapabilityKnown: arrCapabilityState.authoritative, knownDefinitionKeys, contributionKey }; const existing = units.get(identityKey); if (!existing) { units.set(identityKey, unit); return; } if (existing.typeId < 0 && unit.typeId >= 0) existing.typeId = unit.typeId; for (const equipment of unit.equipment) existing.equipment.add(equipment); for (const tractiveType of unit.compatibleTractiveTypes) existing.compatibleTractiveTypes.add(tractiveType); for (const label of unit.labels) existing.labels.add(label); for (const qualification of unit.training) existing.training.add(qualification); for (const capability of unit.arrCapabilities || []) existing.arrCapabilities.add(capability); for (const [key, capacity] of unit.qualificationCounts || []) { const current = existing.qualificationCounts?.get?.(key); if (!current || capacity.min > current.min) existing.qualificationCounts.set(key, capacity); } existing.arrCapabilityKnown = existing.arrCapabilityKnown || unit.arrCapabilityKnown; for (const key of unit.knownDefinitionKeys) existing.knownDefinitionKeys.add(key); if ((!existing.staff || !existing.staff.known) && unit.staff?.known) existing.staff = unit.staff; if (existing.contributionKey.startsWith('element:') && !unit.contributionKey.startsWith('element:')) existing.contributionKey = unit.contributionKey; }); return Array.from(units.values()); }

    function missionRequirementsMissionTypeId(candidate) {
        const scopes = [candidate?.root, candidate?.mount].filter(Boolean);
        const attributes = ['mission_type_id', 'data-mission-type-id', 'data-mission_type_id'];
        for (const scope of scopes) {
        for (const attribute of attributes) {
            const value = Number.parseInt(scope.getAttribute?.(attribute), 10);
            if (Number.isFinite(value) && value >= 0) return value;
        }
        const node = scope.querySelector?.('[mission_type_id], [data-mission-type-id], [data-mission_type_id], input[name="mission_type_id"]');
        if (node) {
            for (const raw of [node.getAttribute?.('mission_type_id'), node.getAttribute?.('data-mission-type-id'), node.getAttribute?.('data-mission_type_id'), node.value]) {
                const value = Number.parseInt(raw, 10);
                if (Number.isFinite(value) && value >= 0) return value;
            }
        }
        }
        const runtimeValue = Number.parseInt(pageWindow.missionTypeId ?? pageWindow.mission_type_id, 10);
        return Number.isFinite(runtimeValue) && runtimeValue >= 0 ? runtimeValue : null;
    }

    function missionRequirementsDefinitionCondition(definition, candidate) {
        const included = Array.from(definition?.missionTypes || []).map(Number).filter(Number.isFinite);
        const excluded = Array.from(definition?.excludedMissionTypes || []).map(Number).filter(Number.isFinite);
        if (!included.length && !excluded.length) return true;
        const missionTypeId = missionRequirementsMissionTypeId(candidate);
        if (missionTypeId === null) return null;
        if (included.length && !included.includes(missionTypeId)) return false;
        if (excluded.includes(missionTypeId)) return false;
        return true;
    }

function missionRequirementsUnitContribution(requirement, unit) { const definition = requirement.definition || {}; const definitionTypes = Array.from(definition.types || []); const typeEligible = definitionTypes.includes(unit.typeId); const equipmentEligible = Array.from(definition.equipment || []).some(equipment => unit.equipment.has(String(equipment).toLowerCase())); const labelEligible = unit.knownDefinitionKeys?.has?.(definition.key) || missionRequirementsDefinitionMatchesValues(definition, unit.labels); const compatibleTractiveTypes = Array.from(unit.compatibleTractiveTypes || []).map(Number).filter(Number.isFinite); const tractiveEligible = definition.pair !== true && compatibleTractiveTypes.length > 0 && compatibleTractiveTypes.every(type => definitionTypes.includes(type)); const trainingRequired = Array.from(definition.training || []).length > 0; const explicitTrainingRequired = definition.requireExplicitTraining === true; const trainingEligible = trainingRequired && missionRequirementsDefinitionMatchesValues(definition, unit.training, 'training'); const arrTokens = new Set(Array.from(definition.arrAttributes || []).map(missionRequirementsCapabilityLabel).filter(Boolean)); const arrEligible = arrTokens.size > 0 && Array.from(unit.arrCapabilities || []).some(capability => arrTokens.has(missionRequirementsCapabilityLabel(capability))); const arrClassificationKnown = arrTokens.size === 0 || unit.arrCapabilityKnown === true; const qualifiedCapacity = unit.qualificationCounts?.get?.(definition.key) || null; const legacyExplicitProof = explicitTrainingRequired && unit.qualificationCounts === undefined && (trainingEligible || arrEligible) && unit.staff ? unit.staff : null; const provenSpecialist = qualifiedCapacity || legacyExplicitProof; const eligible = requirement.group === 'staff' && trainingRequired ? (explicitTrainingRequired ? Boolean(provenSpecialist) : trainingEligible || arrEligible || typeEligible) : typeEligible || equipmentEligible || labelEligible || tractiveEligible; const plausibleExplicitCarrier = explicitTrainingRequired && (typeEligible || labelEligible || trainingEligible || arrEligible); const classificationUnknown = requirement.group === 'staff' && trainingRequired ? Boolean(!eligible && unit.staff && (plausibleExplicitCarrier || (!unit.training?.size && !arrClassificationKnown))) : unit.typeId < 0 && !unit.knownDefinitionKeys?.size && !unit.equipment?.size && !compatibleTractiveTypes.length; if (!eligible) return { eligible: false, unknown: classificationUnknown, capacity: missionRequirementsCapacity(0, classificationUnknown ? null : 0, !classificationUnknown) }; if (requirement.group === 'staff') { const capacity = explicitTrainingRequired ? provenSpecialist : (unit.staff ? missionRequirementsCapacity(unit.staff.min ?? unit.staff.value ?? 0, unit.staff.max, unit.staff.known) : missionRequirementsCapacity(0, null, false)); return { eligible: true, unknown: capacity.max === null, capacity }; } const factor = tractiveEligible && !typeEligible ? 1 : Number(definition.factors?.[unit.typeId] ?? definition.factors?.[String(unit.typeId)] ?? 1); const value = Number.isFinite(factor) && factor > 0 ? factor : 1; return { eligible: true, unknown: false, capacity: missionRequirementsCapacity(value, value, true) }; }

function missionRequirementsAggregate(requirement, units) { const contributions = new Map(); let unresolvedClassification = false; for (const unit of units) { const contribution = missionRequirementsUnitContribution(requirement, unit); unresolvedClassification = unresolvedClassification || contribution.unknown === true; if (!contribution.eligible) continue; const capacity = contribution.capacity; const existing = contributions.get(unit.contributionKey); if (!existing) { contributions.set(unit.contributionKey, capacity); continue; } const pairMin = Math.max(existing.min, capacity.min); const pairMax = existing.max === null || capacity.max === null ? null : Math.max(existing.max, capacity.max); contributions.set(unit.contributionKey, missionRequirementsCapacity(pairMin, pairMax, existing.known && capacity.known && pairMax === pairMin)); } let min = 0; let max = 0; let exact = true; for (const capacity of contributions.values()) { min += capacity.min; if (max === null || capacity.max === null) max = null; else max += capacity.max; exact = exact && capacity.known; } if (unresolvedClassification) return missionRequirementsCapacity(min, null, false); return missionRequirementsCapacity(min, max, exact && max !== null && min === max); }

    function missionRequirementsProgressValue(candidate, bar, metric) {
        const root = candidate?.root?.isConnected ? candidate.root : candidate?.mount;
        const holder = root?.querySelector?.(`[id^="mission_${bar}_holder"]`);
        if (!holder) return null;
        const node = holder.querySelector?.(`[class*="mission_${bar}_bar_${metric}_"], [class*="mission_water_bar_${metric}_"]`);
        return node ? missionRequirementsNumber(node.textContent) : null;
    }

    function missionRequirementsUnknownCoverageRow(requirement) {
        const missing = Math.max(0, missionRequirementsNumber(requirement?.missing));
        return {
        ...requirement,
        missing,
        missingText: missing.toLocaleString('en-GB'),
        selectedMin: 0,
        selectedMax: null,
        selectedKnown: false,
        selectedText: '?',
        enRouteMin: 0,
        enRouteMax: null,
        enRouteKnown: false,
        enRouteText: '?',
        stillNeededMin: 0,
        stillNeededMax: missing,
        stillNeededText: '?',
        covered: false,
        definitelyOpen: false,
        uncertain: true
        };
    }


    const MISSION_REQUIREMENTS_CATALOGUE_TTL_MS = 6 * 60 * 60 * 1000;
    const MISSION_REQUIREMENTS_CATALOGUE_STALE_MS = 7 * 24 * 60 * 60 * 1000;
    const MISSION_REQUIREMENTS_CATALOGUE_RETRY_MS = 60 * 1000;
    const MISSION_REQUIREMENTS_CATALOGUE_CACHE_LIMIT = 96;
    const missionRequirementsCatalogueCache = new Map();

    function missionRequirementsCatalogueText(node) {
        return String(node?.textContent || node?.innerText || '').replace(/\s+/gu, ' ').trim();
    }

function missionRequirementsCatalogueDescriptor(candidate) { const context = missionRequirementsPatientContext(candidate); const scopes = Array.from(new Set([candidate?.root, candidate?.mount, context.activeWindow, context.doc].filter(scope => scope?.querySelectorAll))); const links = []; const seen = new Set(); for (const scope of scopes) { for (const link of Array.from(scope.querySelectorAll?.('a[href*="/einsaetze/"]') || [])) { if (seen.has(link)) continue; seen.add(link); links.push(link); } } links.sort((left, right) => Number(/Requirements\s+for\s+this\s+Mission/iu.test(missionRequirementsElementText(right))) - Number(/Requirements\s+for\s+this\s+Mission/iu.test(missionRequirementsElementText(left)))); const doc = candidate?.root?.ownerDocument || candidate?.mount?.ownerDocument || context.doc; const location = doc?.defaultView?.location || pageWindow.location || {}; const origin = location.origin || `${location.protocol || 'https:'}//${location.host || 'www.missionchief.co.uk'}`; let matched = null; for (const link of links) { const href = String(link.getAttribute?.('href') || link.href || ''); let parsed; try { parsed = new URL(href, origin); } catch (err) { continue; } const match = parsed.pathname.match(/^\/einsaetze\/(\d+)\/?$/iu); if (!match) continue; const parameters = new URLSearchParams(); for (const name of ['overlay_index', 'additive_overlays']) { for (const value of parsed.searchParams.getAll(name)) if (value !== '') parameters.append(name, value); } const query = parameters.toString(); matched = { id: Number(match[1]), overlayIndex: missionRequirementsOptionalNumber(parsed.searchParams.get('overlay_index')), additiveOverlays: parsed.searchParams.getAll('additive_overlays'), path: `${parsed.pathname}${query ? `?${query}` : ''}` }; break; } if (!matched) { const id = missionRequirementsMissionTypeId(candidate); if (id === null || id === undefined || !Number.isFinite(Number(id)) || Number(id) < 0) return null; matched = { id: Number(id), overlayIndex: null, additiveOverlays: [], path: `/einsaetze/${Number(id)}` }; } return { ...matched, origin, url: `${origin}${matched.path}`, key: `${origin}${matched.path}` }; }

function missionRequirementsCatalogueCapability(label) { const cleaned = String(label || '') .replace(/^(?:required|requirement\s+of|needed)\s+/iu, '') .replace(/\s+/gu, ' ') .trim(); if (!cleaned) return null; for (const group of ['vehicles', 'staff', 'other']) { const parsed = missionRequirementsParseText(`1 ${cleaned}`, group); if (parsed.requirements.length !== 1 || parsed.remaining) continue; const requirement = parsed.requirements[0]; return { key: requirement.key, group, definition: requirement.definition, label: requirement.requirement }; } return null; } function missionRequirementsCatalogueModifier(label, value = '', resolveCapability = true) { const rawLabel = missionRequirementsCatalogueText({ textContent: label }); const rawValue = missionRequirementsCatalogueText({ textContent: value }); const leadingProbability = rawLabel.match(/^\s*(\d+(?:\.\d+)?)\s*%?\s+(?=(?:Probability|Chance)\b)/iu); const normalizedLabel = leadingProbability ? rawLabel.slice(leadingProbability[0].length).trim() : rawLabel; const probabilityPatterns = [ /^Probability\s+of\s+(.+?)\s+being\s+required\s*:?\s*$/iu, /^Probability\s+that\s+(.+?)\s+(?:is|are)\s+required\s*:?\s*$/iu, /^(.+?)\s+(?:requirement\s+)?(?:probability|chance)\s*:?\s*$/iu ]; for (const pattern of probabilityPatterns) { const match = normalizedLabel.match(pattern); if (!match) continue; const numberMatch = `${rawValue} ${rawLabel}`.match(/(\d+(?:\.\d+)?)\s*%?/u); const probabilityValue = numberMatch ? Math.max(0, Math.min(100, Number(numberMatch[1]))) : null; const capability = resolveCapability ? missionRequirementsCatalogueCapability(match[1]) : null; return { recognized: true, classification: 'probability', key: capability?.key || null, group: capability?.group || null, resource: capability?.label || String(match[1] || '').trim(), probability: Number.isFinite(probabilityValue) ? probabilityValue : null, availabilityOnly: false, label: rawLabel, value: rawValue }; } const availability = normalizedLabel.match(/^(.+?)\s+only\s+required\s*,?\s*when\s+available\s*:?\s*$/iu); if (availability) { const capability = resolveCapability ? missionRequirementsCatalogueCapability(availability[1]) : null; const enabled = /^(?:yes|true|1)$/iu.test(rawValue); return { recognized: true, classification: 'availability', key: capability?.key || null, group: capability?.group || null, resource: capability?.label || String(availability[1] || '').trim(), probability: null, availabilityOnly: enabled, label: rawLabel, value: rawValue }; } if (/\b(?:probability|chance)\b/iu.test(normalizedLabel) || /^(?:yes|no|true|false)$/iu.test(rawValue)) { return { recognized: true, classification: 'informational', key: null, group: null, resource: '', probability: null, availabilityOnly: false, label: rawLabel, value: rawValue }; } return { recognized: false, classification: null, key: null, group: null, resource: '', probability: null, availabilityOnly: false, label: rawLabel, value: rawValue }; } function missionRequirementsStripNonDemandMetadata(rawText, resolveCapability = false) { const fragments = String(rawText || '').replace(/\r/gu, '').split(/\n+|\s*;\s*/u); const operational = []; for (const fragment of fragments) { const clean = String(fragment || '').trim(); if (!clean) continue; const pair = clean.match(/^(.+?)\s*(?::|\||—)\s*(.+)$/u); const label = pair ? pair[1] : clean; const value = pair ? pair[2] : ''; if (missionRequirementsCatalogueModifier(label, value, resolveCapability).recognized) continue; operational.push(clean); } return operational.join('; '); }

    function missionRequirementsCatalogueRequirement(label, value) { const rawLabel = missionRequirementsCatalogueText({ textContent: label }); const rawValue = missionRequirementsCatalogueText({ textContent: value }); if (missionRequirementsCatalogueModifier(rawLabel, rawValue, true).recognized) return null; const quantityMatch = rawValue.match(/^\s*(\d+(?:[\s,.]\d{3})*)/u); const quantity = quantityMatch ? missionRequirementsNumber(quantityMatch[1]) : null; if (quantity === null) return null; const cleanedLabel = rawLabel .replace(/^(?:required|requirement\s+of|needed)\s+/iu, '') .replace(/\s*\([^)]*%[^)]*\)\s*$/u, '') .trim(); if (!cleanedLabel) return null; const probabilityMatch = `${rawLabel} ${rawValue}`.match(/(\d+(?:\.\d+)?)\s*%/u); const probability = probabilityMatch ? Math.max(0, Math.min(100, Number(probabilityMatch[1]))) : 100; const sourceText = `${quantity} ${cleanedLabel}`; for (const group of ['vehicles', 'staff', 'other']) { const parsed = missionRequirementsParseText(sourceText, group); if (!parsed.requirements.length) continue; const requirement = parsed.requirements[0]; return { ...requirement, missing: quantity, baseline: quantity, baselineText: `${quantity.toLocaleString('en-GB')}${probability < 100 ? ` (${probability}% chance)` : ''}`, probability, availabilityOnly: false, catalogueLabel: rawLabel, catalogueValue: rawValue, catalogueKnown: true }; } const inferredGroup = missionRequirementsInferGroup(cleanedLabel, 'vehicles'); const key = `catalogue-${cleanedLabel.toLowerCase().replace(/[^a-z0-9]+/gu, '-').replace(/^-|-$/gu, '').slice(0, 70) || 'unknown'}`; return { key, requirement: cleanedLabel, missing: quantity, baseline: quantity, baselineText: `${quantity.toLocaleString('en-GB')}${probability < 100 ? ` (${probability}% chance)` : ''}`, probability, availabilityOnly: false, group: inferredGroup, definition: { key, label: cleanedLabel, aliases: [cleanedLabel], group: inferredGroup, types: [], equipment: [], factors: {}, countable: false }, catalogueLabel: rawLabel, catalogueValue: rawValue, catalogueKnown: false }; }

function missionRequirementsCataloguePersonnelRequirements(label, value, kind = null) { const rawLabel = missionRequirementsCatalogueText({ textContent: label }); const available = /^Required\s+Personnel\s+Available$/iu.test(rawLabel); const required = /^Required\s+Personnel$/iu.test(rawLabel); if (!available && !required) return { recognized: false, classification: null, requirements: [], unresolved: [] }; if (available || kind === 'preconditions') return { recognized: true, classification: 'spawn-prerequisite', requirements: [], unresolved: [] }; const text = missionRequirementsCatalogueText({ textContent: value }).replace(/\s+(?=(?:\d+\s*x|x\s*\d+)\s*[A-Za-z])/giu, '; ').replace(/\s*(?:\+|\/|\band\b)\s*(?=\d+\s*x?\s*[A-Za-z])/giu, '; '); const parsed = missionRequirementsParseText(text, 'staff'); return { recognized: true, classification: 'operational', requirements: parsed.requirements.map(requirement => ({ ...requirement, baseline: requirement.missing, baselineText: requirement.missing.toLocaleString('en-GB'), probability: 100, catalogueLabel: rawLabel, catalogueValue: value, catalogueKnown: true, catalogueClassification: 'operational' })), unresolved: parsed.remaining ? [{ label: parsed.remaining, value: '', group: 'staff', classification: 'operational' }] : [] }; } function missionRequirementsCatalogueMergeRequirement(target, requirement) { if (!requirement) return; const existing = target.find(item => item.key === requirement.key); if (!existing) { target.push(requirement); return; } const baseline = Math.max(missionRequirementsOptionalNumber(existing.baseline ?? existing.missing) ?? 0, missionRequirementsOptionalNumber(requirement.baseline ?? requirement.missing) ?? 0); existing.missing = baseline; existing.baseline = baseline; existing.baselineText = baseline.toLocaleString('en-GB'); existing.catalogueKnown = existing.catalogueKnown !== false && requirement.catalogueKnown !== false; }

function missionRequirementsCatalogueParseDocument(doc, descriptor = {}) { if (!doc?.querySelectorAll) throw new Error('catalogue document unavailable'); const requirements = []; const unresolved = []; const preconditions = {}; const other = {}; const metadata = []; const modifiersByKey = new Map(); const records = []; let sawAuthoritativeRequirement = false; const tables = Array.from(doc.querySelectorAll('table') || []); for (const table of tables) { const tableText = missionRequirementsCatalogueText(table); let kind = /Vehicle\s+and\s+Personnel\s+Requirements/iu.test(tableText) ? 'requirements' : /Reward\s+and\s+Precondition/iu.test(tableText) ? 'preconditions' : /Other\s+information/iu.test(tableText) ? 'other' : null; const rows = Array.from(table.querySelectorAll?.('tr') || []); for (const row of rows) { const cells = Array.from(row.querySelectorAll?.('th, td') || []); if (cells.length < 2) continue; const label = missionRequirementsCatalogueText(cells[0]); const value = missionRequirementsCatalogueText(cells[1]); if (!label || /^(?:Value|Vehicle\s+and\s+Personnel\s+Requirements|Reward\s+and\s+Precondition|Other\s+information)$/iu.test(label)) continue; if (!kind && /^(?:Required|Requirement\s+of|Needed)\b/iu.test(label)) kind = 'requirements'; records.push({ kind, label, value }); } } for (const record of records) { const modifier = missionRequirementsCatalogueModifier(record.label, record.value, true); if (!modifier.recognized) continue; metadata.push({ ...modifier, kind: record.kind }); if (record.kind === 'other') other[record.label] = record.value; if (!modifier.key) continue; const current = modifiersByKey.get(modifier.key) || { probability: null, availabilityOnly: false }; if (modifier.classification === 'probability' && modifier.probability !== null) current.probability = modifier.probability; if (modifier.classification === 'availability' && modifier.availabilityOnly) current.availabilityOnly = true; modifiersByKey.set(modifier.key, current); } for (const record of records) { const { kind, label, value } = record; if (missionRequirementsCatalogueModifier(label, value, true).recognized) continue; const personnel = missionRequirementsCataloguePersonnelRequirements(label, value, kind); if (personnel.recognized) { if (personnel.classification === 'spawn-prerequisite') { if (kind === 'preconditions') preconditions[label] = value; continue; } sawAuthoritativeRequirement = true; personnel.requirements.forEach(requirement => missionRequirementsCatalogueMergeRequirement(requirements, requirement)); unresolved.push(...personnel.unresolved); if (kind === 'other') other[label] = value; continue; } if (kind === 'requirements') { const parsed = missionRequirementsCatalogueRequirement(label, value); if (parsed) { sawAuthoritativeRequirement = true; const modifier = modifiersByKey.get(parsed.key); const probability = modifier?.probability ?? parsed.probability ?? 100; missionRequirementsCatalogueMergeRequirement(requirements, { ...parsed, probability, availabilityOnly: modifier?.availabilityOnly === true, baselineText: `${parsed.baseline.toLocaleString('en-GB')}${probability < 100 ? ` (${probability}% chance)` : ''}` }); } else { sawAuthoritativeRequirement = true; unresolved.push({ label, value, classification: 'operational' }); } } else if (kind === 'preconditions') preconditions[label] = value; else if (kind === 'other') other[label] = value; } if (sawAuthoritativeRequirement && !requirements.length && !unresolved.length) unresolved.push({ label: 'Requirements for this Mission', value: 'No quantified vehicle or trained-personnel requirements could be parsed.' }); const titleNode = doc.querySelector?.('h1, [data-mission-title], .mission-title'); const title = missionRequirementsSafeDiagnostic(missionRequirementsCatalogueText(titleNode), 140) || `Mission ${descriptor.id ?? 'Unknown'}`; const variationLinks = Array.from(doc.querySelectorAll('a[href*="/einsaetze/"]') || []); const seenVariations = new Set(); const variations = []; for (const link of variationLinks) { const href = String(link.getAttribute?.('href') || link.href || ''); if (!/\/einsaetze\/\d+/u.test(href) || seenVariations.has(href)) continue; seenVariations.add(href); variations.push({ href: missionRequirementsSafeDiagnostic(href, 180), title: missionRequirementsSafeDiagnostic(missionRequirementsCatalogueText(link), 140) }); } const findValue = (source, pattern) => { const entry = Object.entries(source).find(([key]) => pattern.test(key)); return entry ? entry[1] : ''; }; return { id: descriptor.id ?? null, overlayIndex: descriptor.overlayIndex ?? null, additiveOverlays: Array.from(descriptor.additiveOverlays || []), path: descriptor.path || '', url: descriptor.url || '', title, requirements, unresolved, preconditions, other, metadata, averageCredits: missionRequirementsOptionalNumber(findValue(preconditions, /Average\s+credits/iu)), maxPatients: missionRequirementsOptionalNumber(findValue(other, /Max\.?\s*Patients/iu)), patientTransportProbability: missionRequirementsOptionalNumber(findValue(other, /Probability.*transport/iu)), variations, fetchedAt: Date.now(), stale: false }; }

    function missionRequirementsCataloguePrune() {
        if (missionRequirementsCatalogueCache.size <= MISSION_REQUIREMENTS_CATALOGUE_CACHE_LIMIT) return;
        const ordered = Array.from(missionRequirementsCatalogueCache.entries()).sort((a, b) => (a[1]?.touchedAt || 0) - (b[1]?.touchedAt || 0));
        while (ordered.length && missionRequirementsCatalogueCache.size > MISSION_REQUIREMENTS_CATALOGUE_CACHE_LIMIT) {
            missionRequirementsCatalogueCache.delete(ordered.shift()[0]);
        }
    }

    function missionRequirementsCatalogueCacheStore(key, value, now = Date.now()) {
        missionRequirementsCatalogueCache.set(key, {
            value,
            expiresAt: now + MISSION_REQUIREMENTS_CATALOGUE_TTL_MS,
            staleUntil: now + MISSION_REQUIREMENTS_CATALOGUE_STALE_MS,
            retryAt: 0,
            promise: null,
            touchedAt: now
        });
        missionRequirementsCataloguePrune();
        return value;
    }

    function missionRequirementsCatalogueCacheLookup(key, now = Date.now()) {
        const entry = missionRequirementsCatalogueCache.get(key);
        if (!entry?.value) return null;
        if (now > entry.staleUntil) {
            missionRequirementsCatalogueCache.delete(key);
            return null;
        }
        entry.touchedAt = now;
        return { value: entry.value, stale: now > entry.expiresAt };
    }

    function missionRequirementsCatalogueFailureFallback(key, now = Date.now()) {
        return missionRequirementsCatalogueCacheLookup(key, now);
    }

    function missionRequirementsCatalogueEnsure(record) {
        const descriptor = missionRequirementsCatalogueDescriptor(record?.candidate);
        const previousKey = record?.catalogueDescriptor?.key || '';
        const nextKey = descriptor?.key || '';
        if (previousKey !== nextKey) {
            record.catalogueRequestToken = (Number(record.catalogueRequestToken) || 0) + 1;
            record.catalogue = null;
            record.catalogueState = nextKey ? 'idle' : 'unavailable';
            record.catalogueError = '';
        }
        record.catalogueDescriptor = descriptor;
        const requestToken = Number(record.catalogueRequestToken) || 0;
        const missionIdentity = missionRequirementsMissionIdentity(record?.candidate, record?.source);
        const stillCurrent = () => record?.catalogueDescriptor?.key === descriptor?.key && (Number(record.catalogueRequestToken) || 0) === requestToken && missionRequirementsMissionIdentity(record?.candidate, record?.source) === missionIdentity;
        if (!descriptor) {
            record.catalogueState = 'unavailable';
            return null;
        }
        const now = Date.now();
        const cached = missionRequirementsCatalogueCacheLookup(descriptor.key, now);
        if (cached) {
            record.catalogue = { ...cached.value, stale: cached.stale };
            record.catalogueState = cached.stale ? 'stale' : 'ready';
            if (!cached.stale) return record.catalogue;
        }
        let entry = missionRequirementsCatalogueCache.get(descriptor.key) || { value: cached?.value || null, retryAt: 0, promise: null, touchedAt: now };
        if (entry.promise) {
            entry.promise.finally(() => missionRequirementsScheduleRecord(record));
            return record.catalogue || null;
        }
        if (entry.retryAt > now) return record.catalogue || null;
        const doc = record?.source?.ownerDocument || record?.candidate?.root?.ownerDocument || record?.candidate?.mount?.ownerDocument;
        const view = doc?.defaultView || pageWindow;
        const fetcher = typeof view?.fetch === 'function' ? view.fetch.bind(view) : typeof pageWindow.fetch === 'function' ? pageWindow.fetch.bind(pageWindow) : null;
        const DOMParserCtor = view?.DOMParser || pageWindow.DOMParser;
        if (!fetcher || typeof DOMParserCtor !== 'function') {
            record.catalogueState = record.catalogue ? 'stale' : 'unavailable';
            return record.catalogue || null;
        }
        record.catalogueState = record.catalogue ? 'stale' : 'loading';
        const promise = Promise.resolve(fetcher(descriptor.url, { credentials: 'same-origin', headers: { Accept: 'text/html' } }))
            .then(response => {
                if (!response || response.ok === false) throw new Error(`catalogue HTTP ${response?.status || 'failure'}`);
                return response.text();
            })
            .then(html => {
                const parsedDoc = new DOMParserCtor().parseFromString(String(html || ''), 'text/html');
                const catalogue = missionRequirementsCatalogueParseDocument(parsedDoc, descriptor);
                missionRequirementsCatalogueCacheStore(descriptor.key, catalogue);
                if (!stillCurrent()) return null;
                record.catalogue = catalogue;
                record.catalogueState = 'ready';
                return catalogue;
            })
            .catch(error => {
                if (!stillCurrent()) return null;
                const fallback = missionRequirementsCatalogueFailureFallback(descriptor.key);
                const current = missionRequirementsCatalogueCache.get(descriptor.key) || entry;
                current.retryAt = Date.now() + MISSION_REQUIREMENTS_CATALOGUE_RETRY_MS;
                current.promise = null;
                current.touchedAt = Date.now();
                missionRequirementsCatalogueCache.set(descriptor.key, current);
                record.catalogueError = missionRequirementsSafeDiagnostic(error?.message || 'catalogue request failed', 160);
                if (fallback) {
                    record.catalogue = { ...fallback.value, stale: true };
                    record.catalogueState = 'stale';
                    return record.catalogue;
                }
                record.catalogueState = 'error';
                return null;
            })
            .finally(() => { if (stillCurrent()) missionRequirementsScheduleRecord(record); });
        entry.promise = promise;
        entry.touchedAt = now;
        missionRequirementsCatalogueCache.set(descriptor.key, entry);
        return record.catalogue || null;
    }

    function missionRequirementsCatalogueCompare(parsed, catalogue) {
        if (!catalogue?.requirements?.length) return { state: 'unavailable', summary: 'No catalogue requirements available', issues: [] };
        const baseline = new Map(catalogue.requirements.map(item => [item.key, Number(item.baseline ?? item.missing) || 0]));
        const issues = [];
        for (const live of parsed?.requirements || []) {
            if (!baseline.has(live.key)) issues.push(`Live-only requirement: ${live.requirement}`);
            else if ((Number(live.missing) || 0) > baseline.get(live.key)) issues.push(`Live quantity exceeds catalogue: ${live.requirement}`);
        }
        if (parsed?.unresolved?.length) issues.push(`${parsed.unresolved.length} unresolved live fragment${parsed.unresolved.length === 1 ? '' : 's'}`);
        return { state: issues.length ? 'mismatch' : 'compatible', summary: issues.length ? issues.join('; ') : 'Live requirements are compatible with the catalogue baseline', issues };
    }

    function missionRequirementsCataloguePanelHtml(catalogue) {
        const rows = Array.from(catalogue?.requirements || []);
        const stale = catalogue?.stale === true;
        const rowHtml = rows.map(row => `<tr data-row-state="unresolved"><td>${escapeHtml(row.requirement)}</td><td data-label="Catalogue baseline">${escapeHtml(row.baselineText || String(row.baseline ?? row.missing ?? '?'))}</td></tr>`).join('');
        const unresolved = Array.from(catalogue?.unresolved || []);
        const unresolvedHtml = unresolved.length ? `<div class="mcms-req-unknown"><b>Unmapped catalogue entries</b>${unresolved.map(item => { const text = item.value ? `${item.label}: ${item.value}` : item.label; return `<span>${escapeHtml(text)}</span>`; }).join('')}</div>` : '';
        const note = stale
            ? 'Using a cached official catalogue baseline because the latest catalogue request failed. Current outstanding requirements are unavailable.'
            : 'Official MissionChief catalogue baseline only. Current outstanding requirements are unavailable, so do not treat these quantities as still needed.';
        const title = missionRequirementsSafeDiagnostic(catalogue?.title || '', 100);
        const summary = `${stale ? 'Cached ' : ''}official baseline${title ? ` · ${title}` : ''}`;
        const table = rows.length
            ? `<table aria-label="MissionChief catalogue baseline requirements"><colgroup><col class="mcms-req-name-col"><col class="mcms-req-number-col"></colgroup><thead><tr><th scope="col">Requirement</th><th scope="col">Catalogue baseline</th></tr></thead><tbody>${rowHtml}</tbody></table>`
            : '<div class="mcms-req-fallback"><span class="mcms-req-fallback-message">The official catalogue lists no fixed vehicle or personnel requirements for this mission.</span></div>';
        return {
            stateName: 'warning',
            widthMode: missionRequirementsWidthMode(rows, unresolved),
            html: `<div class="mcms-req-head"><div class="mcms-req-title"><i aria-hidden="true"></i><span>Mission Requirements</span></div><span class="mcms-req-summary">${escapeHtml(summary)}</span><button type="button" class="mcms-req-collapse" data-mcms-requirements-collapse aria-label="Collapse mission requirements" aria-expanded="true">⌃</button></div><div class="mcms-req-body">${table}<div class="mcms-req-unknown"><b>Baseline planning data</b><span>${escapeHtml(note)}</span></div>${unresolvedHtml}</div>`
        };
    }

    function missionRequirementsCatalogueDiagnosticLines(record, parsed) {
        const descriptor = record?.catalogueDescriptor || missionRequirementsCatalogueDescriptor(record?.candidate);
        const catalogue = record?.catalogue;
        const comparison = missionRequirementsCatalogueCompare(parsed, catalogue);
        const rows = Array.from(catalogue?.requirements || []).slice(0, 24).map(item => `  - ${item.requirement}: ${item.baselineText || item.baseline || item.missing}`);
        return [
            '### Official MissionChief catalogue',
            `- State: ${missionRequirementsSafeDiagnostic(record?.catalogueState || 'not requested', 40)}`,
            `- Definition ID: ${descriptor?.id ?? 'Unavailable'}`,
            `- Overlay index: ${descriptor?.overlayIndex ?? 'None'}`,
            `- Path: ${missionRequirementsSafeDiagnostic(descriptor?.path || '', 180) || 'Unavailable'}`,
            `- Catalogue title: ${missionRequirementsSafeDiagnostic(catalogue?.title || '', 140) || 'Unavailable'}`,
            `- Parsed catalogue rows: ${catalogue?.requirements?.length || 0}`,
            `- Unmapped catalogue rows: ${catalogue?.unresolved?.length || 0}`,
            `- Average credits: ${catalogue?.averageCredits ?? 'Unavailable'}`,
            `- Max patients: ${catalogue?.maxPatients ?? 'Unavailable'}`,
            `- Mission variations: ${catalogue?.variations?.length || 0}`,
            `- Live/catalogue comparison: ${missionRequirementsSafeDiagnostic(comparison.summary, 500)}`,
            ...(rows.length ? ['', 'Catalogue requirement summary:', ...rows] : []),
            ''
        ];
    }


    function missionRequirementsExclusiveUnitBuckets(selectedUnits, respondingUnits, onSiteUnits) {
        const claimed = new Set();
        const keysFor = unit => {
            const keys = [];
            if (unit?.vehicleId >= 0) keys.push(`vehicle:${unit.vehicleId}`);
            if (unit?.contributionKey && !String(unit.contributionKey).startsWith('element:')) keys.push(String(unit.contributionKey));
            return keys;
        };
        const claim = units => Array.from(units || []).filter(unit => {
            const keys = keysFor(unit);
            if (keys.some(key => claimed.has(key))) return false;
            keys.forEach(key => claimed.add(key));
            return true;
        });
        const onSite = claim(onSiteUnits);
        const responding = claim(respondingUnits);
        const selected = claim(selectedUnits);
        return { selected, responding, onSite };
    }

    function missionRequirementsResolve(candidate, parsed, catalogue = null) { const rawSelectedUnits = missionRequirementsCollectUnits(candidate, 'selected'); const rawRespondingUnits = missionRequirementsCollectUnits(candidate, 'responding'); const rawOnSiteUnits = missionRequirementsCollectUnits(candidate, 'onsite'); const buckets = missionRequirementsExclusiveUnitBuckets(rawSelectedUnits, rawRespondingUnits, rawOnSiteUnits); const catalogueByKey = new Map(Array.from(catalogue?.requirements || []).map(item => [item.key, item])); return parsed.requirements.map(requirement => { let effectiveMissing = Math.max(0, Number(requirement.missing) || 0); if (requirement.patientCondition === true) { const requiredValue = Math.max(0, Number(requirement.patientConditionRequired ?? requirement.patientRequired ?? requirement.missing) || 0); const fulfilledValue = Math.max(0, Number(requirement.patientConditionFulfilled) || 0); const fulfilledKnown = requirement.patientConditionFulfilledKnown === true; const zero = missionRequirementsCapacity(0, 0, true); const fulfilled = fulfilledKnown ? missionRequirementsCapacity(fulfilledValue, fulfilledValue, true) : missionRequirementsCapacity(fulfilledValue, null, false); const row = missionRequirementsCoverageRow(requirement, zero, zero, fulfilled, missionRequirementsCapacity(requiredValue, requiredValue, true)); if (!fulfilledKnown && !row.covered) { row.definitelyOpen = false; row.uncertain = true; row.coverageKnown = false; } return { ...row, conditionKnown: true, conditionMatched: true, requirementAuthority: 'patient-details' }; } if (requirement.definition?.countable === false) return missionRequirementsUnknownCoverageRow(requirement); const condition = missionRequirementsDefinitionCondition(requirement.definition, candidate); if (condition !== true) { const unknown = missionRequirementsCapacity(0, null, false); const unresolvedRow = missionRequirementsCoverageRow(requirement, unknown, unknown, unknown, unknown); return { ...unresolvedRow, conditionKnown: condition !== null, conditionMatched: false, uncertain: true, definitelyOpen: false, coverageKnown: false }; } let selected; let responding; let onSite; if (requirement.definition?.bar) { const selectedValue = missionRequirementsProgressValue(candidate, requirement.definition.bar, 'selected'); const respondingValue = missionRequirementsProgressValue(candidate, requirement.definition.bar, 'driving'); const missingValue = missionRequirementsProgressValue(candidate, requirement.definition.bar, 'missing'); const onSiteMetrics = ['at_mission', 'on_site', 'onsite', 'arrived', 'actual']; const onSiteValue = onSiteMetrics.map(metric => missionRequirementsProgressValue(candidate, requirement.definition.bar, metric)).find(value => value !== null); if (selectedValue === null || respondingValue === null || missingValue === null) { const unknown = missionRequirementsCapacity(0, null, false); const row = missionRequirementsCoverageRow(requirement, unknown, unknown, unknown, unknown); row.covered = false; row.definitelyOpen = false; row.uncertain = true; row.coverageKnown = false; return { ...row, conditionKnown: true, conditionMatched: true, requirementAuthority: 'mission-progress' }; } effectiveMissing = Math.max(0, missingValue + respondingValue); selected = missionRequirementsCapacity(selectedValue, selectedValue, true); responding = missionRequirementsCapacity(respondingValue, respondingValue, true); onSite = onSiteValue === undefined ? missionRequirementsCapacity(0, 0, true) : missionRequirementsCapacity(onSiteValue, onSiteValue, true); } else { selected = missionRequirementsAggregate(requirement, buckets.selected); responding = missionRequirementsAggregate(requirement, buckets.responding); onSite = missionRequirementsAggregate(requirement, buckets.onSite); } const catalogueRequirement = catalogueByKey.get(requirement.key); const baseline = missionRequirementsOptionalNumber(catalogueRequirement?.baseline ?? catalogueRequirement?.missing); const catalogueOnly = requirement.catalogueDerived === true && requirement.statedRequirement === false; const catalogueProbability = missionRequirementsOptionalNumber(requirement.catalogueProbability ?? catalogueRequirement?.probability) ?? 100; const patientKnown = requirement.patientDerived === true && requirement.patientCountKnown === true; const patientUnknown = requirement.patientDerived === true && requirement.patientCountKnown === false; const patientRequired = patientKnown ? Math.max(0, Number(requirement.patientRequired) || 0) : null; const hasStatedRequirement = requirement.statedRequirement !== false; if (baseline !== null && hasStatedRequirement) { const committed = Math.max(0, baseline - effectiveMissing); const operationalMin = onSite.min + responding.min; const operationalMax = onSite.max === null || responding.max === null ? null : onSite.max + responding.max; const inferredSelectedMin = operationalMax === null ? 0 : Math.max(0, committed - operationalMax); const inferredSelectedMax = Math.max(0, committed - operationalMin); if (inferredSelectedMax > selected.min) { const selectedMin = Math.max(selected.min, inferredSelectedMin); const selectedMax = selected.max === null ? inferredSelectedMax : Math.max(selected.max, inferredSelectedMax); selected = missionRequirementsCapacity(selectedMin, selectedMax, selectedMax !== null && selectedMin === selectedMax && onSite.known && responding.known); } } const statedRequiredMin = hasStatedRequirement ? effectiveMissing + onSite.min : 0; const statedRequiredMax = hasStatedRequirement ? (onSite.max === null ? null : effectiveMissing + onSite.max) : 0; const fixedMinimum = Math.max(patientRequired ?? 0, baseline ?? 0, statedRequiredMin); let required; if (patientUnknown) { required = missionRequirementsCapacity(Math.max(baseline ?? 0, statedRequiredMin), null, false); } else if (catalogueOnly && catalogueProbability < 100) { required = missionRequirementsCapacity(0, baseline ?? 0, false); } else if (patientKnown) { const possibleMaximum = statedRequiredMax === null ? null : Math.max(patientRequired, baseline ?? 0, statedRequiredMax); const exact = possibleMaximum !== null && possibleMaximum === fixedMinimum && (hasStatedRequirement ? onSite.known : true); required = missionRequirementsCapacity(fixedMinimum, possibleMaximum, exact); } else { const liveRequiredMin = statedRequiredMin; const liveRequiredMax = statedRequiredMax; required = baseline !== null ? missionRequirementsCapacity(Math.max(baseline, liveRequiredMin), Math.max(baseline, liveRequiredMin), true) : missionRequirementsCapacity(liveRequiredMin, liveRequiredMax, onSite.known && liveRequiredMax !== null && liveRequiredMin === liveRequiredMax); } const row = missionRequirementsCoverageRow(requirement, selected, responding, onSite, required); if (patientUnknown) { row.covered = false; row.definitelyOpen = false; row.uncertain = true; row.coverageKnown = false; } else if (catalogueOnly && catalogueProbability < 100 && !row.covered) { row.definitelyOpen = false; row.uncertain = true; row.coverageKnown = false; } const authorities = []; if (requirement.patientDerived) authorities.push('patients'); if (baseline !== null) authorities.push('mission-info'); if (hasStatedRequirement) authorities.push('live'); return { ...row, conditionKnown: true, conditionMatched: true, requirementAuthority: authorities.length ? authorities.join('+') : 'live-reconstructed' }; }); }

    function missionRequirementsOverallState(rows, unresolved) {
        if (rows.some(row => row.definitelyOpen)) return 'danger';
        if (rows.some(row => row.uncertain) || unresolved.length) return 'warning';
        return rows.length ? 'success' : 'warning';
    }

    function missionRequirementsLssmActive(candidate, source) {
        // MissionChief and LSSM both use the generic alert-missing-vehicles class.
        // Only explicit LSSM ownership metadata may suppress the Toolkit panel.
        const ownedSelector = [
        '.alert-missing-vehicles[data-raw-html]',
        '[data-lssm-enhanced-missing-vehicles]',
            '[data-lssm-module="extendedCallWindow.enhancedMissingVehicles"]'
        ].join(', ');
        const isLssmOwned = element => {
        if (!element) return false;
        const sharedAlert = Boolean(
            element.matches?.('.alert-missing-vehicles')
            || element.classList?.contains?.('alert-missing-vehicles')
        );
            const rawHtml = element.getAttribute?.('data-raw-html');
            if (sharedAlert && rawHtml !== null && rawHtml !== undefined) return true;
            return Boolean(
                element.matches?.('[data-lssm-enhanced-missing-vehicles]')
                || element.matches?.('[data-lssm-module="extendedCallWindow.enhancedMissingVehicles"]')
            );
        };

        if (isLssmOwned(source)) return true;
        const closestOwned = source?.closest?.(ownedSelector);
        if (isLssmOwned(closestOwned)) return true;
        return isLssmOwned(candidate?.root?.querySelector?.(ownedSelector));
    }

    function missionRequirementsExplicitSource(source) {
        if (!source || source.isConnected === false) return false;
        if (source.getAttribute?.('data-mcms-requirements-anchor') === '1' || source.id === 'missing_text') return true;
        if (source.matches?.('[data-requirement-type], .alert-missing-vehicles, [data-lssm-enhanced-missing-vehicles], [data-lssm-module="extendedCallWindow.enhancedMissingVehicles"]')) return true;
        return Boolean(source.querySelector?.('[data-requirement-type], .alert-missing-vehicles[data-raw-html], [data-lssm-enhanced-missing-vehicles]'));
    }

    function missionRequirementsDirectChild(root, node) {
        let current = node;
        while (current?.parentNode && current.parentNode !== root) current = current.parentNode;
        return current?.parentNode === root ? current : node;
    }

    function missionRequirementsPlacementHostUnsafe(node, boundary = null) {
        const unsafeTags = new Set(['TABLE', 'THEAD', 'TBODY', 'TFOOT', 'TR', 'TD', 'TH', 'COLGROUP']);
        let current = node;
        while (current && current !== boundary) {
            if (unsafeTags.has(String(current.tagName || '').toUpperCase())) return true;
            current = current.parentNode;
        }
        return false;
    }

    function missionRequirementsPlacementBlock(root, node) {
        if (!root || !node) return null;
        let target = node;
        let current = node;
        while (current && current !== root) {
            if (String(current.tagName || '').toUpperCase() === 'TABLE') target = current;
            current = current.parentNode;
        }
        const block = missionRequirementsDirectChild(root, target);
        const parent = block?.parentNode || root;
        if (!parent || missionRequirementsPlacementHostUnsafe(parent, root?.parentNode || null)) {
            return { root, parent: root, before: root.firstChild || null };
        }
        return { root, parent, before: block };
    }

    function missionRequirementsPlacement(candidate, source = null) {
        const root = missionRequirementsCandidateRoot(candidate) || candidate?.root || candidate?.mount;
        if (!root) return null;
        const native = root.matches?.('#missing_text') ? root : root.querySelector?.('#missing_text');
        const explicit = native || (missionRequirementsExplicitSource(source) && source?.getAttribute?.('data-mcms-requirements-anchor') !== '1' ? source : null);
        if (explicit?.parentNode) return missionRequirementsPlacementHostUnsafe(explicit.parentNode, root?.parentNode || null)
            ? missionRequirementsPlacementBlock(root, explicit)
            : { root, parent: explicit.parentNode, before: explicit };
        const address = root.querySelector?.('#mission_address, [data-mission-address], .mission-address, .mission_address');
        const title = root.querySelector?.('#mission_caption, #mission_name, [data-mission-title], .mission-title, .mission_caption, h1');
        const header = address || title;
        if (header) {
            const block = missionRequirementsDirectChild(root, header);
            const parent = block?.parentNode || root;
            const siblings = Array.from(parent.children || []);
            const index = siblings.indexOf(block);
            return { root, parent, before: index >= 0 ? (siblings[index + 1] || null) : (block?.nextSibling || null) };
        }
        // Operational regions may load before the mission header during AJAX dispatch.
        // They remain data sources only and are never valid panel hosts.
        return null;
    }

    function missionRequirementsPlacePanel(candidate, source, panel) {
        const placement = missionRequirementsPlacement(candidate, source);
        if (!placement?.parent || !panel) return false;
        const siblings = Array.from(placement.parent.children || []);
        const panelIndex = siblings.indexOf(panel);
        const beforeIndex = placement.before ? siblings.indexOf(placement.before) : siblings.length;
        if (panel.parentNode !== placement.parent || panelIndex < 0 || panelIndex !== beforeIndex - 1) {
            placement.parent.insertBefore?.(panel, placement.before || null);
        }
        return true;
    }

    function missionRequirementsSourceForCandidate(candidate) {
        const root = missionRequirementsCandidateRoot(candidate) || candidate?.root;
        const supplied = candidate?.source;
        const native = root?.matches?.('#missing_text') ? root : root?.querySelector?.('#missing_text');
        if (native && native.isConnected !== false) return native;
        if (supplied?.getAttribute?.('data-mcms-requirements-anchor') === '1' && supplied.isConnected !== false) {
            const placement = missionRequirementsPlacement({ ...candidate, root, mount: root }, supplied);
            if (placement?.parent) return supplied;
            supplied.remove?.();
        }
        return missionRequirementsExplicitSource(supplied) ? supplied : null;
    }

    function missionRequirementsCandidateFromSource(source) {
        if (!source?.ownerDocument || source.isConnected === false) return null;
        const rootSelector = [
            '#mission_form',
            'form[action*="/missions/"]',
            '#mission_content',
            '#lightbox_box',
            '#lightbox',
            '.lightbox_content',
            '.modal',
            '[role="dialog"]',
            '.ui-dialog'
        ].join(', ');
        const root = source.closest?.(rootSelector) || source.parentNode || source.ownerDocument.body;
        if (!root) return null;
        return { root, mount: root, source, directMissionRequirements: true };
    }

    function missionRequirementsAnchorForCandidate(candidate) {
        const root = missionRequirementsCandidateRoot(candidate) || candidate?.root || candidate?.mount;
        if (!root?.ownerDocument?.createElement) return null;
        let anchor = Array.from(root.children || []).find(node => node?.getAttribute?.('data-mcms-requirements-anchor') === '1')
            || root.querySelector?.('[data-mcms-requirements-anchor="1"]');
        const placement = missionRequirementsPlacement({ ...candidate, root, mount: root });
        if (!placement?.parent) {
            anchor?.remove?.();
            return null;
        }
        if (!anchor || anchor.isConnected === false) {
            anchor = root.ownerDocument.createElement('span');
            anchor.hidden = true;
            anchor.setAttribute('aria-hidden', 'true');
            anchor.setAttribute('data-mcms-requirements-anchor', '1');
        }
        placement.parent.insertBefore?.(anchor, placement.before || null);
        return anchor;
    }

    function missionRequirementsCandidateRoot(candidate) {
        const missionSelector = '#mission_form, form[action*="/missions/"], #mission_content, .mission_content, [data-mission-content]';
        const windowSelector = '#lightbox_box, #lightbox, .lightbox_content, .modal-body, .modal, [role="dialog"], .ui-dialog-content, .ui-dialog';
        const nodes = [candidate?.source, candidate?.root, candidate?.mount].filter(Boolean);
        const missionWithin = node => {
            if (!node) return null;
            if (node.matches?.(missionSelector)) return node;
            const closest = node.closest?.(missionSelector);
            if (closest) return closest;
            return node.querySelector?.(missionSelector) || null;
        };
        for (const node of nodes) {
            const mission = missionWithin(node);
            if (mission) return mission;
        }
        for (const node of nodes) {
            const windowRoot = node.matches?.(windowSelector) ? node : node.closest?.(windowSelector);
            if (windowRoot) return missionWithin(windowRoot) || windowRoot;
        }
        for (const node of nodes) {
            try {
                const frame = node.ownerDocument?.defaultView?.frameElement || null;
                if (!frame) continue;
                const frameMission = missionWithin(frame);
                if (frameMission) return frameMission;
                const frameWindow = frame.matches?.(windowSelector) ? frame : frame.closest?.(windowSelector);
                if (frameWindow) return missionWithin(frameWindow) || frameWindow;
            } catch (err) {}
        }
        return candidate?.root || candidate?.mount || candidate?.source || null;
    }

    function missionRequirementsLooksLikeWindow(candidate) {
        const root = missionRequirementsCandidateRoot(candidate);
        if (!root?.querySelector) return false;
        if (missionRequirementsMissionIdentity({ ...candidate, root }, missionRequirementsSourceForCandidate({ ...candidate, root })) > 0) return true;
        if (root.matches?.('#mission_form, form[action*="/missions/"], #mission_content')) return true;
        return Boolean(root.querySelector('#vehicle_show_table_body_all, #mission_vehicle_driving, .vehicle_checkbox, [mission_type_id], [data-mission-type-id]'));
    }

    function missionRequirementsPrimaryRuntime(){try{return!pageWindow.top||pageWindow.top===pageWindow}catch{return true}}
    function missionRequirementsMissionIdentity(candidate,source){const r=candidate?.root,l=r?.querySelector?.('a[href*="/missions/"],form[action*="/missions/"]');for(const v of[candidate?.missionId,candidate?.mission_id,r?.dataset?.missionId,r?.getAttribute?.('mission_id'),r?.getAttribute?.('action'),l?.getAttribute?.('href'),l?.getAttribute?.('action'),source?.ownerDocument?.defaultView?.location?.pathname]){const m=String(v??'').match(/(?:\/missions\/|mission[_-]?)(\d+)|^(\d+)$/i),id=+(m?.[1]||m?.[2]);if(id>0)return id}return 0}
    function missionRequirementsWindowCandidates() {
        const candidates = [];
        const seenSources = new Set();
        const seenRoots = new Set();
        const add = (candidate, trusted = false) => {
            const root = missionRequirementsCandidateRoot(candidate);
            if (!root || seenRoots.has(root)) return;
            let source = missionRequirementsSourceForCandidate({ ...candidate, root, mount: root });
            if (!source) {
                if (!trusted && !missionRequirementsLooksLikeWindow({ ...candidate, root, mount: root })) return;
                source = missionRequirementsAnchorForCandidate({ ...candidate, root, mount: root });
            }
            if (!source || source.isConnected === false || seenSources.has(source)) return;
            seenRoots.add(root);
            seenSources.add(source);
            candidates.push({ ...candidate, root, mount: root, source });
        };
        missionValueWindowCandidates().forEach(candidate => add(candidate, true));
        for (const context of transportSweepDocumentContexts()) {
            const doc = context?.doc;
            if (!doc?.querySelectorAll) continue;
            for (const source of doc.querySelectorAll('#missing_text')) add(missionRequirementsCandidateFromSource(source), true);
            for (const root of doc.querySelectorAll('#mission_form, form[action*="/missions/"], #mission_content')) add({ root, mount: root }, false);
        }
        const priority = candidate => {
            const source = candidate?.source;
            return (isVisible(candidate?.root) ? 100 : 0)
                + (source?.id === 'missing_text' || source?.matches?.('#missing_text') ? 20 : 0)
                + (source?.getAttribute?.('data-mcms-requirements-anchor') === '1' ? 0 : 5)
                + (missionRequirementsRecords.has(source) ? 1 : 0);
        };
        const missionIds = new Set();
        return candidates.sort((left, right) => priority(right) - priority(left)).filter(candidate => {
            const missionId = missionRequirementsMissionIdentity(candidate, candidate.source);
            if (!missionId) return true;
            if (missionIds.has(missionId)) return false;
            missionIds.add(missionId);
            return true;
        });
    }

    function missionRequirementsDocumentCss() {
        return `
#${SCRIPT.missionRequirementsPanelId}{--mcms-req-accent:#6fd7ff;--mcms-req-surface:#101820;--mcms-req-surface-2:#17242f;--mcms-req-border:rgba(111,215,255,.38);--mcms-req-text:#eef9ff;--mcms-req-muted:#a9bdc8;display:block!important;position:relative!important;clear:both!important;width:min(100%,940px)!important;max-width:100%!important;box-sizing:border-box!important;margin:0 0 7px!important;border:1px solid var(--mcms-req-border)!important;border-left:4px solid var(--mcms-req-state,#ef5350)!important;border-radius:9px!important;background:linear-gradient(145deg,var(--mcms-req-surface),var(--mcms-req-surface-2))!important;color:var(--mcms-req-text)!important;box-shadow:0 5px 14px rgba(0,0,0,.19)!important;overflow:hidden!important;font-family:Arial,Helvetica,sans-serif!important;z-index:auto!important}
[data-mcms-requirements-source-hidden="1"]{display:none!important}
#${SCRIPT.missionRequirementsPanelId}[data-width-mode="wide"]{width:min(100%,1140px)!important}
#${SCRIPT.missionRequirementsPanelId}[data-width-mode="fluid"]{width:100%!important}
#${SCRIPT.missionRequirementsPanelId}[data-state="danger"]{--mcms-req-state:#ef5350}
#${SCRIPT.missionRequirementsPanelId}[data-state="warning"]{--mcms-req-state:#ffb74d}
#${SCRIPT.missionRequirementsPanelId}[data-state="success"]{--mcms-req-state:#4dd68a}
#${SCRIPT.missionRequirementsPanelId}[data-mcms-theme="cyberpunk"]{--mcms-req-accent:#00f0ff;--mcms-req-surface:#080b12;--mcms-req-surface-2:#111725;--mcms-req-border:rgba(0,240,255,.50);border-radius:2px!important}
#${SCRIPT.missionRequirementsPanelId}[data-mcms-theme="fallout4"]{--mcms-req-accent:#c8ff8b;--mcms-req-surface:#071008;--mcms-req-surface-2:#172817;--mcms-req-border:rgba(164,234,101,.48);--mcms-req-text:#d8ffad;--mcms-req-muted:#91b978}
#${SCRIPT.missionRequirementsPanelId}[data-mcms-theme="umbrella"]{--mcms-req-accent:#f4f6f8;--mcms-req-surface:#101114;--mcms-req-surface-2:#1c1d21;--mcms-req-border:rgba(214,39,50,.55)}
#${SCRIPT.missionRequirementsPanelId}[data-mcms-theme="factorio"]{--mcms-req-accent:#f0a44a;--mcms-req-surface:#171717;--mcms-req-surface-2:#2a2824;--mcms-req-border:rgba(240,164,74,.48);border-radius:4px!important}
#${SCRIPT.missionRequirementsPanelId}[data-mcms-theme="bond007"]{--mcms-req-accent:#d9bd77;--mcms-req-surface:#090a0c;--mcms-req-surface-2:#17191e;--mcms-req-border:rgba(217,189,119,.45)}
#${SCRIPT.missionRequirementsPanelId}[data-mcms-theme="hyrule"]{--mcms-req-accent:#6ee6d6;--mcms-req-surface:#10231d;--mcms-req-surface-2:#17352b;--mcms-req-border:rgba(217,183,90,.48)}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-head{display:flex!important;align-items:center!important;gap:7px!important;min-width:0!important;padding:6px 9px!important;border-bottom:1px solid rgba(255,255,255,.10)!important;background:rgba(0,0,0,.16)!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-title{display:flex!important;align-items:center!important;gap:7px!important;min-width:0!important;flex:1 1 auto!important;font-size:13px!important;line-height:1.15!important;font-weight:900!important;letter-spacing:.12px!important;color:var(--mcms-req-text)!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-title i{display:block!important;width:8px!important;height:8px!important;flex:0 0 8px!important;border-radius:50%!important;background:var(--mcms-req-state)!important;box-shadow:0 0 9px color-mix(in srgb,var(--mcms-req-state) 65%,transparent)!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-summary{flex:0 1 auto!important;min-width:0!important;max-width:50%!important;padding:3px 7px!important;border:1px solid color-mix(in srgb,var(--mcms-req-state) 52%,transparent)!important;border-radius:999px!important;color:var(--mcms-req-text)!important;background:color-mix(in srgb,var(--mcms-req-state) 15%,transparent)!important;font-size:10px!important;line-height:1.15!important;font-weight:850!important;white-space:normal!important;text-align:center!important;overflow-wrap:anywhere!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-collapse{display:inline-flex!important;align-items:center!important;justify-content:center!important;flex:0 0 26px!important;width:26px!important;height:24px!important;padding:0!important;border:1px solid rgba(255,255,255,.18)!important;border-radius:6px!important;background:rgba(255,255,255,.07)!important;color:var(--mcms-req-text)!important;font:900 13px/1 Arial,sans-serif!important;cursor:pointer!important}
#${SCRIPT.missionRequirementsPanelId}.mcms-collapsed .mcms-req-body{display:none!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-body{max-height:min(36vh,360px)!important;overflow:auto!important;overscroll-behavior:contain!important}
#${SCRIPT.missionRequirementsPanelId} table{width:100%!important;max-width:100%!important;border-collapse:separate!important;border-spacing:0!important;table-layout:fixed!important;margin:0!important;background:transparent!important;color:inherit!important}
#${SCRIPT.missionRequirementsPanelId} col.mcms-req-name-col{width:40%!important}
#${SCRIPT.missionRequirementsPanelId} col.mcms-req-number-col{width:12%!important}
#${SCRIPT.missionRequirementsPanelId} thead th{position:sticky!important;top:0!important;z-index:2!important;padding:5px 4px!important;border:0!important;border-bottom:1px solid rgba(255,255,255,.12)!important;background:color-mix(in srgb,var(--mcms-req-surface-2) 94%,black)!important;color:var(--mcms-req-muted)!important;font-size:9.5px!important;line-height:1.1!important;font-weight:900!important;letter-spacing:.12px!important;text-transform:uppercase!important;white-space:normal!important;text-align:center!important;overflow-wrap:anywhere!important}
#${SCRIPT.missionRequirementsPanelId} thead th:first-child{text-align:left!important;padding-left:7px!important}
#${SCRIPT.missionRequirementsPanelId} tbody tr{--mcms-row-state:#ef5350}
#${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="covered"]{--mcms-row-state:#4dd68a}
#${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="partial"]{--mcms-row-state:#ffb74d}
#${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="unresolved"]{--mcms-row-state:#aab2bd}
#${SCRIPT.missionRequirementsPanelId} tbody td{box-sizing:border-box!important;padding:5px 4px!important;border:0!important;border-bottom:1px solid rgba(255,255,255,.07)!important;background:transparent!important;color:var(--mcms-req-text)!important;font-size:12px!important;line-height:1.15!important;vertical-align:middle!important}
#${SCRIPT.missionRequirementsPanelId} tbody tr:last-child td{border-bottom:0!important}
#${SCRIPT.missionRequirementsPanelId} tbody td:first-child{padding-left:7px!important;border-left:3px solid var(--mcms-row-state)!important;font-weight:850!important;text-align:left!important;white-space:normal!important;overflow-wrap:anywhere!important;word-break:normal!important}
#${SCRIPT.missionRequirementsPanelId} tbody td:first-child>span{display:inline!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-source{display:inline-flex!important;align-items:center!important;margin-left:5px!important;padding:1px 4px!important;border:1px solid color-mix(in srgb,var(--mcms-req-accent) 48%,transparent)!important;border-radius:999px!important;background:color-mix(in srgb,var(--mcms-req-accent) 12%,transparent)!important;color:var(--mcms-req-accent)!important;font-size:8px!important;line-height:1.2!important;font-weight:900!important;letter-spacing:.08px!important;text-transform:uppercase!important;vertical-align:middle!important;white-space:nowrap!important}
#${SCRIPT.missionRequirementsPanelId} tbody td:not(:first-child){font-variant-numeric:tabular-nums!important;text-align:center!important;white-space:nowrap!important;font-weight:800!important}
#${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="covered"] td{background:rgba(77,214,138,.075)!important}
#${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="covered"] td:first-child{color:#9bf2bf!important}
#${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="partial"] td{background:rgba(255,183,77,.055)!important}
#${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="partial"] td:first-child{color:#ffd18a!important}
#${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="open"] td{background:rgba(239,83,80,.045)!important}
#${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="unresolved"] td{background:rgba(170,178,189,.055)!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-still{font-size:13px!important;font-weight:950!important;color:var(--mcms-row-state)!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-unknown{display:grid!important;gap:4px!important;padding:7px 9px 8px!important;border-top:1px solid rgba(255,183,77,.22)!important;background:rgba(255,183,77,.06)!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-unknown b{color:#ffd18a!important;font-size:10px!important;text-transform:uppercase!important;letter-spacing:.2px!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-unknown span{color:var(--mcms-req-text)!important;font-size:11px!important;line-height:1.3!important;overflow-wrap:anywhere!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-fallback{display:flex!important;align-items:center!important;justify-content:space-between!important;gap:10px!important;padding:9px!important;color:var(--mcms-req-text)!important;font-size:11px!important;line-height:1.35!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-fallback-message{min-width:0!important;overflow-wrap:anywhere!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-report{display:inline-flex!important;align-items:center!important;justify-content:center!important;flex:0 0 auto!important;padding:5px 8px!important;border:1px solid rgba(255,183,77,.58)!important;border-radius:6px!important;background:rgba(255,183,77,.14)!important;color:#ffe0aa!important;font:800 10px/1.2 Arial,sans-serif!important;cursor:pointer!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-unknown .mcms-req-report{justify-self:start!important;margin-top:2px!important}
@media(min-width:768px) and (max-width:1180px){#${SCRIPT.missionRequirementsPanelId}{width:100%!important}#${SCRIPT.missionRequirementsPanelId} .mcms-req-head{padding:6px 8px!important}#${SCRIPT.missionRequirementsPanelId} thead th{font-size:9px!important}#${SCRIPT.missionRequirementsPanelId} tbody td{font-size:11.5px!important;padding:5px 3px!important}}
@media(max-width:767px){#${SCRIPT.missionRequirementsPanelId}{margin-bottom:6px!important;border-radius:7px!important}#${SCRIPT.missionRequirementsPanelId} .mcms-req-head{padding:6px 7px!important;gap:6px!important}#${SCRIPT.missionRequirementsPanelId} .mcms-req-title{font-size:12px!important}#${SCRIPT.missionRequirementsPanelId} .mcms-req-summary{max-width:47%!important;font-size:9px!important;padding:3px 5px!important}#${SCRIPT.missionRequirementsPanelId} .mcms-req-body{max-height:min(42vh,390px)!important;padding:5px!important}#${SCRIPT.missionRequirementsPanelId} table,#${SCRIPT.missionRequirementsPanelId} tbody{display:block!important;width:100%!important}#${SCRIPT.missionRequirementsPanelId} colgroup,#${SCRIPT.missionRequirementsPanelId} thead{display:none!important}#${SCRIPT.missionRequirementsPanelId} tbody tr{display:grid!important;grid-template-columns:repeat(5,minmax(0,1fr))!important;gap:0!important;margin:0 0 5px!important;border:1px solid rgba(255,255,255,.11)!important;border-left:3px solid var(--mcms-row-state)!important;border-radius:6px!important;background:rgba(255,255,255,.035)!important;overflow:hidden!important}#${SCRIPT.missionRequirementsPanelId} tbody tr:last-child{margin-bottom:0!important}#${SCRIPT.missionRequirementsPanelId} tbody td{display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;min-width:0!important;min-height:38px!important;padding:4px 2px!important;border:0!important;border-right:1px solid rgba(255,255,255,.07)!important;font-size:11.5px!important;white-space:normal!important}#${SCRIPT.missionRequirementsPanelId} tbody td:last-child{border-right:0!important}#${SCRIPT.missionRequirementsPanelId} tbody td:first-child{grid-column:1/-1!important;display:block!important;min-height:0!important;padding:6px!important;border-left:0!important;border-right:0!important;border-bottom:1px solid rgba(255,255,255,.09)!important;font-size:12px!important;text-align:left!important}#${SCRIPT.missionRequirementsPanelId} tbody td:not(:first-child)::before{content:attr(data-label)!important;display:block!important;margin-bottom:2px!important;color:var(--mcms-req-muted)!important;font-size:7.5px!important;line-height:1!important;font-weight:900!important;letter-spacing:.08px!important;text-transform:uppercase!important;text-align:center!important;white-space:normal!important;overflow-wrap:anywhere!important}#${SCRIPT.missionRequirementsPanelId} .mcms-req-fallback{align-items:stretch!important;flex-direction:column!important}#${SCRIPT.missionRequirementsPanelId} .mcms-req-report{align-self:flex-start!important}}
        `;
    }

    function ensureMissionRequirementsDocumentStyle(doc) {
        if (!doc?.createElement) return;
        const requirementsDocumentStyleId = SCRIPT.missionRequirementsDocumentStyleId;
        let style = doc.getElementById?.(requirementsDocumentStyleId);
        if (!style) {
            style = doc.createElement('style');
            style.id = requirementsDocumentStyleId;
            (doc.head || doc.documentElement)?.appendChild(style);
        }
        const css = missionRequirementsDocumentCss();
        if (style.textContent !== css) style.textContent = css;
    }

    function missionRequirementsHideSource(source) {
        if (!source || source.dataset.mcmsRequirementsSourceHidden === '1') return;
        source.dataset.mcmsRequirementsSourceHidden = '1';
    }

    function missionRequirementsRestoreSource(source) {
        if (!source || source.dataset.mcmsRequirementsSourceHidden !== '1') return;
        delete source.dataset.mcmsRequirementsSourceHidden;
    }

    function missionRequirementsWidthMode(rows = [], unresolved = []) {
        const labels = Array.from(rows || []).map(row => String(row?.requirement || row?.catalogueLabel || row?.label || ''));
        const fragments = Array.from(unresolved || []).map(item => String(item?.text || [item?.label, item?.value].filter(Boolean).join(': ') || item || ''));
        const longestLabel = labels.reduce((maximum, value) => Math.max(maximum, value.length), 0);
        const longestFragment = fragments.reduce((maximum, value) => Math.max(maximum, value.length), 0);
        if (longestLabel > 62 || longestFragment > 150) return 'fluid';
        if (longestLabel > 32 || longestFragment > 72) return 'wide';
        return 'standard';
    }

    function missionRequirementsPanelHtml(rows, unresolved) {
        const visibleRows = rows.filter(row => !row.covered);
        const definiteOutstanding = visibleRows.filter(row => row.definitelyOpen).length;
        const uncertain = visibleRows.filter(row => row.uncertain).length + unresolved.length;
        const fulfilled = rows.length - visibleRows.length;
        const stateName = missionRequirementsOverallState(rows, unresolved);
        const summary = stateName === 'success'
            ? `All ${rows.length} covered`
            : stateName === 'warning'
                ? `${uncertain} need confirmation · ${fulfilled}/${rows.length} covered`
                : `${definiteOutstanding} outstanding · ${fulfilled}/${rows.length} covered`;
        const rowHtml = visibleRows.map(row => {
            const rowState = row.uncertain ? 'unresolved' : row.partial ? 'partial' : 'open';
            const requiredText = row.requiredText || (Number.isFinite(Number(row.missing)) ? Number(row.missing).toLocaleString('en-GB') : '?');
            const onSiteText = row.onSiteText || '?';
            const respondingText = row.respondingText || row.enRouteText || '?';
            const selectedText = row.selectedText || '?';
            const stillText = row.stillNeededText || '?';
            const status = row.uncertain ? 'requires confirmation' : row.partial ? 'partially fulfilled' : 'outstanding';
            const sourceKey = String(row.requirementSource || '').trim().toLowerCase().replace(/[^a-z0-9]+/gu, '-').replace(/^-|-$/gu, '');
            const detail = String(row.definition?.details || row.definition?.detail || '').trim();
            return `<tr data-row-state="${rowState}" data-requirement-key="${escapeHtml(row.key || '')}" data-requirement-source="${escapeHtml(sourceKey)}" data-required="${escapeHtml(requiredText)}" data-on-site="${escapeHtml(onSiteText)}" data-responding="${escapeHtml(respondingText)}" data-selected="${escapeHtml(selectedText)}" data-still-needed="${escapeHtml(stillText)}" title="${escapeHtml(`${row.requirement}: ${status}`)}"><td><span class="mcms-matrix-requirement-name"${detail ? ` title="${escapeHtml(detail)}" aria-label="${escapeHtml(`${row.requirement}. ${detail}`)}"` : ''}>${escapeHtml(row.requirement)}</span></td><td data-label="Required">${escapeHtml(requiredText)}</td><td data-label="On site">${escapeHtml(onSiteText)}</td><td data-label="Respond.">${escapeHtml(respondingText)}</td><td data-label="Selected">${escapeHtml(selectedText)}</td><td class="mcms-req-still" data-label="Need">${escapeHtml(stillText)}</td></tr>`;
        }).join('');
        const tableHtml = visibleRows.length
            ? `<table aria-label="Live mission requirements"><colgroup><col class="mcms-req-name-col"><col class="mcms-req-number-col"><col class="mcms-req-number-col"><col class="mcms-req-number-col"><col class="mcms-req-number-col"><col class="mcms-req-number-col"></colgroup><thead><tr><th scope="col">Requirement</th><th scope="col">Required</th><th scope="col">On site</th><th scope="col">Responding</th><th scope="col">Selected</th><th scope="col">Still needed</th></tr></thead><tbody>${rowHtml}</tbody></table>`
            : '';
        const allCoveredHtml = rows.length && !visibleRows.length && !unresolved.length
            ? '<div class="mcms-req-fallback mcms-req-all-covered" role="status"><span class="mcms-req-fallback-message">All currently known requirements are covered.</span></div>'
            : '';
        const unknownHtml = unresolved.length
            ? `<div class="mcms-req-unknown"><b>Unresolved MissionChief requirement</b>${unresolved.map(item => `<span>${escapeHtml(item.text)}</span>`).join('')}<button type="button" class="mcms-req-report" data-mcms-report-mission>Report Mission</button></div>`
            : '';
        return {
            stateName,
            widthMode: missionRequirementsWidthMode(visibleRows, unresolved),
            html: `<div class="mcms-req-head"><div class="mcms-req-title"><i aria-hidden="true"></i><span>Mission Requirements</span></div><span class="mcms-req-summary">${escapeHtml(summary)}</span><button type="button" class="mcms-req-collapse" data-mcms-requirements-collapse aria-label="Collapse mission requirements" aria-expanded="true">⌃</button></div><div class="mcms-req-body">${tableHtml}${allCoveredHtml}${unknownHtml}</div>`
        };
    }

    function missionRequirementsSafeDiagnostic(value, limit = 600) {
        let text = Array.from(String(value ?? ''), ch => { const code = ch.charCodeAt(0); return code < 32 || code === 127 ? ' ' : ch; }).join('').replace(/\s+/g, ' ').trim();
        text = text
            .replace(/https?:\/\/(?:discord(?:app)?\.com\/api\/webhooks|[^\s/]+\/webhooks)\/\S+/gi, '[redacted webhook]')
            .replace(/\b(?:csrf|authenticity|authorization|session|cookie|token|password|secret|api[_-]?key)\b\s*[:=]\s*[^\s,;]+/gi, match => `${match.split(/[:=]/)[0]}: [redacted]`)
            .replace(/\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi, '[redacted email]')
            .replace(/-?\d{1,3}\.\d{4,}\s*[,/]\s*-?\d{1,3}\.\d{4,}/g, '[redacted coordinates]');
        return text.slice(0, Math.max(0, limit));
    }

    function missionRequirementsTypeSummary(units) {
        const counts = new Map();
        for (const unit of units || []) if (Number.isFinite(unit?.typeId) && unit.typeId >= 0) counts.set(unit.typeId, (counts.get(unit.typeId) || 0) + 1);
        return Array.from(counts.entries()).sort((a, b) => a[0] - b[0]).map(([type, count]) => `${type}×${count}`).join(', ') || 'None detected';
    }

    function missionRequirementsMissionTitle(record) {
        const root = record?.candidate?.root || record?.candidate?.mount;
        const node = root?.querySelector?.('[data-mission-title], #mission_name, .mission-title, .mission_caption, h1');
        return missionRequirementsSafeDiagnostic(node?.getAttribute?.('data-mission-title') || node?.textContent || node?.innerText || '', 100);
    }

    function missionRequirementsReportUrl(record, reason = 'unknown') {
        const candidate = record?.candidate || {};
        const source = record?.source;
        const root = candidate.root || candidate.mount;
        const doc = source?.ownerDocument || root?.ownerDocument;
        const view = doc?.defaultView || pageWindow;
        const missionId = missionRequirementsMissionIdentity(candidate, source) || 'Unknown';
        const title = missionRequirementsMissionTitle(record);
        const missionType = missionRequirementsMissionTypeId(candidate);
        const raw = source?.getAttribute?.('data-mcms-requirements-anchor') === '1' ? '' : missionRequirementsElementText(source);
        let parsed = { requirements: [], unresolved: [] };
        try { if (raw) parsed = missionRequirementsParseSource(source); } catch (err) {}
        missionRequirementsCatalogueEnsure(record);
        const selected = missionRequirementsCollectUnits(candidate, 'selected');
        const responding = missionRequirementsCollectUnits(candidate, 'responding');
        const onSite = missionRequirementsCollectUnits(candidate, 'onsite');
        const classes = Array.from(source?.classList || []).filter(value => /^[A-Za-z0-9_-]{1,40}$/.test(value)).slice(0, 8).join(' ');
        const count = selector => { try { return root?.querySelectorAll?.(selector)?.length || 0; } catch (err) { return 0; } };
        const platform = missionRequirementsSafeDiagnostic(view?.navigator?.userAgentData?.platform || view?.navigator?.platform || 'Unknown', 80);
        const mobile = view?.navigator?.userAgentData?.mobile === true ? 'yes' : 'no/unknown';
        const path = missionRequirementsSafeDiagnostic(view?.location?.pathname || '', 180);
        const mode = state.uiMode || state.operatingMode || (Number(view?.innerWidth) <= 767 ? 'mobile' : Number(view?.innerWidth) <= 1180 ? 'tablet' : 'desktop');
        const fields = [
            '## Automatically harvested Mission Requirements diagnostic',
            '',
            '> Review this report before submitting. No GitHub token, cookies, chat, coordinates, addresses, vehicle IDs or authentication data are included.',
            '',
            `- **Failure reason:** ${missionRequirementsSafeDiagnostic(reason, 120) || 'Unknown'}`,
            `- **Mission ID:** ${missionId}`,
            `- **Mission title:** ${title || 'Unavailable'}`,
            `- **Mission type ID:** ${missionType ?? 'Unavailable'}`,
            `- **MissionChief path:** ${path || 'Unavailable'}`,
            `- **Toolkit version:** ${SCRIPT.version}`,
            `- **Layout:** ${missionRequirementsSafeDiagnostic(mode, 40)}`,
            `- **Viewport:** ${Number(view?.innerWidth) || 0}×${Number(view?.innerHeight) || 0}`,
            `- **Platform:** ${platform}; mobile=${mobile}`,
            '',
            '### Requirement source',
            `- Present: ${source?.getAttribute?.('data-mcms-requirements-anchor') === '1' ? 'No' : 'Yes'}`,
            `- Element: ${missionRequirementsSafeDiagnostic(source?.tagName || 'Unavailable', 30)}#${missionRequirementsSafeDiagnostic(source?.id || '', 60)}`,
            `- Classes: ${missionRequirementsSafeDiagnostic(classes, 180) || 'None'}`,
            `- Typed groups: ${count('[data-requirement-type]')}`,
            `- Parsed rows: ${parsed.requirements.length}`,
            `- Unresolved fragments: ${parsed.unresolved.length}`,
            '',
            ...missionRequirementsCatalogueDiagnosticLines(record, parsed),
            '### Native selector counts',
            `- missing_text: ${count('#missing_text')}`,
            `- selected checkboxes: ${count('.vehicle_checkbox:checked')}`,
            `- responding rows: ${count('#mission_vehicle_driving tbody tr')}`,
            `- on-site rows: ${count('#mission_vehicle_at_mission tbody tr')}`,
            `- patient summary nodes: ${count('#patient_button_form, #patient_button_text')}`,
            `- patient state: ${missionRequirementsSafeDiagnostic(JSON.stringify(missionRequirementsPatientCount(candidate)), 240)}`,
            `- selected vehicle types: ${missionRequirementsTypeSummary(selected)}`,
            `- responding vehicle types: ${missionRequirementsTypeSummary(responding)}`,
            `- on-site vehicle types: ${missionRequirementsTypeSummary(onSite)}`,
            '',
            '### Visible requirement text',
            '```text',
            missionRequirementsSafeDiagnostic(raw, 1200) || 'Unavailable',
            '```'
        ];
        const issueTitle = `Mission requirements missing: ${title || `Mission ${missionId}`}`.slice(0, 180);
        let body = fields.join('\n');
        const build = () => {
            const params = new URLSearchParams({ template: 'mission-info-missing.yml', title: issueTitle, diagnostic: body });
            return `https://github.com/Conroy1988/missionchief-toolkit-assets/issues/new?${params.toString()}`;
        };
        let url = build();
        while (url.length > 7600 && body.length > 1800) {
            body = `${body.slice(0, Math.max(1500, body.length - 500))}\n\n_Report shortened to fit GitHub's issue URL limit._`;
            url = build();
        }
        return url;
    }
    function missionRequirementsFallbackHtml(kind) {
        const loading = kind === 'loading';
        const empty = kind === 'empty';
        const message = loading ? 'Loading mission requirements…' : empty ? 'No outstanding requirements reported by MissionChief.' : 'Unable to pull mission requirements';
        const summary = loading ? 'Loading' : empty ? 'No outstanding requirements' : 'Requirements unavailable';
        const report = loading || empty ? '' : '<button type="button" class="mcms-req-report" data-mcms-report-mission>Report Mission</button>';
        return { stateName: 'warning', html: `<div class="mcms-req-head"><div class="mcms-req-title"><i aria-hidden="true"></i><span>Mission Requirements</span></div><span class="mcms-req-summary">${summary}</span></div><div class="mcms-req-fallback"><span class="mcms-req-fallback-message">${message}</span>${report}</div>` };
    }

    function missionRequirementsPresent(record, presentation, reason = '') {
        record.panel.dataset.state = presentation.stateName;
        record.panel.dataset.mcmsTheme = state.uiTheme;
        record.panel.dataset.widthMode = presentation.widthMode || 'standard';
        if (reason) record.panel.dataset.mcmsReportReason = reason;
        else delete record.panel.dataset.mcmsReportReason;
        setInnerHtmlIfChanged(record.panel, presentation.html);
        const collapse = record.panel.querySelector('[data-mcms-requirements-collapse]');
        if (collapse) {
            const expanded = !record.panel.classList.contains('mcms-collapsed');
            collapse.setAttribute('aria-expanded', String(expanded));
            collapse.setAttribute('aria-label', expanded ? 'Collapse mission requirements' : 'Expand mission requirements');
            collapse.textContent = expanded ? '⌃' : '⌄';
        }
    }

    function missionRequirementsRenderRecord(record) { if (!record?.source?.isConnected || !record?.candidate?.mount?.isConnected || !record?.panel?.isConnected) { scheduleMissionRequirementsScan(0); return; } if (missionRequirementsLssmActive(record.candidate, record.source)) { missionRequirementsRemoveRecord(record.source); return; } missionRequirementsCatalogueEnsure(record); const presentCatalogue = reason => { if (!record.catalogue) return false; missionRequirementsRestoreSource(record.source); missionRequirementsPresent(record, missionRequirementsCataloguePanelHtml({ ...record.catalogue, stale: record.catalogueState === 'stale' }), reason); return true; }; const patientState = missionRequirementsPatientState(record); const reconcile = parsed => missionRequirementsReconcilePatientDemand(missionRequirementsReconcileCatalogue(parsed, record.catalogue, record.catalogueState, Boolean(record.catalogueDescriptor)), patientState); const presentLive = parsed => { const reconciled = reconcile(parsed); if (!reconciled.requirements.length && !reconciled.unresolved.length) return false; if (record.source.getAttribute?.('data-mcms-requirements-anchor') !== '1') missionRequirementsHideSource(record.source); else missionRequirementsRestoreSource(record.source); missionRequirementsPresent( record, missionRequirementsPanelHtml(missionRequirementsResolve(record.candidate, reconciled, record.catalogue), reconciled.unresolved), reconciled.unresolved.length ? 'partially unresolved requirement or patient data' : '' ); return true; }; const age = Date.now() - (record.startedAt || Date.now()); const anchor = record.source.getAttribute?.('data-mcms-requirements-anchor') === '1'; if (anchor) { if (presentLive({ requirements: [], unresolved: [] })) return; if (presentCatalogue('live requirement source absent; official catalogue baseline shown')) return; missionRequirementsRestoreSource(record.source); const loading = record.catalogueState === 'loading' || age < 1200; missionRequirementsPresent(record, missionRequirementsFallbackHtml(loading ? 'loading' : 'error'), loading ? '' : 'requirement source and catalogue unavailable'); return; } const raw = missionRequirementsElementText(record.source); if (!raw) { if (presentLive({ requirements: [], unresolved: [] })) return; missionRequirementsRestoreSource(record.source); missionRequirementsPresent(record, missionRequirementsFallbackHtml(age < 1200 ? 'loading' : 'empty')); return; } let parsed; try { parsed = missionRequirementsParseSource(record.source); } catch (err) { const patientOnly = reconcile({ requirements: [], unresolved: [{ group: 'vehicles', text: `Requirement parser failed: ${err?.message || 'unknown'}` }] }); if (patientOnly.requirements.length) { missionRequirementsHideSource(record.source); missionRequirementsPresent(record, missionRequirementsPanelHtml(missionRequirementsResolve(record.candidate, patientOnly, record.catalogue), patientOnly.unresolved), 'parser exception with patient demand preserved'); return; } if (presentCatalogue(`parser exception; official catalogue baseline shown: ${err?.message || 'unknown'}`)) return; missionRequirementsRestoreSource(record.source); missionRequirementsPresent(record, missionRequirementsFallbackHtml(record.catalogueState === 'loading' ? 'loading' : 'error'), `parser exception: ${err?.message || 'unknown'}`); return; } const reconciled = reconcile(parsed); if (!reconciled.requirements.length) { const authoritativeUnresolved = reconciled.unresolved.some(item => item?.catalogueDerived || item?.authoritativePending || /Requirements for this Mission/iu.test(String(item?.text || ''))); if (authoritativeUnresolved) { missionRequirementsRestoreSource(record.source); missionRequirementsPresent(record, missionRequirementsPanelHtml([], reconciled.unresolved), 'authoritative requirements unresolved'); return; } if (presentCatalogue(reconciled.unresolved.length ? 'live requirement text unparseable; official catalogue baseline shown' : 'no quantified live requirements; official catalogue baseline shown')) return; missionRequirementsRestoreSource(record.source); missionRequirementsPresent(record, missionRequirementsFallbackHtml(record.catalogueState === 'loading' ? 'loading' : 'error'), reconciled.unresolved.length ? 'requirement text unparseable' : 'no quantified requirements detected'); return; } missionRequirementsHideSource(record.source); missionRequirementsPresent(record, missionRequirementsPanelHtml(missionRequirementsResolve(record.candidate, reconciled, record.catalogue), reconciled.unresolved), reconciled.unresolved.length ? 'partially unresolved requirement or patient data' : ''); }

    function missionRequirementsScheduleRecord(record) {
        if (!record || record.frame || runtime.destroyed) return;
        record.frame = runtimeRequestAnimationFrame(() => {
            record.frame = null;
            missionRequirementsRenderRecord(record);
        });
    }

    function missionRequirementsMutationRelevant(record, mutation) {
        const panel = record?.panel;
        const target = mutation?.target;
        if (panel && (target === panel || target?.closest?.(`#${SCRIPT.missionRequirementsPanelId}`))) return false;
        const selector = '#missing_text, [data-mcms-requirements-anchor], #patient_button_form, #patient_button_text, #patient_button_text strong, [id^="patient_"], [data-patient-id], [data-patient], [class*="patient"], [data-patient-count], [data-patient-total], [data-patients], #mission_vehicle_driving, #mission_vehicle_at_mission, #vehicle_show_table_body_all, #occupied, .vehicle_checkbox, [vehicle_type_id], [data-vehicle-type-id], [data-vehicle_type_id], [data-equipment-types], [data-equipment-type], [data-current-personnel], [data-min-personnel], [data-max-personnel], [id^="mission_water_holder"], [id^="mission_foam_holder"], [id^="mission_pump_holder"]';
        return mutationTouchesSelector(mutation, selector);
    }

    function missionRequirementsHostPanels(source){return[...(source?.parentNode?.children||[])].filter(p=>p?.id===SCRIPT.missionRequirementsPanelId||p?.getAttribute?.('data-mcms-requirements-panel')==='1')}
    function missionRequirementsCanonicalPanel(source,p){const a=missionRequirementsHostPanels(source);if(!a.length)return null;p=p&&a.includes(p)?p:a[0];p.setAttribute?.('data-mcms-requirements-panel','1');for(const x of a)if(x!==p)x.remove();return p}
    function missionRequirementsBindPanel(p){if(!p||p.getAttribute?.('data-mcms-requirements-collapse-bound'))return;p.setAttribute?.('data-mcms-requirements-collapse-bound','1');p.addEventListener('click',e=>{const report=e.target?.closest?.('[data-mcms-report-mission]');if(report){const r=Array.from(missionRequirementsRecords.values()).find(x=>x.panel===p);const url=missionRequirementsReportUrl(r,p.dataset.mcmsReportReason||'unresolved requirement text');const opened=pageWindow.open?.(url,'_blank','noopener,noreferrer');try{if(opened)opened.opener=null}catch(err){}return}const b=e.target?.closest?.('[data-mcms-requirements-collapse]');if(!b)return;const c=p.classList.toggle('mcms-collapsed');b.setAttribute('aria-expanded',String(!c));b.setAttribute('aria-label',c?'Expand mission requirements':'Collapse mission requirements');b.textContent=c?'⌄':'⌃'})}
    function missionRequirementsEnsureRecord(candidate, source) {
        let record = missionRequirementsRecords.get(source);
        let panel = missionRequirementsCanonicalPanel(source, record?.panel?.isConnected ? record.panel : null);
        const root = missionRequirementsCandidateRoot(candidate);
        const scopedCandidate = { ...candidate, root, mount: root };
        const missionIdentity = missionRequirementsMissionIdentity(scopedCandidate, source);
        if (record && panel) {
            if (record.missionIdentity && missionIdentity && record.missionIdentity !== missionIdentity) {
                record.catalogueRequestToken = (Number(record.catalogueRequestToken) || 0) + 1;
                record.catalogue = null;
                record.catalogueDescriptor = null;
                record.catalogueState = 'idle';
                record.startedAt = Date.now();
                if (record.patientTransitionTimer) runtimeClearTimeout(record.patientTransitionTimer);
                record.patientTransitionTimer = null;
            }
            record.missionIdentity = missionIdentity;
            record.panel = panel;
            record.candidate = scopedCandidate;
            missionRequirementsPlacePanel(scopedCandidate, source, panel);
            missionRequirementsBindPanel(panel);
            missionRequirementsScheduleRecord(record);
            return record;
        }
        if (record) missionRequirementsRemoveRecord(source);
        const doc = source.ownerDocument || document;
        for (const [otherSource] of missionRequirementsRecords) {
            if (otherSource !== source && otherSource.ownerDocument === doc) missionRequirementsRemoveRecord(otherSource);
        }
        ensureMissionRequirementsDocumentStyle(doc);
        panel = missionRequirementsCanonicalPanel(source);
        if (!panel) {
            panel = doc.createElement('section');
            panel.id = SCRIPT.missionRequirementsPanelId;
            panel.setAttribute('data-mcms-requirements-panel', '1');
            panel.setAttribute('aria-label', 'Live mission requirements');
        }
        missionRequirementsPlacePanel(scopedCandidate, source, panel);
        panel.dataset.mcmsTheme = state.uiTheme;
        missionRequirementsBindPanel(panel);
        record = { candidate: scopedCandidate, source, panel, startedAt: Date.now(), missionIdentity };
        const Observer = doc.defaultView?.MutationObserver || pageWindow.MutationObserver || MutationObserver;
        if (root && typeof Observer === 'function') {
            record.observer = runtimeTrackObserver(new Observer(mutations => mutations.some(mutation => missionRequirementsMutationRelevant(record, mutation)) && missionRequirementsScheduleRecord(record)));
            record.observer.observe(root, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ['checked', 'class', 'style', 'vehicle_type_id', 'data-vehicle-type-id', 'data-vehicle_type_id', 'data-equipment-types', 'data-equipment-type', 'data-current-personnel', 'data-min-personnel', 'data-max-personnel', 'data-patient-count', 'data-patient-total', 'data-patients', 'patient_count', 'patients_count', 'tractive_vehicle_id', 'data-tractive-vehicle-id', 'trailer_id', 'data-trailer-id', 'sortvalue'] });
        }
        missionRequirementsRecords.set(source, record);
        missionRequirementsScheduleRecord(record);
        return record;
    }

    function missionRequirementsRemoveRecord(source) {
        const record = missionRequirementsRecords.get(source);
        if (!record) {
            missionRequirementsRestoreSource(source);
            if (source?.getAttribute?.('data-mcms-requirements-anchor') === '1') source.remove?.();
            return;
        }
        if (record.frame) runtimeCancelAnimationFrame(record.frame);
        if (record.patientTransitionTimer) runtimeClearTimeout(record.patientTransitionTimer);
        record.patientTransitionTimer = null;
        runtimeUntrackObserver(record.observer);
        try { record.panel?.remove(); } catch (err) {}
        missionRequirementsRestoreSource(record.source);
        if (record.source?.getAttribute?.('data-mcms-requirements-anchor') === '1') record.source.remove?.();
        missionRequirementsRecords.delete(source);
    }

    function clearMissionRequirementsPanels() {
        for (const source of Array.from(missionRequirementsRecords.keys())) missionRequirementsRemoveRecord(source);
        missionRequirementsPatientSnapshots.clear();
        for (const context of transportSweepDocumentContexts()) {
            try {
                context.doc.querySelectorAll?.(`#${SCRIPT.missionRequirementsPanelId}`).forEach(panel => panel.remove());
                context.doc.querySelectorAll?.('[data-mcms-requirements-source-hidden="1"]').forEach(missionRequirementsRestoreSource);
                context.doc.querySelectorAll?.('[data-mcms-requirements-anchor="1"]').forEach(anchor => anchor.remove());
            } catch (err) {}
        }
    }

    function scheduleMissionRequirementsScan(delay = 60) {
        runtimeClearTimeout(missionRequirementsScanTimer);
        missionRequirementsScanTimer = runtimeSetTimeout(() => {
            missionRequirementsScanTimer = null;
            scanMissionRequirementsWindows();
        }, Math.max(0, Number(delay) || 0));
    }

    function scanMissionRequirementsWindows() {
        if (runtime.destroyed || !missionRequirementsPrimaryRuntime()) return;
        if (!state.missionRequirements) {
            clearMissionRequirementsPanels();
            return;
        }
        const activeSources = new Set();
        const activeDocuments = new WeakSet();
        for (const candidate of missionRequirementsWindowCandidates()) {
            const source = missionRequirementsSourceForCandidate(candidate) || missionRequirementsAnchorForCandidate(candidate);
            if (!source || source.isConnected === false) continue;
            const doc = source.ownerDocument || candidate?.root?.ownerDocument || document;
            if (!doc || activeDocuments.has(doc)) continue;
            activeDocuments.add(doc);
            ensureMissionRequirementsDocumentStyle(doc);
            if (missionRequirementsLssmActive(candidate, source)) {
                missionRequirementsRemoveRecord(source);
                continue;
            }
            activeSources.add(source);
            missionRequirementsEnsureRecord({ ...candidate, source }, source);
        }
        for (const source of Array.from(missionRequirementsRecords.keys())) {
            if (source.isConnected === false || !activeSources.has(source)) missionRequirementsRemoveRecord(source);
        }
    }

    function missionRequirementsScheduleDocumentRecords(doc) {
        for (const record of missionRequirementsRecords.values()) {
            if (record.source?.ownerDocument === doc) missionRequirementsScheduleRecord(record);
        }
    }

    function observeMissionRequirementsFrame(frame) {
        if (!frame || missionRequirementsObservedFrames.has(frame)) return;
        missionRequirementsObservedFrames.add(frame);
        const onLoad = () => scheduleMissionRequirementsScan(20);
        frame.addEventListener('load', onLoad);
        runtimeOnCleanup(() => frame.removeEventListener('load', onLoad));
    }

    function observeMissionRequirementsDocument(doc) {
        if (!doc) return;
        ensureMissionRequirementsDocumentStyle(doc);
        if (missionRequirementsObservedDocuments.has(doc)) return;
        missionRequirementsObservedDocuments.add(doc);
        try { doc.querySelectorAll('iframe, frame').forEach(observeMissionRequirementsFrame); } catch (err) {}
        runtimeListen(doc, 'change', event => {
            if (!event.target?.matches?.('.vehicle_checkbox, input[type="checkbox"][vehicle_type_id]')) return;
            missionRequirementsScheduleDocumentRecords(doc);
        }, true);
        const root = doc.documentElement || doc.body;
        if (!root) return;
        const activitySelector = '#missing_text, [data-mcms-requirements-anchor], #patient_button_form, #patient_button_text, #patient_button_text strong, [id^="patient_"], [data-patient-id], [data-patient], [class*="patient"], [data-patient-count], [data-patient-total], [data-patients], #mission_vehicle_driving, #mission_vehicle_at_mission, #vehicle_show_table_body_all, #occupied, .vehicle_checkbox, [vehicle_type_id], [data-vehicle-type-id], [data-vehicle_type_id], [data-equipment-types], [data-equipment-type], [data-current-personnel], [data-min-personnel], [data-max-personnel], [id^="mission_water_holder"], [id^="mission_foam_holder"], [id^="mission_pump_holder"], #lightbox_box, #lightbox, .lightbox_content, .modal, [role="dialog"], .ui-dialog, iframe, frame';
        const view = doc.defaultView || pageWindow;
        const MutationObserverCtor = view?.MutationObserver || pageWindow.MutationObserver || MutationObserver;
        const observer = runtimeTrackObserver(new MutationObserverCtor(mutations => {
            const relevant = mutations.some(mutation => {
                if (mutation.target?.closest?.(`#${SCRIPT.missionRequirementsPanelId}`)) return false;
                if (mutationTouchesSelector(mutation, activitySelector)) return true;
                return false;
            });
            if (!relevant) return;
            try { doc.querySelectorAll('iframe, frame').forEach(observeMissionRequirementsFrame); } catch (err) {}
            scheduleMissionRequirementsScan(35);
            missionRequirementsScheduleDocumentRecords(doc);
        }));
        observer.observe(root, { childList: true, subtree: true, characterData: true });
    }

    function installMissionRequirementsWindows() {
        if (!missionRequirementsPrimaryRuntime()) return;
        if (!missionRequirementsFeatureInstalled) {
            missionRequirementsFeatureInstalled = true;
            runtimeOnCleanup(() => {
                runtimeClearTimeout(missionRequirementsScanTimer);
                missionRequirementsScanTimer = null;
                clearMissionRequirementsPanels();
                for (const context of transportSweepDocumentContexts()) {
                    try { context.doc.getElementById?.(SCRIPT.missionRequirementsDocumentStyleId)?.remove(); } catch (err) {}
                }
            });
        }
        for (const context of transportSweepDocumentContexts()) observeMissionRequirementsDocument(context.doc);
        scheduleMissionRequirementsScan(0);
        runtimeSetTimeout(() => scheduleMissionRequirementsScan(0), 180);
        runtimeSetTimeout(() => scheduleMissionRequirementsScan(0), 800);
        runtimeSetTimeout(() => scheduleMissionRequirementsScan(0), 1600);
    }





