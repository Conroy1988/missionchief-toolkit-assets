PAYLOAD = r'''    function missionRequirementsSourceForCandidate(candidate) {
        const root = candidate?.root;
        const supplied = candidate?.source;
        const suppliedIsAnchor = supplied?.getAttribute?.('data-mcms-requirements-anchor') === '1';
        if (supplied && supplied.isConnected !== false && !suppliedIsAnchor) return supplied;
        if (!root?.querySelector) return supplied?.isConnected !== false ? supplied : null;
        const native = root.matches?.('#missing_text') ? root : root.querySelector('#missing_text');
        return native || (supplied?.isConnected !== false ? supplied : null);
    }'''
