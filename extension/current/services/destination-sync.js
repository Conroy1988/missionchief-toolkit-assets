// Cloud-first secret sync. Kept separate from safe preference exports.
export async function syncDestination({local,base,remote,restoring,writeCloud,writeLocal,saveBase}) {
 const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
 const cloud=remote?.destination;
 let desired=local;
 if(remote){
  if(restoring||!base||same(local,base))desired=cloud;
  else if(!same(cloud,base)&&!same(cloud,local))throw Error('The Toolkit webhook changed on another device. Reconnect Discord to restore that destination before editing it.');
 }
 if(!remote||!same(desired,cloud))await writeCloud(desired,remote?.revision||0);
 if(!same(local,desired))await writeLocal(desired);
 await saveBase(desired);
 return desired;
}
