*** Settings ***
Library    ../../BibliotecaLib.py
#espera um pouco pro horário da queda do banco mudar
Suite Setup    Sleep    1.2s

*** Test Cases ***
Calcular multa por atraso
    #Arrange
    ${comando}=    Set Variable    SELECT multa
    #Act
    ${linhas}=    Consultar Banco    ${comando}
    #Assert
    Should Be Equal As Integers    ${linhas}    1

Quitar multa pendente
    #Arrange
    ${comando}=    Set Variable    UPDATE multa
    #Act
    ${linhas}=    Consultar Banco    ${comando}
    #Assert
    Should Be Equal As Integers    ${linhas}    1
