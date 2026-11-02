# NetPractice

Ten small networks to repair in a browser. You give hosts and routers IP addresses, masks and routes until every packet arrives. The values change on every attempt, so this repository explains **how** to solve each level instead of listing answers. It also includes a small calculator, `tools/subnet.py`.

> Originally completed at **42 Türkiye** as part of the common core. This repository is a 2026 rewrite, because the original notes were lost.
> 42 Türkiye'de tamamladığım projenin 2026'da yeniden yazılmış hali; orijinal notlar kayboldu.

## The four rules that solve every level

1. **Same network = same network part.** Two interfaces can talk directly only if `IP AND mask` gives the same result on both sides. Both sides must use the same mask.
2. **Never use the first or last address of a block.** The first is the network address and the last is the broadcast address. A `/30` has 4 addresses and only 2 usable ones.
3. **Subnets must not overlap.** Every link between routers needs its own block. Two networks on the same router cannot share addresses.
4. **Every packet needs a way out and a way back.** A host sends anything outside its subnet to its **gateway**, which is the IP of the router interface on its own subnet. A router needs a route for each network it does not touch directly, in **both** directions.

## Masks at a glance

| CIDR | Mask | Block size | Usable hosts |
|---|---|---|---|
| /24 | 255.255.255.0 | 256 | 254 |
| /25 | 255.255.255.128 | 128 | 126 |
| /26 | 255.255.255.192 | 64 | 62 |
| /27 | 255.255.255.224 | 32 | 30 |
| /28 | 255.255.255.240 | 16 | 14 |
| /29 | 255.255.255.248 | 8 | 6 |
| /30 | 255.255.255.252 | 4 | 2 |

Blocks always start at a multiple of their size. A `/26` starts at .0, .64, .128 or .192, so .130/26 belongs to the block .128 – .191.

Addresses you cannot give to a host: `127.x.x.x` (loopback), `0.x.x.x`. Private ranges, which the Internet never routes: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`.

## Level by level

| Level | What is new | How to solve it |
|---|---|---|
| 1 | Two pairs of hosts | Give each host of a pair an IP in the other's network (same network part, same mask) |
| 2 | Masks to fill in, `/30` | Copy the mask to both sides. Pick the 2 usable addresses of the block, never .0 or the broadcast |
| 3 | A switch with 3 hosts | A switch is one network: one mask for everyone, and every IP in that block |
| 4 | A router | The host and the router interface facing it share a subnet. The router's other interfaces must use different blocks |
| 5 | Routes on hosts | Each host gets `default` → the IP of its router's interface. Both hosts need it |
| 6 | The Internet | The router needs `default` → the Internet. The Internet needs a route **back** to your subnet: destination = your network/mask, next hop = your router |
| 7 | Two routers, three networks | Split the given range into 3 non-overlapping blocks (for example three `/28`s). Each router needs a route to the network behind the other router |
| 8 | Routers + Internet | Same as 7, plus the Internet's way back. That return route can cover several of your subnets with one bigger block |
| 9 | Many hosts and routers | Draw it: for every pair of machines that must talk, follow the packet hop by hop, then do it again backwards |
| 10 | Everything | Fix overlaps first, then the gateways, then the routes. Check the Internet's way back last |

## The calculator

```sh
python3 tools/subnet.py 192.168.1.130/26
# address    192.168.1.130/26
# mask       255.255.255.192   (block size 64)
# network    192.168.1.128
# broadcast  192.168.1.191
# hosts      192.168.1.129 - 192.168.1.190   (62 usable)

python3 tools/subnet.py 10.0.0.5/30 10.0.0.6 10.0.0.9
# ...
# 10.0.0.6       same subnet
# 10.0.0.9       DIFFERENT subnet
```
