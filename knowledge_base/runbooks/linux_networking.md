# Linux Networking Troubleshooting Runbook

## 1. Purpose

This runbook provides a systematic procedure for diagnosing common Linux networking problems. It covers network interface status, IP addressing, routing, DNS resolution, connectivity, listening ports, and network-related system logs.

The objective is to identify the cause of a connectivity problem before making changes to the system's network configuration.

## 2. Common Symptoms of Network Problems

Common networking symptoms include:

- The system cannot access the internet.
- A remote server cannot be reached.
- A hostname fails to resolve to an IP address.
- An application cannot connect to a service on a particular port.
- A network interface is down or has no IP address.
- Connections are slow or frequently interrupted.
- A service is running but cannot be accessed remotely.
- Network connections fail after a configuration change or system restart.

A symptom alone does not establish the cause. Investigate the interface, IP configuration, routing, DNS, and service state as appropriate.

## 3. Step One: Inspect Network Interfaces

Run:

```bash
ip link show
```

This displays network interfaces and their link states.

To inspect IP addresses assigned to interfaces, run:

```bash
ip addr show
```

Alternatively:

```bash
ip -br addr
```

The brief output makes it easier to identify interfaces and their assigned addresses.

Investigate the following:

- Whether the expected interface exists.
- Whether the interface is administratively enabled.
- Whether an appropriate IP address is assigned.
- Whether the interface has an unexpected state.
- Whether the address belongs to the expected network.

An interface shown as `DOWN` may be disabled or disconnected. An interface shown as `UP` does not, by itself, prove that internet connectivity is working.

## 4. Step Two: Inspect the Routing Table

Run:

```bash
ip route show
```

The routing table determines where packets are sent.

Look for a default route when the system is expected to reach destinations outside its local network.

Example:

```text
default via 192.168.1.1 dev eth0
```

In this example, traffic without a more specific matching route is directed through gateway `192.168.1.1` using interface `eth0`.

To inspect the route selected for a destination, run:

```bash
ip route get 8.8.8.8
```

Investigate missing or unexpected routes, incorrect gateways, and interfaces that do not match the intended network configuration.

Do not add or replace routes until the expected network configuration is understood.

## 5. Step Three: Test Basic Network Connectivity

Use `ping` to test reachability to a known IP address:

```bash
ping -c 4 8.8.8.8
```

The `-c 4` option sends four echo requests and then stops.

Interpret the result carefully:

- Replies indicate that the destination responded to ICMP echo requests.
- Packet loss may indicate connectivity problems, congestion, filtering, or an unreliable path.
- No replies do not prove that the destination is unreachable because ICMP traffic may be blocked.

If the destination does not respond, inspect the interface and routing table before concluding that the internet connection is down.

Where possible, compare the result with another known destination or a system on the same network.

## 6. Step Four: Diagnose DNS Resolution

DNS translates hostnames into IP addresses.

Test hostname resolution using:

```bash
getent hosts example.com
```

If `dig` is installed, you can also run:

```bash
dig example.com
```

If `nslookup` is installed, another option is:

```bash
nslookup example.com
```

Interpret the results:

- If an IP address is returned, the hostname resolved successfully through the tested resolver path.
- If resolution fails but connectivity to a known IP address works, investigate DNS configuration.
- If both hostname resolution and IP connectivity fail, investigate the interface, routing, and upstream network before focusing exclusively on DNS.

Inspect resolver configuration with:

```bash
cat /etc/resolv.conf
```

On systems using `systemd-resolved`, inspect resolver status with:

```bash
resolvectl status
```

The availability and behavior of these tools depend on the Linux distribution and its networking configuration.

Avoid replacing resolver configuration blindly, particularly on systems where NetworkManager, DHCP, containers, or `systemd-resolved` manages it.

## 7. Step Five: Check Listening Ports and Services

When an application cannot be reached, determine whether the expected service is listening on the required port.

Run:

```bash
sudo ss -tulpn
```

This displays listening TCP and UDP sockets, along with process information where permissions allow.

To inspect TCP listening sockets specifically, run:

```bash
sudo ss -ltnp
```

Check the following:

- Whether the expected port is listening.
- Whether the correct application owns the listening socket.
- Whether the service listens on `127.0.0.1` only or on an address reachable from other systems.
- Whether another process is using the expected port.

A service bound only to `127.0.0.1` normally accepts connections from the local host, not directly from remote hosts.

Do not expose a service to all network interfaces unless its security requirements and firewall rules permit it.

