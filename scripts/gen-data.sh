#!/bin/bash

ansible-playbook -i /home/magisterka/etl-nosql/ansible-gen-data/hosts \
 -u <user> \
 --extra-vars "ansible_become_password=<password>, ansible_ssh_pass=<password>" \
 /home/magisterka/etl-nosql/ansible-gen-data/data_gen.yaml
