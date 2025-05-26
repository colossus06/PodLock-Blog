---
myst:
  html_meta:
    "description lang=en": "This article breaks down the networking path a pod inherits at creation, using a Minikube cluster running Kubernetes with Kindnet. You'll see how the Kindnet CNI assigns IPs from the node’s PodCIDR, creates veth pairs linking the pod to the host network, and installs routing rules that define how the pod communicates within the cluster."
    "keywords": "Kubernetes, CNI, Kindnet, veth pair, pod networking, DevOps, Linux namespaces, Gulcan Topcu, Minikube, ptp plugin"
    "property=og:locale": "en_US"
    "property=og:image": "https://raw.githubusercontent.com/colossus06/PodLock-Blog/main/og/ptp.png"
---

<img src="https://raw.githubusercontent.com/colossus06/PodLock-Blog/main/og/ptp.png" alt="ptp" class="bg-primary">
 
(ptp)=
# Inside a Pod’s Birth: Veth Pairs, IPAM, and Routing with Kindnet CNI

When a Kubernetes pod starts, it doesn't just spin up a container. It gets a full, isolated network stack—complete with its own IP address, routing table, and virtual interface. But how exactly does this happen under the hood, especially when using the Kindnet CNI plugin?

This article breaks down the networking path a pod inherits at creation, using a Minikube cluster running Kubernetes with Kindnet. You'll see how the Kindnet CNI assigns IPs from the node’s PodCIDR, creates veth pairs linking the pod to the host network, and installs routing rules that define how the pod communicates within the cluster.

## Kubernetes CNI Requirements Are Simpler Than You Think

The Container Network Interface (CNI) standard is flexible enough to serve a range of environments—Kubernetes is just one of them. But Kubernetes only requires two core capabilities from a CNI plugin: At its core, Kubernetes just needs the CNI plugin to handle IP assignment and create a network interface. That's it!

For IP Address Management, the CNI simply needs to allocate addresses from the node's PodCIDR range. Think of this like assigning apartment numbers in a building—each pod gets its own unique address within the node's designated block.

As for interface configuration, the CNI creates a virtual network interface inside the pod's network namespace. This is installing the network "doorway" that connects the pod to the outside world.

To achieve this Kindnet uses well-known CNI reference plugins.

## Kindnet's Approach

Kubernetes itself doesn’t handle IP assignments or interface configurations directly. Instead, it delegates this task to a Container Network Interface (CNI) plugin. Kindnet uses a configuration directory to define how networking is set up. Let’s inspect this directory:

```bash
minikube ssh
cd /etc/cni/net.d/ && ls -la
-rw-r - r - 1 10-kindnet.conflist
-rw-r - r - 1 100-crio-bridge.conf.mk_disabled
-rw-r - r - 1 200-loopback.conf
-rw-r - r - 1 87-podman-bridge.conflist.mk_disabled
cat 10-kindnet.conflist


{
        "cniVersion": "0.3.1",
        "name": "kindnet",
        "plugins": [
        {
                "type": "ptp",
                "ipMasq": false,
                "ipam": {
                        "type": "host-local",
                        "dataDir": "/run/cni-ipam-state",
                        "routes": [


                                { "dst": "0.0.0.0/0" }
                        ],
                        "ranges": [


                                [ { "subnet": "10.244.0.0/24" } ]
                        ]
                }
                ,
                "mtu": 1500

        },
        {
                "type": "portmap",
                "capabilities": {
                        "portMappings": true
                }
        }
        ]
}
```

The `ptp` plugin creates the veth pair connecting the pod to the host—think of this as a virtual network cable stretched between two points. One end lives in the pod's network namespace while the other stays in the host network. The host-side veth gets assigned the IP `.1` in the pod's subnet (used as gateway).

The `host-local` plugin handles IP allocation, drawing addresses from the node's PodCIDR range. This ensures each pod gets its own unique address without stepping on any network toes.

## Tracking a Pod's Network Lifecycle

Let me walk you through what happens when you run a simple deployment. In our two node minikube cluster, we have three pods:

```bash
minikube      control-plane v1.32.0   192.168.49.2
minikube-m02  <none>        v1.32.0   192.168.49.3

pod-to-pod-6d4875f88c-5qcw5   10.244.1.2   minikube-m02
pod-to-pod-6d4875f88c-99qwj   10.244.1.3   minikube-m02
pod-to-pod-6d4875f88c-mfm7t   10.244.0.3   minikube
```

Two pods might be on the same physical machine—but can they interfere with each other? No. Because Kubernetes guarantees isolation using **Linux network namespaces**.

## Namespaces

Each Kubernetes pod runs inside its own isolated Linux network namespace. This namespace has its own interfaces, routing table, and iptables rules. From the pod's perspective, it’s the entire network stack—isolated from every other pod and the host.

Let's get a shell inside the pod running on minikube node and list network interfaces:

```bash
k exec -it pod-to-pod-6d4875f88c-mfm7t  -- bash

ls /sys/class/net
eth0  lo
```

Within the pod's isolated namespace, two interfaces are present by default: `lo`, the loopback used for intra-pod communication (e.g., `localhost` bindings), and `eth0`, which handles all ingress and egress traffic outside the pod.

But `eth0` isn’t backed by a physical interface. Instead, it's one end of a virtual Ethernet device—*a veth pair*.

What is a veth pair?

## The Veth Pair: Your Pod’s Pipe to the Host

When a pod is created, the container runtime invokes the CNI plugin with an `ADD` command. Kindnet responds by generating a **veth pair**—a linked virtual Ethernet device.

An interface index (or ifindex) is a unique integer assigned by the Linux kernel to every network interface on the system. When you create a veth pair, each side gets its own ifindex:

