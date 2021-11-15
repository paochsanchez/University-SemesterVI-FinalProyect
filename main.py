#Aquí iría nuestro proyecto
#SI HUBIERA UNO :(
import csv
import math
import json
from collections import OrderedDict

# DOCID es el identificador del documento
# CLASE es la clase a la que pertenece el documento
# NUM-TERMINOS es el número de términos del documento
# TERMINOS[termino/peso] último campo contiene una lista con los términos y sus correspondientes pesos

#Variables Globales y Constantes
paths =['training-set.csv','test-set.csv']
CSV_Data = []
CSV_Data_2 = []
Param_Rocchio = [[0.75, 0.25], [0.85, 0.15], [0.95, 0.05]]
Clases ={}
Clases_2 ={}

def readCSVFile(path,CSV_Data_,Clases_):
    Words_List_WW =[]
    with open(path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter='\t')
        for row in csv_reader:
            CSV_Data_.append(row)
            Words_List_WW.append(row.get("TERMINOS[termino/peso]").split(" "))
            if row.get("CLASE") not in Clases_.keys():
                Clases_[row.get("CLASE")] = 1
            else:
                Clases_[row.get("CLASE")] = Clases_[row.get("CLASE")]+1
    CSV_Data_.sort(key=lambda k: k['CLASE'])
    return Words_List_WW

def prepareWords(Words_List_WW):
    wordList =[]
    for list in Words_List_WW:
        for item in list:
            tuple = item.split("/")
            if tuple[0] not in wordList:
                wordList.append(tuple[0])
    wordList.sort()
    return wordList

def prepareWeights(Words_List,CSV_Data_):
    for item in CSV_Data_:
        termsList = item.get("TERMINOS[termino/peso]").split(" ")
        tuples = {}
        for term in termsList:            
            wordData = term.split("/")
            tuples[wordData[0]] = wordData[1]
        for term in Words_List:
            if term not in tuples.keys():
                tuples[term] = 0
        item["TERMINOS[termino/peso]"] = tuples

            
            
def calculateRocchioCP(clase, Words_List):
    actualDocs = [item for item in CSV_Data if item["CLASE"] == clase]
    cont = 0
    averageCP = {} 
    for doc in actualDocs:
        cont += 1
        for word in Words_List:
            if word not in averageCP.keys():
                averageCP[word]= float(doc["TERMINOS[termino/peso]"].get(word, 0))
            else:
                averageCP[word] = averageCP[word]+float(doc["TERMINOS[termino/peso]"].get(word, 0))
            if cont == Clases[clase]:
                averageCP[word] = averageCP[word]/int(Clases[clase]) if averageCP[word]!=0 else 0
    return averageCP             
        
def calculateRocchioNotCP(clase, Words_List):
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
        qCP[value] = qCP[value] - ( Param_Rocchio[param][1]*float(notCP[value]))
    return qCP

def rocchioAlgorithm(W_L):
    allqCp = {}
    for clase in Clases:
        CP = calculateRocchioCP(clase, W_L)
        notCP = calculateRocchioNotCP(clase, W_L)
        allqCp[clase] = calculateRocchioQCP(CP,notCP,0)
        
    for doc in CSV_Data_2:  
        print("********************")  
        print(doc["DOCID"])  
        valDoc={}
        for cp in allqCp:
            sumMult = 0
            for value in allqCp[cp]:
                sumMult += float(doc["TERMINOS[termino/peso]"].get(value, 0)) *float(allqCp[cp][value])
            valDoc[cp] = sumMult
        print(valDoc[max(valDoc, key=valDoc.get)])
        

# ------- Bayesianos Ingenuos -------

def createDictionaryPerClass(Words_List):
    frequencyPerClass = {}
    for clase in Clases:
        frequencyPerClass[clase] = {}
        for word in Words_List:
            frequencyPerClass[clase][word] = 0
    return frequencyPerClass

