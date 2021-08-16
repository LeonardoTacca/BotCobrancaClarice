
import numpy as np
from selenium import webdriver
import time as tempo
from selenium.webdriver.common.keys import Keys
import pyodbc
import pandas as pd
import urllib
import PySimpleGUI as sg

from datetime import date

def formatcnpj(dado):
    return "%s.%s.%s/%s-%s" % (dado[0:2], dado[2:5], dado[5:8], dado[8:12], dado[12:])


def formatcpf(cpf):
    return "%s.%s.%s-%s" % (cpf[:3], cpf[3:6], cpf[6:9], cpf[9:])


def formatdata(data):
    return "%s/%s/%s" % (data[0:2], data[2:4], data[4:])
layout = [[sg.Text('Digite a data inicial')],
          [sg.Input(key='datainicial')],
          [sg.Text('Digite a data final')],
          [sg.Input(key='datafinal')],
          [sg.Button('Iniciar o Bot')],
          [sg.Output()],
          ]

janela = sg.Window('WhatsBot', layout)
datainicial = ''
datafinal = ''
while True:
    eventos, valores = janela.read()
    if(eventos == sg.WINDOW_CLOSED):
        break
    if(eventos == 'Iniciar o Bot'):
        if(len(valores['datainicial']) >= 8 & len(valores['datafinal']) >= 8):
            datainicial = valores['datainicial']
            datafinal = valores['datafinal']
            break
        else:
            sg.popup('A data esta com o formato errado!!')
        
datainicial = formatdata(datainicial)
datafinal = formatdata(datafinal)
print(datainicial)
conn = pyodbc.connect(
    'DRIVER={SQL SERVER Native Client 11.0};SERVER=ip;DATABASE=base;UID=nome;PWD=nome')

comando = f"""aqui vai o sql"""
df = pd.read_sql(comando, conn)
listaUsersSemFon = []
print(df)
navegador = webdriver.Chrome("C:/driver/chromedriver.exe")
navegador.get("https://web.whatsapp.com/")
while len(navegador.find_elements_by_id("side")) < 1:
    tempo.sleep(1)
df['FONCL2'] = df['FONCL2'].str.replace(r'[^0-9]', '', regex=True)
df['FONCLI'] = df['FONCLI'].str.replace(r'[^0-9]', '', regex=True)
df['FONCL2'] = '55' + df['FONCL2'].astype(str)
df['FONCLI'] = '55' + df['FONCLI'].astype(str)

for i, foncl2 in enumerate(df['FONCL2']):
    if len(df['FONCL2'][i]) < 13:
        df['FONCL2'][i] = df['FONCL2'][i][:4] + '9' + df['FONCL2'][i][4:]
        print(df['FONCL2'][i])
for i, foncli in enumerate(df['FONCLI']):
    if int(df['FONCLI'][i][4]) != 3:
        print(df['FONCLI'][i][4])
        if len(df['FONCLI'][i]) < 13:
            df['FONCLI'][i] = df['FONCLI'][i][:4] + '9' + df['FONCLI'][i][4:]
            print('Isso é um celular' + df['FONCLI'][i])
