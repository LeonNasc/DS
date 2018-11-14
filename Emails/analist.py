import re
import csv

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
        parseado['pacientes'] = num_pacientes
        parseado['plantao'],parseado['data'] = get_plantao(email)
        #get_equipe retorna farmaceuticos(equipe[0]), auxiliares(equipe[1])
        parseado['farmaceuticos'], auxiliares = get_equipe(email)
        parseado["num_farmas"] = len(parseado["farmaceuticos"].split(","))
        parseado["pacientes/farma"] = parseado['pacientes']/parseado['num_farmas']
        dados.append(parseado)
  escrever_csv(dados)

def get_equipe(email):
  #TODO: Auxiliares
  farmaceuticos = get_farmas(email)
  auxiliares = get_auxiliares(email)
  return farmaceuticos, auxiliares

def get_auxiliares(email):

  return []

def get_farmas(email):
  regex = r'farm\w*os:([\s\w,\(\)?\/\-.:;?]+)(?=aux)'
  regex = re.compile(regex, re.I)
  results = re.search(regex,email)
  if results is not None:
    #Para alguns casos em que o regex não funciona
    result = results.group(1).split("Auxiliares")[0].strip()
    return result.replace(" e ", ",")
  else:
    print(email)
    return ''

def get_plantao(email):
  regex = r'Plantão +(Azul|Verde|Branco|Vermelho|Brasil|Vermerlho) *-? (\d{2}\/\d{2}\/\d{2,4})'
  regex = re.compile(regex,re.I)
  results = re.search(regex, email)
  if results is not None:
    return results.group(1), results.group(2)
  else:
    return None, None

def get_pacientes(email):
  regex = r'pacientes internados ?(\(.*\))? ?: *?(\d+)'
  regexer = re.compile(regex, re.I)
  results = re.search(regexer, email)
  if results is not None:
    return int(results.group(2))
  else:
    return -1

def escrever_csv(dados):
  with open('plantões.csv','w') as csvfile:
    chaves = dados[0].keys()
    writer = csv.DictWriter(csvfile, chaves)
    writer.writerows(dados)


def main():
  emails = abrir_arquivo()
  parse_emails(emails)

main()
