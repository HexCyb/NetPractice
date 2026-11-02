#!/usr/bin/env python3
"""Subnet calculator for NetPractice.

  python3 subnet.py 192.168.1.130/26            -> network, broadcast, usable hosts, mask
  python3 subnet.py 192.168.1.130 255.255.255.192
  python3 subnet.py 10.0.0.5/30 10.0.0.6        -> are both addresses in the same subnet?
"""
import sys


def to_int(ip):
    parts = [int(p) for p in ip.split(".")]
    if len(parts) != 4 or any(p < 0 or p > 255 for p in parts):
        raise ValueError(f"bad IPv4 address: {ip}")
    return (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]


def to_ip(n):
    return ".".join(str((n >> shift) & 255) for shift in (24, 16, 8, 0))


def parse(text, mask_arg=None):
    """'1.2.3.4/24' or ('1.2.3.4', '255.255.255.0') -> (address, prefix length)"""
    if "/" in text:
        ip, prefix = text.split("/")
        return to_int(ip), int(prefix)
    mask = to_int(mask_arg)
    prefix = bin(mask).count("1")
    if mask != (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF:
        raise ValueError(f"not a valid mask: {mask_arg}")
    return to_int(text), prefix


def describe(addr, prefix):
    mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
    network = addr & mask
    broadcast = network | (~mask & 0xFFFFFFFF)
    size = 2 ** (32 - prefix)
    print(f"address    {to_ip(addr)}/{prefix}")
    print(f"mask       {to_ip(mask)}   (block size {size})")
    print(f"network    {to_ip(network)}")
    print(f"broadcast  {to_ip(broadcast)}")
    if prefix <= 30:
        print(f"hosts      {to_ip(network + 1)} - {to_ip(broadcast - 1)}   ({size - 2} usable)")
    if addr in (network, broadcast) and prefix <= 30:
        print("warning    this is the network or broadcast address: a host cannot use it")
    return network, mask


def main(args):
    if not args:
        print(__doc__)
        return 1
    if len(args) == 2 and "/" not in args[0]:
        describe(*parse(args[0], args[1]))
        return 0
    addr, prefix = parse(args[0])
    network, mask = describe(addr, prefix)
    for other in args[1:]:
        same = (to_int(other) & mask) == network
        print(f"{other:<15}{'same subnet' if same else 'DIFFERENT subnet'}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except ValueError as error:
        print(f"error: {error}")
        sys.exit(1)
