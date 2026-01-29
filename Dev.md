Short answer: Docker Compose can’t create real VMs, but you can create a cluster of containerized “VM-like” nodes that each run an SSH server and have stable, assigned IP addresses on a custom Docker network. From your local machine, you SSH directly to those IPs.

Below is the clean, correct way to do it, plus the limits you should be aware of.

⸻

Architecture overview (important mental model)
	•	Docker containers ≠ VMs
	•	Each “node” is a Linux container running:
	•	OpenSSH server
	•	Its own filesystem
	•	A fixed private IP on a Docker bridge network
	•	Your host machine can route to that network
	•	SSH works exactly like a VM cluster

This is perfect for:
	•	Distributed systems testing
	•	Cluster orchestration experiments
	•	Networking simulations
	•	CI / dev environments

Not good for:
	•	Kernel testing
	•	Systemd-heavy OS behavior
	•	Nested virtualization

⸻

Step 1: Project structure

cluster/
├── docker-compose.yml
├── Dockerfile
└── authorized_keys


⸻

Step 2: SSH-enabled node image

Dockerfile

FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y openssh-server iproute2 && \
    mkdir /var/run/sshd

RUN useradd -m cluster && \
    mkdir /home/cluster/.ssh && \
    chmod 700 /home/cluster/.ssh

COPY authorized_keys /home/cluster/.ssh/authorized_keys
RUN chmod 600 /home/cluster/.ssh/authorized_keys && \
    chown -R cluster:cluster /home/cluster/.ssh

RUN echo "cluster ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]


⸻

Step 3: SSH keys

On your host machine:

ssh-keygen -t ed25519 -f cluster_key

Then copy the public key:

cp cluster_key.pub authorized_keys


⸻

Step 4: Docker Compose with static IPs

docker-compose.yml

version: "3.9"

networks:
  cluster_net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.30.0.0/24

services:
  node1:
    build: .
    container_name: node1
    networks:
      cluster_net:
        ipv4_address: 172.30.0.11

  node2:
    build: .
    container_name: node2
    networks:
      cluster_net:
        ipv4_address: 172.30.0.12

  node3:
    build: .
    container_name: node3
    networks:
      cluster_net:
        ipv4_address: 172.30.0.13


⸻

Step 5: Start the cluster

docker compose up -d --build

Verify:

docker ps
docker network inspect cluster_cluster_net


⸻

Step 6: SSH from your local machine

ssh -i cluster_key cluster@172.30.0.11
ssh -i cluster_key cluster@172.30.0.12
ssh -i cluster_key cluster@172.30.0.13

Each container behaves like its own node.

⸻

Step 7: Inter-node SSH (optional)

If you want nodes to SSH into each other:

docker exec -it node1 bash
ssh cluster@172.30.0.12

Works immediately since they’re on the same subnet.

⸻

Common pitfalls (read this)

❌ “Why can’t I ping from host?”

Docker bridge networks are private. SSH works, ICMP may not depending on host OS.

❌ “I want public IPs”

Docker Compose does not assign public IPs. For that you need:
	•	macvlan networking or
	•	real VMs (KVM, Proxmox, cloud)

❌ “This doesn’t feel like a real VM”

Correct. If you need:
	•	systemd
	•	kernel modules
	•	full init systems

Use Vagrant + libvirt, Proxmox, or Multipass instead.

⸻

When this setup is exactly the right choice
	•	Distributed algorithms
	•	Raft / gossip / leader election
	•	Kubernetes internals testing
	•	Network partitions
	•	CI cluster simulations
	•	Teaching systems concepts

⸻

If you want, I can also:
	•	Convert this to macvlan so containers appear as LAN machines
	•	Show a Vagrant / libvirt version with real VMs
	•	Add Ansible provisioning
	•	Turn this into a Kubernetes-in-Docker lab

Just tell me what direction you’re heading.
