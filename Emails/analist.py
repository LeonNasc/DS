#encoding:utf-8

import re
import csv
import locale 
from functools import reduce 

locale.resetlocale()
print(locale.getdefaultlocale())
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def abrir_arquivo():
  try:
    with open("todos os emails.txt",'r') as emails:
      emails_array = []
      for email in emails:
        emails_array.append(email)
      
      return emails_array
  except IOError:
    print("Não consegui abrir o arquivo")
    return []

def parse_emails(emails):
  '''Para minha alegria, quando eu fiz o scrapper, eu fiz o join usando
     "<br><br>" como cola. Daí, quando eu fui testar o arquivo, cada email
     ocupa uma linha e assim dá pra usar for line in lines como separador.
  '''
  dados = []
  for email in emails:
    #Permite remover algumas linhas em branco
    if len(email) > 1:
      #num_pacientes permite filtrar alguns emails que foram scrappeados errado
      num_pacientes = get_pacientes(email)
      parseado = {}
      if num_pacientes > 0:
        parseado['plantao'],parseado['data'] = get_plantao(email)

        #get_equipe retorna farmaceuticos(equipe[0]), auxiliares(equipe[1])
        parseado['farmaceuticos'], parseado['auxiliares'] = get_equipe(email)

        parseado['pacientes'] = num_pacientes

        # O -1 é devido ao farmacêutico lider
        parseado["num_farmas"] = len(parseado["farmaceuticos"].split(",")) 
        if parseado['num_farmas'] > 1:
          parseado['num_clinicos'] = parseado['num_farmas'] - 1
        else:
          parseado['num_clinicos'] = 1
        
        parseado['num_aux'] = len(parseado['auxiliares'].split(","))
        parseado['dispensados_media_mensal'] = get_media_dispensado(parseado['data'])

        #Algumas razões entre pacientes/funcionários
        parseado["pacientes/farma"] = locale.format_string("%.2f",parseado['pacientes']/parseado['num_farmas'],0)
        parseado["pacientes/clinicos"] = locale.format_string("%.2f",parseado['pacientes']/parseado['num_clinicos'],0)
        parseado["pacientes/aux"] = locale.format_string("%.2f",parseado['pacientes']/parseado['num_aux'],0)

        #Outras razões entre os medicamentos dispensados/funcionários
        parseado['dispensados/prod'] = locale.format_string("%.2f",parseado['dispensados_media_mensal'],0)
        parseado['dispensados/aux'] = locale.format_string("%.2f", linearizar_dispensados_pacientes(parseado['pacientes'])/parseado['num_aux'],0)
        
        parseado['dispensados_media_mensal'] = locale.format_string("%.2f",get_media_dispensado(parseado['data']),0)

        parseado['qt'] = get_quimio(email)
        parseado['dialise'] = get_dialise(email)
        parseado['compras'] = get_compras(email)

        #Depois de limpar e incluir todos os dados
        dados.append(parseado)
  gerar_relatorios(dados)

def gerar_relatorios(dados):
  #o primeiro relatorio e o geral
  escrever_csv("plantoes",dados)
  noturnos = ('BRANCO','VERMELHO','VERMERLHO','BRASIL')
  noite = [x for x in dados if safe_upper(x['plantao']) in noturnos]
  dia = [x for x in dados if safe_upper(x['plantao']) not in noturnos ]

  escrever_csv("plantoes_noite", noite)
  escrever_csv("plantoes_dia", dia)

def safe_upper(palavra):
  try:
    return palavra.upper()
  except:
    return palavra

def exec_regex(regex, data,flags=0):
  if flags == 0:
    regex = re.compile(regex, re.I)
  else:
    if i in flags:
      r_flags = re.I
    if m in flags:
      r_flags = r_flags | re.M
    regex = re.compile(regex, r_flags)

  return re.search(regex, data)

