#!/bin/bash

# Carregar variáveis de ambiente

. /etc/profile
. ~/.bash_profile
. ~/.bashrc

# Vai para o diretório de execução do script
cd /home/mohid/Aplica/SC_PR_SP/

# Testes
echo " " >> /home/mohid/Aplica/SC_PR_SP/XMART.log
echo "-------" >> /home/mohid/Aplica/SC_PR_SP/XMART.log
echo $LDFLAGS >> /home/mohid/Aplica/SC_PR_SP/XMART.log

# Executa

/home/mohid/Aplica/SC_PR_SP/XMART.py >> /home/mohid/Aplica/SC_PR_SP/XMART.log 2>&1

# printenv > /tmp/printenv.log