df.fillna(0, inplace=True)
for i, nomcli in enumerate(df['NOMCLI']):
    telefone = np.int64(df.loc[i, "FONCL2"])
    cnpj = df.loc[i, "CGCCPF"]
    dataVencimento = df.loc[i, "VCTPRO"]
    valorDivida = df.loc[i, "VLRABE"]
    numeroTitulo = df.loc[i, "NUMTIT"]
    if int(telefone) < 2:
        print('Tentando pegar o numero 2')
        telefone = np.int64(df.loc[i, "FONCLI"])
        print(type(telefone))
    if int(telefone) > 4:
        print(telefone)
        if len(str(cnpj)) == 11:
            cnpjoucpf = formatcpf(str(cnpj))
            data_em_texto = dataVencimento.strftime('%d/%m/%Y')
        else:
            cnpjoucpf = formatcnpj(str(cnpj))
            data_em_texto = dataVencimento.strftime('%d/%m/%Y')
        mensagem = urllib.parse.quote(f"""
        Prezado cliente {nomcli}  portador do CPF/CNPJ Nº{cnpjoucpf}. Estamos realizando uma conciliação e 
        identificação dos recebimentos dos nossos clientes, constam titulos vencidos em seu nome. Titulo Nº 
{numeroTitulo}, com vencimento na data {data_em_texto}, que possui valor de R$ {valorDivida}. Solicito que 
nos informe se este titulo ja foi pago, e nos envie o comprovante ou a previsão de pagamento do mesmo. Caso o mesmo 
ja tenha sido liquidado, desconsidere esta mensagem. Ressaltamos que os titulos vencidos são enviados ao SERASA apos 
o quinto dia de vencimento ou caso se não recebermos um posicionamento da sua parte! 

Att. Clarice Eletrodomesticos LTDA""")
        url = f"https://web.whatsapp.com/send?phone={telefone}&text={mensagem}"
        navegador.get(url)
        tempo.sleep(20)
       
        if len(navegador.find_elements_by_xpath('//*[@id="app"]/div[1]/span[2]/div[1]/span/div[1]/div/div')) != 0:
            while len(navegador.find_elements_by_id("side")) < 1:
                tempo.sleep(1)
            navegador.find_element_by_xpath(
                '//*[@id="app"]/div[1]/span[2]/div[1]/span/div[1]/div/div/div/div/div[2]/div').send_keys(Keys.ENTER)
            telefone2 = telefone = np.int64(df.loc[i, "FONCLI"]) 
            url = f"https://web.whatsapp.com/send?phone={telefone2}&text={mensagem}"
            navegador.get(url)
            while len(navegador.find_elements_by_id("side")) < 1:
                tempo.sleep(1)
            tempo.sleep(10)
            
            if len(navegador.find_elements_by_xpath('//*[@id="app"]/div[1]/span[2]/div[1]/span/div[1]/div/div')) == 1:
                navegador.find_element_by_xpath(
                    '//*[@id="app"]/div[1]/span[2]/div[1]/span/div[1]/div/div/div/div/div[2]/div').send_keys(Keys.ENTER)
                tempo.sleep(30)
                listaUsersSemFon.append([nomcli, numeroTitulo])
            else:
                while len(navegador.find_elements_by_id("side")) < 1:
                    tempo.sleep(1)
                tempo.sleep(10)
                navegador.find_element_by_xpath(
                    '/html/body/div/div[1]/div[1]/div[4]/div[1]/footer/div[1]/div[2]/div/div[1]/div/div[2]').send_keys(Keys.ENTER)
                tempo.sleep(45)
        else:
            tempo.sleep(10)
            navegador.find_element_by_xpath(
                '/html/body/div/div[1]/div[1]/div[4]/div[1]/footer/div[1]/div[2]/div/div[1]/div/div[2]').send_keys(Keys.ENTER)
            tempo.sleep(45)
    else:
        print('Não foi encontrado o numero do cliente ')
        listaUsersSemFon.append([nomcli, numeroTitulo])
sg.popup('Finalizado a Execução!!!!')
tempo.sleep(10)
janela.close()
data_atual = date.today()
data_em_texto = data_atual.strftime('%d/%m/%Y')
caminho ='C:\logBotWhats.txt'
try:
    arquivo = open(file=caminho, mode='a')
    arquivo.write('Data:'+data_em_texto+'-Esses foram os usuarios que não foi encontrado telefone'+'\n')
    for i in range(len(listaUsersSemFon)):
        for j in range(len(listaUsersSemFon[i])):
            arquivo.write(str(listaUsersSemFon[i][j])+'\n')
    arquivo.close()
except FileNotFoundError:
    arquivo = open(file=caminho, mode='w+')
    arquivo.write('Data:'+data_em_texto+'-Esses foram os usuarios que não foi encontrado telefone'+'\n')
    for i in range(len(listaUsersSemFon)):
        for j in range(len(listaUsersSemFon[i])):
            arquivo.write(str(listaUsersSemFon[i][j])+'\n')
    arquivo.close()