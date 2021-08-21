

ansible-playbook -i /home/magisterka/etl-nosql/ansible-gen-data/hosts \
 -u magisterka \
 --extra-vars "ansible_become_password=$1, ansible_ssh_pass=$2" \
 /home/magisterka/etl-nosql/ansible-gen-data/hosts/genTables.yaml
