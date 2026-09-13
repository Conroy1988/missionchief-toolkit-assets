// Observed in the live UK Home Response vehicle shop, 2026-09-13.
// Guide prices only: execution must parse the current native Credit purchase link.
export const VEHICLES = [
 [3,'Fire Officer',10000,''],[10,'Rapid Response Vehicle',4000,''],
 [20,'Operational Team Leader',20000,''],[21,'General Practitioner',4000,'Critical care'],
 [22,'Community First Responder',2500,''],[34,'Ambulance Officer',25500,'Ambulance Officer'],
 [95,'Community Midwife',10000,'Midwifery Training'],[96,'Specialist Paramedic RRV',10000,'Specialist Paramedic Training'],
 [92,'Personal SAR Vehicle',10000,''],[93,'SAR 4x4',10000,''],[101,'Search Dog Unit',15000,'Dog handling'],
 [57,'Coastguard Rescue Vehicle',20000,''],[60,'Coastguard Commander',25000,'Coastal Command Training'],
 [12,'Dog Support Unit',7000,'Dog handling']
].map(([id,name,credits,training])=>Object.freeze({id,name,credits,training}));