## 8. Step Six: Test Application Port Connectivity

If a service should be reachable on a known host and TCP port, use:

```bash
nc -vz HOST PORT
```

Replace `HOST` with the target hostname or IP address and `PORT` with the expected TCP port.

For example:

```bash
nc -vz 192.168.1.20 22
```

This tests whether a TCP connection can be established to port 22 on the example host.

The `nc` command may need to be installed. Option availability varies between implementations.

A successful TCP connection confirms that the connection was established; it does not prove that the application is functioning correctly at the application layer.

If the connection fails, check the destination service, listening address, routing, and applicable firewall rules.

## 9. Step Seven: Inspect Network-Related Logs

Inspect recent system messages:

```bash
journalctl --since "1 hour ago"
```

To inspect kernel messages, run:

```bash
journalctl -k --since "1 hour ago"
```

Search the output for relevant events such as:

- Network interface state changes.
- Link disconnections and reconnections.
- DHCP failures or address assignment problems.
- Driver or device errors.
- Resolver or network-management failures.

For a particular systemd-managed service, inspect its status and recent logs:

```bash
systemctl status SERVICE_NAME
```

```bash
journalctl -u SERVICE_NAME --since "1 hour ago"
```

Replace `SERVICE_NAME` with the actual service name.

Access to some logs may require elevated privileges. Use `sudo` when necessary and permitted.

## 10. Step Eight: Check Firewall Rules

Firewall rules can prevent incoming or outgoing traffic even when the interface and routing table appear correct.

On systems using nftables, inspect the rules with:

```bash
sudo nft list ruleset
```

If the system uses iptables, inspect its rules with:

```bash
sudo iptables -L -n -v
```

Use the firewall system actually configured on the machine. These tools do not necessarily represent every firewall or network policy in use.

Check whether the required traffic is permitted and whether rules apply to the relevant interface, protocol, address, and port.

Do not flush firewall rules or disable the firewall as a first troubleshooting step. Doing so can expose services or interrupt legitimate network access.

## 11. Step Nine: Apply Safe Corrective Actions

After identifying the likely cause, choose the smallest appropriate corrective action.

Examples include:

- Correcting an application hostname or port.
- Starting an approved service that is unexpectedly stopped.
- Correcting a verified configuration error.
- Restoring a missing route through the approved network-management process.
- Correcting DNS settings through the system's configured network manager.
- Adjusting a firewall rule through the authorized change process.

Before modifying network settings on a remote machine, consider whether the change could terminate your SSH session or make the machine inaccessible.

Record the original configuration where appropriate, follow organizational procedures, and avoid changes whose effects are not understood.

## 12. Verification

After applying a corrective action, repeat the tests related to the original failure.

For example:

```bash
ip -br addr
```

```bash
ip route show
```

```bash
getent hosts example.com
```

```bash
ping -c 4 8.8.8.8
```

If a specific service was inaccessible, also test its expected port:

```bash
nc -vz HOST PORT
```

Verify that:

- The required interface has the expected state and address.
- The routing table contains the expected route.
- DNS resolution works if the problem involved a hostname.
- The required service is listening and reachable.
- Relevant logs no longer show the same recurring failure.
- The original application or user operation succeeds.

A successful ping alone does not prove that a particular application or TCP port is working.

## 13. Troubleshooting Summary

| Symptom | Initial command | What to investigate |
|---|---|---|
| Interface missing or down | `ip link show` | Interface state and device availability |
| Incorrect or missing IP address | `ip -br addr` | Address assignment and interface configuration |
| Remote IP unreachable | `ip route show` | Default route, gateway, and network path |
| Hostname does not resolve | `getent hosts example.com` | DNS resolver configuration |
| Application port unreachable | `ss -ltnp` | Listening socket and service state |
| TCP connection fails | `nc -vz HOST PORT` | Destination port, routing, and firewall |
| Unexpected network interruptions | `journalctl -k --since "1 hour ago"` | Link, driver, and device events |
| Suspected firewall blockage | `nft list ruleset` | Rules affecting the relevant traffic |

## 14. Important Notes

- Use read-only diagnostic commands before changing network configuration.
- A successful interface state does not guarantee end-to-end connectivity.
- DNS, routing, firewall, and application problems can produce similar symptoms.
- ICMP tests may fail even when other protocols work.
- Network-management tools differ across Linux distributions.
- Always verify that a corrective action resolved the original problem without introducing another failure.