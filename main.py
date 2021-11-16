import csv
import math
import json
import ast

# DOCID es el identificador del documento
# CLASE es la clase a la que pertenece el documento
# NUM-TERMINOS es el número de términos del documento
# TERMINOS[termino/peso] último campo contiene una lista con los términos y sus correspondientes pesos

# ------- Variables Globales y Constantes ------- 

CSV_Data = []
CSV_Data_2 = []
Param_Rocchio = [[0.75, 0.25], [0.85, 0.15], [0.95, 0.05]]
Clases ={}
Clases_2 ={}

# ------- Base -------      
        
        
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

# ------- Rocchio -------      
                    
            
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

def rocchioAlgorithm(W_L, param):
    allqCp = {}
    for clase in Clases:
        CP = calculateRocchioCP(clase, W_L)
        notCP = calculateRocchioNotCP(clase, W_L)
        allqCp[clase] = calculateRocchioQCP(CP,notCP,param)
    return allqCp

def rocchioAlgorithm2(allqCp,CSV_Data_2):   
    print("Rocchio Algorithm")
    docs = {}   
    for doc in CSV_Data_2:  
        valDoc={}
        valDoc["CLASE ORIGINAL"] = doc["CLASE"]
        valDoc["CLASE OTORGADA"] = 0
        valDoc["SIMILITUDES"] = {}
        id = doc["DOCID"]
        for cp in allqCp:
            sumMult = 0
            for value in allqCp[cp]:
                sumMult += float(doc["TERMINOS[termino/peso]"].get(value, 0)) *float(allqCp[cp][value])
            valDoc["SIMILITUDES"][cp] = sumMult
        sorted_tuples = sorted(valDoc["SIMILITUDES"].items(), key=lambda item: item[1])
        sorted_tuples.reverse()
        sorted_dict = {k: v for k, v in sorted_tuples}
        valDoc["SIMILITUDES"] = sorted_dict
        valDoc["CLASE OTORGADA"] = max(valDoc["SIMILITUDES"], key=lambda key: valDoc["SIMILITUDES"][key])
        docs[id] = valDoc
        print(id+"\t"+doc["CLASE"]+"\t"+valDoc["CLASE OTORGADA"])    
    res = json.dumps(docs,sort_keys=False, indent=4)
    new_file= open("Rocchio.txt",mode="w")
    new_file.write(res)
    new_file.close()
    print(" ")
    return docs



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

def bayesianosIngenuosAlgorithm(Words_List):
    frequencyPerClass = getFrequenciesPerClass(Words_List)
    nis = calculateNis(Words_List, frequencyPerClass)
    PIPPerClass = getPIPPerClass(Words_List, frequencyPerClass)
    QIPPerClass = getQIPPerClass(Words_List, frequencyPerClass, nis)
    return [PIPPerClass,QIPPerClass]

def bayesianosIngenuosAlgorithm2(PIPPerClass, QIPPerClass, Words_List_2, CSV_Data_2, Clases_2):
    print("Bayesianos Ingenuos Algorithm")
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
        
        print(doc['DOCID']+"\t"+doc["CLASE"]+"\t"+docs[int(doc['DOCID'])]['CLASE OTORGADA'])

    dictionary_items = docs.items()
    docs = dict(sorted(dictionary_items))
    res = json.dumps(docs,sort_keys=False, indent=4)
    new_file= open("BayesianosIngenuos.txt",mode="w")
    new_file.write(res)
    new_file.close()
    print(" ")
    return docs


# ------- evaluation -------

