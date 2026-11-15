*** Settings ***
Library    ../../BibliotecaLib.py

*** Test Cases ***
Cadastrar novo leitor
    #Arrange
    ${comando}=    Set Variable    INSERT leitor
    #Act
    ${linhas}=    Consultar Banco    ${comando}
    #Assert
    Should Be Equal As Integers    ${linhas}    1

Atualizar e-mail do leitor
    #Arrange
    ${comando}=    Set Variable    UPDATE leitor
    #Act
    ${linhas}=    Consultar Banco    ${comando}
    #Assert
    Should Be Equal As Integers    ${linhas}    1

Exportar carteirinha em PDF
    Skip    Exportação em PDF ainda não implementada
