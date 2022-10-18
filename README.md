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
se uma excessão é levantada por uma função (f1), dentro de outra função (f2), quando uma função f3 chama a f1 e a f2 levanta a excessão, essa excessão pode ser tratada por f3?
Tratar exceções da seguinte forma: caso ela ocorra, acione uma flag e tente repetir x vezes!