def doEvaluation(clasificatorRes, Clases_2):
    g_N = 0 
    for clase in Clases_2: g_N += Clases_2[clase]

    for clase in Clases_2:
        c_numDocsInClassBySet = Clases_2[clase]
        a_numDocsInClassWellAssigned = 0
        f_numDocsInClassAssigned = 0
        for doc in clasificatorRes:
            if clase == clasificatorRes[doc]["CLASE OTORGADA"]:
                if clasificatorRes[doc]["CLASE OTORGADA"] == clasificatorRes[doc]["CLASE ORIGINAL"]:
                    a_numDocsInClassWellAssigned+=1
                f_numDocsInClassAssigned+=1
    
        b_numDocsInClassBadAssigned = c_numDocsInClassBySet-a_numDocsInClassWellAssigned
        d_numDocsNotInClassButAssigned = f_numDocsInClassAssigned-a_numDocsInClassWellAssigned
        numCassesBadAssigned = g_N-f_numDocsInClassAssigned
        e_numDocsNotInClassAndNotAssigned = numCassesBadAssigned-b_numDocsInClassBadAssigned
        numDocsNotAssignedToClass = d_numDocsNotInClassButAssigned+e_numDocsNotInClassAndNotAssigned
        
        precision=(a_numDocsInClassWellAssigned/f_numDocsInClassAssigned)
        recall=(a_numDocsInClassWellAssigned/c_numDocsInClassBySet)
        sucess=((a_numDocsInClassWellAssigned+e_numDocsNotInClassAndNotAssigned)/g_N)
        error=((b_numDocsInClassBadAssigned+d_numDocsNotInClassButAssigned)/g_N)

        print("Clase: " + clase)
        print("Precision: " + str(precision))
        print("Recall: " + str(recall))
        print("Sucess: " + str(sucess))
        print("Error: " + str(error))
        print("------------------")
        


# ------- main -------      
def main():
    print("Proyecto Final - RIT")
    print("--------------------")
    print("1. Ingresar datos de entrenamiento")
    print("2. Ingresar datos de prueba")
    print("3. Salir")
    print("Seleccione una opcion: ")
    choice = input()
    
    if(choice=="1"):
        
        print("Ingrese la dirección de los datos: ")
        path = input()
        
        print("El algoritmo Rocchio posee tres pares de párametos:")
        print("1. (Beta = 0.75, Gama=0.25)")
        print("2. (Beta = 0.85, Gama=0.15)")
        print("3. (Beta = 0.95, Gama=0.05)")
        print("Seleccione un parámetro: ")
        choiceParam = input()
        if(choice!="1" and choice!="2" and choice!="3"): 
            print("El valor ingresado no es válido")
            print("Se pondrá por defecto el valor 1")
            choice==1
        listWWW = readCSVFile(path,CSV_Data,Clases)
        Words_List = prepareWords(listWWW)
        prepareWeights(Words_List,CSV_Data)
        
        res = rocchioAlgorithm(Words_List,int(choiceParam)-1)
        new_file= open("Training-Rocchio.txt",mode="w")
        new_file.write(str(res))
        new_file.close()
        
        res = bayesianosIngenuosAlgorithm(Words_List)
        new_file= open("Training-BI.txt",mode="w")
        new_file.write(str(res))
        new_file.close()
        print("")
    elif(choice=="2"):
        
        print("Ingrese la dirección de los datos: ")
        path = input()
        
        CSV_Data_2 = []
        Clases_2 = {}
        
        listWWW_2 = readCSVFile(path,CSV_Data_2,Clases_2)
        Words_List_2 = prepareWords(listWWW_2)
        prepareWeights(Words_List_2,CSV_Data_2)

        new_file= open("Training-Rocchio.txt",mode="r")
        text = new_file.read()
        res = ast.literal_eval(text)

        resRocchio = rocchioAlgorithm2(res,CSV_Data_2)
        print("------ Rocchio Evaluation ------")
        doEvaluation(resRocchio, Clases_2)
        print(" ")
        
        new_file= open("Training-BI.txt",mode="r")
        text = new_file.read()
        res = ast.literal_eval(text)
        
        resBayesianos = bayesianosIngenuosAlgorithm2(res[0],res[1],Words_List_2, CSV_Data_2, Clases_2)
        print("------ Byesianos Ingenuos Evaluation ------")
        doEvaluation(resBayesianos, Clases_2)
        print(" ")

    elif(choice=="3"):
        return   
    else:
        print("Error. Intente nuevamente.")
        return main()
    return main()


main()