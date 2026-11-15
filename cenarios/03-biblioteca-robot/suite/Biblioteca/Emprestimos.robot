*** Settings ***
Library    ../BibliotecaLib.py

*** Test Cases ***
Emprestar livro disponível
    #Arrange
    ${leitor}=    Set Variable    L-001
    ${livro}=    Set Variable    Dom Casmurro
    #Act
    ${status}=    Emprestar    ${leitor}    ${livro}
    #Assert
    Should Be Equal    ${status}    emprestado

Prazo de devolução padrão é 14 dias
    #Arrange
    ${prazo_esperado}=    Set Variable    14
    #Act
    ${prazo}=    Prazo De Devolucao
    #Assert
    Should Be Equal As Integers    ${prazo}    ${prazo_esperado}
    ...    msg=Prazo de devolução deveria ser 14 dias, mas foi ${prazo}    values=False

Leitor com multa não pode emprestar
    #Arrange
    ${leitor_com_multa}=    Set Variable    L-002
    #Act
    ${status}=    Emprestar    ${leitor_com_multa}    Vidas Secas
    #Assert
    Should Be Equal    ${status}    bloqueado
    ...    msg=Empréstimo deveria ser bloqueado para leitor com multa pendente    values=False

Buscar livro pelo título
    #Arrange
    ${titulo}=    Set Variable    Vidas Secas
    #Act
    ${achou}=    Buscar Livro    ${titulo}
    #Assert
    Should Be True    ${achou}