def monta_serie_historica():
  #Dados da serie historica. Vamos considerar que o cada plantão segue a média pra cada dia.
  plantoes_mes = [62,60,62,62,60,62,60,62,58,62,62,60]
  medias_mensais = [207609,149271,149938,107935,98444,118654,108508,95464,138211,144255,149818,145894]
  meses = ["10/18","09/18","08/18","07/18","06/18","05/18","04/18","03/18","02/18","01/18","12/17","11/17"]
  serie_historica = {}

  for i in range(len(meses)):
    serie_historica[meses[i]] = medias_mensais[i]/plantoes_mes[i]
  
  #Esse ajuste só é necessário pois eu contabilizo 8 dias de novembro/18
  serie_historica["11/18"] = serie_historica["10/18"]
  serie_historica["10/17"] = serie_historica["11/17"]

  return serie_historica

def linearizar_dispensados_pacientes(pacientes):
    medias_mensais = [207609,149271,149938,107935,98444,118654,108508,95464,138211,144255,149818,145894]
    meds_por_paciente = reduce(lambda a,b: a+b, medias_mensais)/(67*60*12)
   
    return meds_por_paciente*pacientes

def get_media_dispensado(data):
  serie = monta_serie_historica()
  media = 0
  if data is not None:
    try:
      data_c = exec_regex(r'\d{2}\/(\d{2}\/.+$)',data)
      mes = data_c.group(1)
      mes = re.sub(re.compile(r'20(?=\d)',re.I), '', mes)
      media = serie[mes]
    except KeyError as e:
      #Alguns emails estão como 09/2019 e outros como 02/201
      if '02' in data:
        media = serie['02/18']
      else:
        media = serie['09/18']

  return media

def get_equipe(email):
  farmaceuticos = get_farmas(email)
  auxiliares = get_auxiliares(email)
  return farmaceuticos, auxiliares

def get_auxiliares(email):

  regex = r'auxiliares ?:[\s\w,\(\)?\/\-.:;?]*'
  result = exec_regex(regex,email)

  if result is not None:
    result = result.group(0).split("Auxiliares:")[1]
    result = re.sub(re.compile(r' (hig.*)|(mens.*)|(aux.*)$',re.I), '', result)
    return result.replace(" e ", ",")
  else:
    print(email)
    return ''

def get_farmas(email):
  regex = r'farm\w*os:([\s\w,\(\)?\/\-.:;?]+)(?=aux)'
  results = exec_regex(regex,email)
  if results is not None:
    #Para alguns casos em que o regex não funciona
    result = results.group(1).split("Auxiliares")[0].strip()
    return result.replace(" e ", ",")
  else:
    print(email)
    return ''

def get_plantao(email):
  regex = r'Plantão +(Azul|Verde|Branco|Vermelho|Brasil|Vermerlho) *-? (\d{2}\/\d{2}\/\d{2,4})'
  results = exec_regex(regex,email)
  if results is not None:
    return results.group(1), results.group(2)
  else:
    return None, None

def get_pacientes(email):
  regex = r'pacientes internados ?(\(.*\))? ?: *?(\d+)'
  results = exec_regex(regex,email)
  if results is not None:
    return int(results.group(2))
  else:
    return -1

def get_quimio(email):
  regex = r'(?<=quimioterapia:) ?\d*'
  results = exec_regex(regex,email)
  if results is not None:
    return int(results.group(0))
  else:
    return 0
 
def get_dialise(email):
  regex = r'(?<=e dispensadas:) ?(\d*)'
  results = exec_regex(regex,email)
  if results is not None:
    try:
      return int(results.group(1))
    except:
      return 'indisponível - ver email do %s do dia %s' % get_plantao(email) 
  else:
    return 0

def get_compras(email):
  regex = r'(?<=compras:) ?(\d*)'
  results = exec_regex(regex,email)
  if results is not None:
    try:
      return int(results.group(1))
    except:
      return 'indisponível - ver email do %s do dia %s' % get_plantao(email) 
  else:
    regex = r'(?<=compras :) ?(\d*)'
    results = exec_regex(regex,email)
    return results.group(0)

def escrever_csv(nome,dados):
  with open("%s.csv"%nome,'w') as csvfile:
    chaves = dados[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames = chaves, delimiter=';')
    writer.writeheader()
    writer.writerows(dados)


def main():
  emails = abrir_arquivo()
  parse_emails(emails)

main()
