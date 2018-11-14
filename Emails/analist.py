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
        parseado['farmaceuticos'], parseado['auxiliares'] = get_equipe(email)

        # O -1 é devido ao farmacêutico lider
        parseado["num_farmas"] = len(parseado["farmaceuticos"].split(",")) 
        parseado['num_aux'] = len(parseado['auxiliares'].split(","))
        #Algumas razões entre pacientes/funcionários
        parseado["pacientes/farma"] = parseado['pacientes']/parseado['num_farmas']
        parseado["pacientes/aux"] = parseado['pacientes']/parseado['num_aux']

        parseado['qt'] = get_quimio(email)
        parseado['dialise'] = get_dialise(email)
        parseado['compras'] = get_compras(email)

        #Depois de limpar e incluir todos os dados
        dados.append(parseado)

  escrever_csv(dados)

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
    return 0



def escrever_csv(dados):
  with open('plantões.csv','w') as csvfile:
    chaves = dados[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames = chaves)
    writer.writeheader()
    writer.writerows(dados)


def main():
  emails = abrir_arquivo()
  parse_emails(emails)

main()