def getFrequenciesPerClass(Words_List):
    frequencyPerClass = createDictionaryPerClass(Words_List)

    for clase in Clases:
        for doc in CSV_Data:
            if doc['CLASE'] == clase:
                for terms in doc['TERMINOS[termino/peso]']:
                    if (doc['TERMINOS[termino/peso]'][terms]!=0):
                        #print(doc['TERMINOS[termino/peso]'][terms])
                        frequencyPerClass[clase][terms] += 1

    #print(frequencyPerClass)
    return frequencyPerClass


def calculateNis(Words_List, frequencyPerClass):
    #Sumar apariciones de cada palabra en frequencyPerClass
    nis = {}
    for word in Words_List:
        nis[word] = 0
    
    for clase in Clases:
        for word in Words_List:
            nis[word] += frequencyPerClass[clase][word]

    #print(nis)
    return nis

def getPIPPerClass(Words_List, frequencyPerClass):
    PIPPerClass = createDictionaryPerClass(Words_List)

    for clase in Clases:
        for word in Words_List:
            PIPPerClass[clase][word] = (1+frequencyPerClass[clase][word])/(2+Clases[clase])

    return PIPPerClass

def getQIPPerClass(Words_List, frequencyPerClass, nis):
    QIPPerClass = createDictionaryPerClass(Words_List)
    N = 0 
    for clase in Clases: N += Clases[clase]

    for clase in Clases:
        for word in Words_List:
            QIPPerClass[clase][word] = (1+nis[word]-frequencyPerClass[clase][word])/(2+N-Clases[clase])

    return QIPPerClass

def bayesianosIngenuosAlgorithm(Words_List, Words_List_2):
    frequencyPerClass = getFrequenciesPerClass(Words_List)
    nis = calculateNis(Words_List, frequencyPerClass)
    PIPPerClass = getPIPPerClass(Words_List, frequencyPerClass)
    QIPPerClass = getQIPPerClass(Words_List, frequencyPerClass, nis)

    docs = {}

    for doc in CSV_Data_2:
        docs[int(doc['DOCID'])] = {'CLASE ORIGINAL': doc['CLASE'], 'CLASE OTORGADA': '', 'SIMILITUDES': {}}

        similarityDict = {}

        for clase in Clases_2:
            similarityVal = 0
            for word in Words_List_2:
                if((clase in PIPPerClass.keys()) and (clase in QIPPerClass.keys())):
                    if((word in PIPPerClass[clase].keys()) and (word in QIPPerClass[clase].keys())):
                        similarityVal += float(doc['TERMINOS[termino/peso]'][word])*(math.log((PIPPerClass[clase][word]/(1-PIPPerClass[clase][word])),2) + math.log(((1-QIPPerClass[clase][word])/QIPPerClass[clase][word]),2))
            similarityDict[clase] = similarityVal
        sorted_tuples = sorted(similarityDict.items(), key=lambda item: item[1])
        sorted_tuples.reverse()
        sorted_dict = {k: v for k, v in sorted_tuples}
        docs[int(doc['DOCID'])]['SIMILITUDES'] = sorted_dict
        docs[int(doc['DOCID'])]['CLASE OTORGADA'] = max(sorted_dict, key=sorted_dict.get)
    dictionary_items = docs.items()
    docs = dict(sorted(dictionary_items))
    print(json.dumps(docs,sort_keys=False, indent=4))

        
def main():
    
    listWWW = readCSVFile(paths[0],CSV_Data,Clases)
    listWWW_2 = readCSVFile(paths[1],CSV_Data_2,Clases_2)

    Words_List = prepareWords(listWWW)
    Words_List_2 = prepareWords(listWWW_2)
    
    prepareWeights(Words_List,CSV_Data)
    prepareWeights(Words_List_2,CSV_Data_2)
    
    #rocchioAlgorithm(Words_List)
    bayesianosIngenuosAlgorithm(Words_List, Words_List_2)

main()