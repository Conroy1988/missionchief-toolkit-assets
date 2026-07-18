PAYLOAD = r'''    function missionRequirementsAnchorForCandidate(candidate) {
        const root = candidate?.root || candidate?.mount;
        if (!root?.ownerDocument?.createElement) return null;
        let anchor = Array.from(root.children || []).find(node => node?.getAttribute?.('data-mcms-requirements-anchor') === '1')
            || root.querySelector?.('[data-mcms-requirements-anchor="1"]');
        if (anchor?.isConnected !== false) return anchor;
        anchor = root.ownerDocument.createElement('span');
        anchor.hidden = true;
        anchor.setAttribute('aria-hidden', 'true');
        anchor.setAttribute('data-mcms-requirements-anchor', '1');
        root.insertBefore?.(anchor, root.firstChild || null);
        return anchor;
    }

    function missionRequirementsCandidateRoot(candidate) {
        const root = candidate?.root || candidate?.mount;
        if (!root) return null;
        if (root.matches?.('#mission_form, form[action*="/missions/"], #mission_content')) return root;
        return root.querySelector?.('#mission_form, form[action*="/missions/"], #mission_content') || root;
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
    function missionRequirementsWindowCandidates(){const a=[],s=new Set(),roots=new Set(),add=(c,trusted=false)=>{const root=missionRequirementsCandidateRoot(c);if(!root||roots.has(root))return;let x=missionRequirementsSourceForCandidate({...c,root});if(!x){if(!trusted&&!missionRequirementsLooksLikeWindow({...c,root}))return;x=missionRequirementsAnchorForCandidate({...c,root})}if(!x||x.isConnected===false||s.has(x))return;roots.add(root);s.add(x);a.push({...c,root,mount:c?.mount||root,source:x})};missionValueWindowCandidates().forEach(c=>add(c,true));for(const c of transportSweepDocumentContexts()){const d=c?.doc;if(!d?.querySelectorAll)continue;for(const x of d.querySelectorAll('#missing_text'))add(missionRequirementsCandidateFromSource(x),true);for(const r of d.querySelectorAll('#mission_form, form[action*="/missions/"], #mission_content'))add({root:r,mount:r},false)}const ids=new Set();return a.sort((x,y)=>4*((y.source?.getAttribute?.('data-mcms-requirements-anchor')!=='1')-(x.source?.getAttribute?.('data-mcms-requirements-anchor')!=='1'))+2*(missionRequirementsRecords.has(y.source)-missionRequirementsRecords.has(x.source))+isVisible(y.root)-isVisible(x.root)).filter(c=>{const id=missionRequirementsMissionIdentity(c,c.source);return!id||!ids.has(id)&&(ids.add(id),true)})}
'''