* One end of the pair becomes `eth0` **inside** the pod's private network namespace.
* The other end lives in the **host** namespace and is assigned the gateway IP `10.244.X.1/32`.

Let's get the interface index for `eth0` on the pod:

```bash
cat /sys/class/net/eth0/ifindex
2
```

We can identify the host veth paired with eth0 using ifindex correlation by running the following:

```bash
ip -br a
lo               UNKNOWN        127.0.0.1/8 ::1/128 
eth0@if3         UP             10.244.0.2/24 fe80::683b:1eff:fe76:37ad/64 
```

`if3` means `eth0` is inside the pod, and it's peer-linked to **interface with index 3 on the host**. So, that index (3) refers to the host-side interface's ifindex!

This brings to me to a question then: can i match this ifX to Host vethXXXX?

To know it we rely on two facts:

* pod's `eth0` is the inside end of a veth pair and it is linked to host interface index 3.
* `vethX` is interface index 3 on the minikube node, and it's linked to interface index 2, which is in the pod as we've seen above.

If we list all host-side veth interfaces and interface index 3 on the Minikube node, we should see `ifindex=2`:

```bash
m ssh
ip -br addr | grep veth
vethffa2ff74@if2 UP             10.244.0.1/32 fe80::e4e5:97ff:feea:4a03/64 
veth4fc93ebb@if2 UP             10.244.0.1/32 fe80::6074:acff:fefa:853a/64 

ip -o link | grep ^3:
3: vethffa2ff74@if2: UP link-netnsid 1
```

The host-side veth that's paired with the pod's `eth0` is interface index 2 inside the pod!

## The host-side veth IP

Notice those `10.244.0.1/32` addresses assigned to the veth interfaces? They're the gateway IPs our pods are configured to use and it exists inside each pod's routing table.

The `/32` subnet mask (meaning a single-host network) is Kindnet's way of handling pod-to-host routing without complex bridge devices. Each veth pair becomes a simple point-to-point link, creating a direct pipeline for packets to flow between the pod and the host. Inside the pod, look at the routing table:

```bash
kubectl exec -it pod-to-pod-6d4875f88c-mfm7t -- sh 
apt update && apt install -y iproute2

ip route
default via 10.244.0.1 dev eth0
10.244.0.0/24 via 10.244.0.1 dev eth0 src 10.244.0.2 
10.244.0.1 dev eth0 scope link src 10.244.0.2
```

Let's take a look at them one by one.

`default via 10.244.0.1 dev eth0` means if a packet is destined for any IP not explicitly matched by a more specific route, kernel sends it to 10.244.0.1 using the `eth0` interface. So if we curl `1.1.1.1` or hit `8.8.8.8` from the pod, this is the route that applies. The packet will go to 10.244.0.1.

`10.244.0.0/24 via 10.244.0.1 dev eth0 src 10.244.0.2` says to reach any IP in the range `10.244.0.0/24` (for example other pods on this node), send traffic via the gateway on `eth0`, using `10.244.0.2` as the source IP. Even though the destination is "local", it still sends the packet to `10.244.0.1`.

Both of the other routes in the pod’s table—the `/24` and default—rely on forwarding to `10.244.0.1`. But for Linux to send anything to 10.244.0.1, it needs to understand how to reach it.

`10.244.0.1 dev eth0 scope link src 10.244.0.2` says to reach `10.244.0.1`, send traffic directly over `eth0` because it is on the same Ethernet segment as me.

Now jump to the minikube host:

```bash
ip route | grep 10.244
10.244.0.2 dev vethffa2ff74 scope host       # Pod mfm7t (local) → its veth interface
10.244.1.0/24 via 192.168.49.3 dev eth0      # Route to node minikube-m02 (Pod 5qcw5 and 99qwj)
```

`10.244.0.2 dev vethffa2ff74 scope host` maps Pod mfm7t's IP to its veth on the host. When traffic comes in from outside the pod, the kernel delivers it through this interface.

`10.244.1.0/24 via 192.168.49.3 dev eth0` tells the host to forward traffic for any pod on `minikube-m02` out via its `eth0`, using the internal IP `192.168.49.3` of `minikube-m02`.

To summarize, when Kubernetes schedules a pod, it hands off setting up thenetworking to the CNI. Kindnet takes over and wires the pod into the cluster network. This setup gives the pod a routable IP, a default gateway, and a clean L3 path out through the host. But what happens when it starts talking to another pod?

➡️ Up next: **Inside Intra-Node Pod Traffic in Kubernetes: How Kindnet with PTP Moves Packets** where we trace packets from one pod to another on the same node.

## References

* [CNI Specification v1.0.0 – Container Networking Interface](https://github.com/containernetworking/cni/blob/main/SPEC.md)
* [Kindnetd Plugin Source Code](https://github.com/kubernetes-sigs/kind/tree/main/images/kindnetd)
* [The Kubernetes Networking Guide – Kindnet](https://kubernetes.networking.guide/cni/kindnet/)
* [Kubernetes CNI Plugin Architecture](https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/network-plugins/)
* [`iproute2` Linux Manual Pages](https://man7.org/linux/man-pages/man8/ip-route.8.html)
* [Understanding Linux Network Namespaces and veth Pairs](https://man7.org/linux/man-pages/man7/namespaces.7.html)

**Enjoyed this read?**

If you found this guide helpful,check our blog archives 📚✨

- Follow me on [LinkedIn](https://www.linkedin.com/in/gulcantopcu/) to get updated.
- Read incredible Kubernetes Stories: [Medium](https://medium.com/@gulcantopcu)
- Challenging projects: You're already in the right place.

Until next time!