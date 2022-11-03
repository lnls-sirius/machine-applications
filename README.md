# UvvUndulator-ioc

This is a project to control the EPU from UVX with EPICS.
Motor drives: Indramat DKCXX.3-040-7-FW EcoDrive

## Requirements

run conda install -c paulscherrerinstitute pcaspy=0.7.3 to install pcaspy
run pip install requirements.txt to install other required packages.

## Deploy

A comunicação entre ioc e drives é realizada da seguinte forma: No host do ioc, uma porta serial é emulada com socat, que redireciona as mensagens via ethernet. Essa porta serial emulada é utilizada pelo ioc, o redirecionamento via ethernet é transparente para a aplicação.
Na beagle bone, ser2net é utilizado para receber as mensagens via ethernet e redirecionar os drives via porta serial, o oposto também é realizado pelo ser2net.

Na beagle bone:
Instale ser2net: apt install ser2net
Troque o arquivo /etc/ser2net.conf do host pelo ser2net.conf deste repositório

No host do ioc:
Instale socat: apt install socat
execute: socat -d -d pty,raw,echo=0 tcp:10.1.2.156:9993
Isso criará uma porta serial virtual, é necessário saber o nome dessa porta para utilizála.

Melhorias: padronizar nome da serial virtual criada.
Automatizar a mudança do dono da virtual serial criada.

## Notas importantes sobre o desenvolvimento
A função de escrever na serial, não verifica se tem algo no buffer de saída, sempre que utilizada, ela apaga esse buffer e escreve. O inconveniente de verificar se tem algo no buffer de saída é que pode acontecer um problema que faz com que o buffer fique "cheio". Veja bem, é de responsabilidade do cliente das funções do drive, saber quando ou não usar cada função. Se tem uma mensagem/requisição no buffer de saída, então a resposta dela ainda não chegou, se essa resposta não chegou, outra requisição não deve ser feita. O cliente, no caso, é quem escreve o fluxograma de funcionamento da classe Epu, atente-se a isso.

Existe um número mágico na função send do drive. Ele é o tempo mínimo entre uma escrita e uma leitura na porta serial. Testar colocar ele no timeout da serial, se funcionar, pode ser retirado do código, caso contrário, mude para que não seja um número mágico.

Se a serial falhar em qualquer momento, aborte.
serial.read(100) -> se o buffer possuir 10 bytes, ele espera o timeout para saber que leu tudo?
Tratar exceções da seguinte forma: caso ela ocorra, acione uma flag e tente repetir x vezes!
Implementar função para solicitar lista cronológica de diagnósticos.

## Comentários para desenvolvimento:
### Ideias para aumentar taxa de aquisição:

1) Pegar status do halt e do enable da eletrônica da bbb e não do drive
2) Target position: não tem necessidade de ficar atualizando, ou atualizar a uma taxa bem menor (~ 5 s)
3) Target position reached: Tem necessidade de ficar atualizando? Se sim, talvez com período de 5 ~ ou maior.
A IDEIA É CRIAR UMA LÓGICA ROBUSTA QUE GARANTA O VALOR DE CERTAS VARIÁVEIS COM BASE EM OUTRAS, REDUZINDO A QUANTIDADE DE VARIÁVEIS ATUALIZADAS VIA SERIAL.
4) Velocidade atual: DESNECESSÁRIA
5) Drive is moving? Manter atualização periódica sob certas condições: drive halt e drive enable ativados.


# Documentação
Se o freio está livre, então todas as outras condições para se iniciar o movimento foram satisfeitas, por isso a variável que define se pode ou não ter movimentação é atualizada com base nas leituras via bsmp, da beagle bone, apenas. Isso economisa banda do barramento RS485. As variáveis de status do enable e do halt também são baseadas nas leituras das GPIOs da bbb.
Com qualquer sinal digital de saída em nível lógico alto, nada pode ser escrito no drive. Isso é uma premissa importante, já que a lógica de alguns métodos se baseia nela. Por isso é importante uma leitura periodia do status da saída digital da bbb.
A função check_*movement() é chamada a cada vez que o sinal de start é enviado. Ela monitora o movimento até ele acabar ou até timeout. Ela está sem robustez, carece de melhorias.
