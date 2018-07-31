import os
import pint
from kubernetes import client, config, watch

def main():
    #setup the namespace
    ns = os.getenv("kubia")

    if ns is None:
        ns = ""

    unit = pint.UnitRegistry()

    unit.define('yocto = 1e-24 = y')
    unit.define('zepto = 1e-21 = z')
    unit.define('atto = 1e-18 = a')
    unit.define('femto = 1e-15 = f')
    unit.define('pico = 1e-12 = p')
    unit.define('nano = 1e-9 = n')
    unit.define('micro = 1e-6 = µ')
    unit.define('mili = 1e-3 = m')
    unit.define('centi = 1e-2 = c')
    unit.define('deci = 1e-1 = d')
    unit.define('deca = 1e+1 = da')
    unit.define('hecto = 1e2 = h')
    unit.define('kilo = 1e3 = k')
    unit.define('mega = 1e6 = M')
    unit.define('giga = 1e9 = G')
    unit.define('tera = 1e12 = T')
    unit.define('peta = 1e15 = P')
    unit.define('exa = 1e18 = E')
    unit.define('zetta = 1e21 = Z')
    unit.define('yotta = 1e24 = Y')

    unit.define('kibi = 2**10 = Ki')
    unit.define('mebi = 2**20 = Mi')
    unit.define('gibi = 2**30 = Gi')
    unit.define('tebi = 2**40 = Ti')
    unit.define('pebi = 2**50 = Pi')
    unit.define('exbi = 2**60 = Ei')
    unit.define('zebi = 2**70 = Zi')
    unit.define('yobi = 2**80 = Yi')

    max_claims = unit.Quantity("1200Gi")
    total_claims = unit.Quantity("0Gi")

    config.load_kube_config()
    api = client.CoreV1Api()

    pvcs = api.list_namespaced_persistent_volume_claim(namespace=ns, watch=False)
    print("")
    print("---PVCs---")
    for pvc in pvcs.items:
        print("%-16s\t%-40s\t%-6s" % (pvc.metadata.name, pvc.spec.volume_name, pvc.spec.resources.requests['storage']))
    print("")

    w = watch.Watch()
    for item in w.stream(api.list_namespaced_persistent_volume_claim, namespace=ns, timeout_seconds=0):
        pvc = item['object'];

        # parse PVC events
        # new PVC added
        if item['type'] == 'ADDED':
            size = pvc.spec.resources.requests['storage']
            claimQty = unit.Quantity(size)
            total_claims = total_claims + claimQty

            print("PVC Added: %s; size %s" % (pvc.metadata.name, size))

            if total_claims >= max_claims:
                print("---------------------------------------------")
                print("WARNING: claim overage reached; max %s; at %s" % (max_claims, total_claims))
                print("**** Trigger over capacity action ***")
                print("---------------------------------------------")

        # PVC is removed
        if item['type'] == 'DELETED':
            size = pvc.spec.resources.requests['storage']
            claimQty = unit.Quantity(size)
            total_claims = total_claims - claimQty

            print("PVC Deleted: %s; size %s" % (pvc.metadata.name, size))

            if total_claims <= max_claims:
                print("---------------------------------------------")
                print("INFO: claim usage normal; max %s; at %s" % (max_claims, total_claims))
                print("---------------------------------------------")

        # PVC is updated
        if item['type'] == 'MODIFIED':
            print("MODIFIED: %s" % (pvc.metadata.name))

        print("INFO: total PVC at %4.1f%% capacity" % ((total_claims/max_claims)*100))

if __name__ == '__main__':
    main()
