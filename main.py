#Aquí iría nuestro proyecto
#SI HUBIERA UNO :(
import csv

# DOCID es el identificador del documento
# CLASE es la clase a la que pertenece el documento
# NUM-TERMINOS es el número de términos del documento
# TERMINOS[termino/peso] último campo contiene una lista con los términos y sus correspondientes pesos

#Variables Globales y Constantes
CSV_Data = []
Param_Rocchio = [[0.75, 0.25], [0.85, 0.15], [0.95, 0.05]]
Words_List =[]
Clases ={}

def readCSVFile():
    Words_List_WW =[]
    with open('test-set.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter='\t')
        for row in csv_reader:
            CSV_Data.append(row)
            Words_List_WW.append(row.get("TERMINOS[termino/peso]").split(" "))
            if row.get("CLASE") not in Clases.keys():
                Clases[row.get("CLASE")] = 1
            else:
                Clases[row.get("CLASE")] = Clases[row.get("CLASE")]+1
          
    CSV_Data.sort(key=lambda k: k['CLASE'])
    return Words_List_WW

def prepareWords(Words_List_WW):
    for list in Words_List_WW:
        for item in list:
            tuple = item.split("/")
            if tuple[0] not in Words_List:
                Words_List.append(tuple[0])
    Words_List.sort()

def prepareWeights():
    for item in CSV_Data:
        termsList = item.get("TERMINOS[termino/peso]").split(" ")
        tuples = {}
        for term in termsList:            
            wordData = term.split("/")
            tuples[wordData[0]] = wordData[1]
        for term in Words_List:
            if term not in tuples.keys():
                tuples[term] = 0
        item["TERMINOS[termino/peso]"] = tuples

            
            
def calculateRocchioCP(clase):
    actualDocs = [item for item in CSV_Data if item["CLASE"] == clase]
    cont = 0
    averageCP = {}
    print("**************************")
    for doc in actualDocs:
        cont += 1
        for word in Words_List:
            if word not in averageCP.keys():
                averageCP[word]= float(doc["TERMINOS[termino/peso]"].get(word, 0))
            else:
                averageCP[word] = averageCP[word]+float(doc["TERMINOS[termino/peso]"].get(word, 0))
            if cont == Clases[clase]:
                averageCP[word] = averageCP[word]/int(Clases[clase]) if averageCP[word]!=0 else 0
    for word in averageCP:
        print(word+"\t"+str(averageCP[word]))
    return averageCP             
        
def calculateRocchioNotCP(clase):
    actualDocs = [item for item in CSV_Data if item["CLASE"] != clase]
    total = len(CSV_Data) - Clases[clase]
    cont = 0
    averageCP = {}
    for doc in actualDocs:
        cont += 1
        for word in Words_List:
            if word not in averageCP.keys():
                averageCP[word]= float(doc["TERMINOS[termino/peso]"].get(word, 0))
            else:
                averageCP[word] = averageCP[word]+float(doc["TERMINOS[termino/peso]"].get(word, 0))
            if cont == total:
                averageCP[word] = averageCP[word]/int(total) if averageCP[word]!=0 else 0
    return averageCP            

def calculateRocchioQCP(CP,notCP,param):
    qCP = {}
    for value in CP:
        qCP[value] = Param_Rocchio[param][0]*float(CP[value])
    for value in notCP:
        qCP[value] = qCP[value] - Param_Rocchio[param][1]*float(notCP[value])
    return qCP
 
def escalofonesRocchio(qCP,doc):
    addition = 0
    for val in qCP:
        addition += qCP[val] * float(doc["TERMINOS[termino/peso]"].get(val, 0)) 
        
def rocchioAlgorithm():
    allqCp = {}
    for clase in Clases:
        CP = calculateRocchioCP(clase)
        notCP = calculateRocchioNotCP(clase)
        allqCp[clase] = calculateRocchioQCP(CP,notCP,0)
        
    for doc in CSV_Data:    
        valDoc={}
        for cp in allqCp:
            sumMult = 0
            for value in allqCp[cp]:
                sumMult += float(doc["TERMINOS[termino/peso]"].get(value, 0)) *float(allqCp[cp][value])
            valDoc[cp] = sumMult
        
        
def main():
    listWordsWithWeight= readCSVFile()
    prepareWords(listWordsWithWeight)
    prepareWeights()
    rocchioAlgorithm()
    
    
main()