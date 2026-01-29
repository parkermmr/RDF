Perfect — Ansible-on-Docker is a very common (and very sane) way to practice 👍
Let’s tighten this specifically for Ansible correctness, not just “SSH works”.

Below is a minimal but Ansible-accurate setup: control node + managed nodes, stable IPs, SSH keys, Python present, sudo configured, predictable inventory.

⸻

What Ansible actually needs (non-negotiable)

Managed nodes must have:
	•	SSH
	•	Python (Ansible uses it, even for ping)
	•	Sudo (usually)
	•	Stable addressing

Control node needs:
	•	Ansible installed
	•	SSH key access to all nodes
	•	Inventory that does not rely on Docker DNS magic

We’ll do all of that inside Docker Compose.

⸻

Final topology

ansible-lab/
├── docker-compose.yml
├── Dockerfile.node
├── Dockerfile.control
├── inventory.ini
├── ansible.cfg
├── authorized_keys
└── playbook.yml


⸻

Step 1: SSH key (host)

ssh-keygen -t ed25519 -f ansible_lab_key
cp ansible_lab_key.pub authorized_keys


⸻

Step 2: Managed node image

Dockerfile.node

FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y openssh-server python3 sudo && \
    mkdir /var/run/sshd

RUN useradd -m ansible && \
    mkdir /home/ansible/.ssh && \
    chmod 700 /home/ansible/.ssh

COPY authorized_keys /home/ansible/.ssh/authorized_keys

RUN chmod 600 /home/ansible/.ssh/authorized_keys && \
    chown -R ansible:ansible /home/ansible/.ssh && \
    echo "ansible ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]

This image is:
	•	Python-ready
	•	Passwordless sudo
	•	Ansible-compatible

⸻

Step 3: Control node image

Dockerfile.control

FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y openssh-client python3 python3-pip && \
    pip3 install ansible

RUN useradd -m ansible

COPY ansible.cfg /home/ansible/ansible.cfg
COPY inventory.ini /home/ansible/inventory.ini
COPY playbook.yml /home/ansible/playbook.yml
COPY ansible_lab_key /home/ansible/.ssh/id_ed25519

RUN chmod 600 /home/ansible/.ssh/id_ed25519 && \
    chown -R ansible:ansible /home/ansible

USER ansible
WORKDIR /home/ansible


⸻

Step 4: Docker Compose (static IPs)

docker-compose.yml

version: "3.9"

networks:
  ansible_net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.31.0.0/24

services:
  control:
    build:
      context: .
      dockerfile: Dockerfile.control
    container_name: ansible-control
    networks:
      ansible_net:
        ipv4_address: 172.31.0.10
    tty: true

  node1:
    build:
      context: .
      dockerfile: Dockerfile.node
    container_name: ansible-node1
    networks:
      ansible_net:
        ipv4_address: 172.31.0.11

  node2:
    build:
      context: .
      dockerfile: Dockerfile.node
    container_name: ansible-node2
    networks:
      ansible_net:
        ipv4_address: 172.31.0.12


⸻

Step 5: Ansible configuration

ansible.cfg

[defaults]
inventory = inventory.ini
host_key_checking = False
retry_files_enabled = False
interpreter_python = /usr/bin/python3


⸻

inventory.ini

[nodes]
node1 ansible_host=172.31.0.11
node2 ansible_host=172.31.0.12

[nodes:vars]
ansible_user=ansible
ansible_ssh_private_key_file=~/.ssh/id_ed25519

This is real-world style inventory — no Docker shortcuts.

⸻

Step 6: Example playbook

playbook.yml

- hosts: nodes
  become: true
  tasks:
    - name: Ping nodes
      ansible.builtin.ping

    - name: Install curl
      apt:
        name: curl
        state: present
        update_cache: true


⸻

Step 7: Run the lab

docker compose up -d --build
docker exec -it ansible-control bash

Inside control container:

ansible all -m ping
ansible-playbook playbook.yml


⸻

Why this setup is good Ansible practice
	•	Explicit inventory with IPs
	•	SSH key auth
	•	Python dependency awareness
	•	Privilege escalation
	•	No Docker-specific Ansible plugins
	•	Works exactly like cloud VMs

If you later move to EC2, GCP, bare metal — nothing changes.

⸻

Optional upgrades (worth doing later)
	•	Add a bastion node
	•	Break inventory into groups + vars
	•	Use Ansible Vault
	•	Simulate failures by stopping containers
	•	Add system users, services, cron jobs

⸻

If you want, next I can:
	•	Add systemd support inside containers (hard mode)
	•	Add roles and directory layout
	•	Convert this into an Ansible Molecule workflow
	•	Show how to target these nodes from Ansible on your host, not in Docker

Just tell me how deep you want to go 🧠
