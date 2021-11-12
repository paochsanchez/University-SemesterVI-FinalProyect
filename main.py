#Aquí iría nuestro proyecto
#SI HUBIERA UNO :(
import csv

# DOCID es el identificador del documento
# CLASE es la clase a la que pertenece el documento
# NUM-TERMINOS es el número de términos del documento
# TERMINOS[termino/peso] último campo contiene una lista con los términos y sus correspondientes pesos

#Variables Globales y Constantes
CSV_Data = []
Param_Rocchio = [(0.75, 0.25), (0.85, 0.15), (0.95, 0.05)]
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
        item["TERMINOS[termino/peso]"]  = tuples
        
def main():
    listWordsWithWeight= readCSVFile()
    prepareWords(listWordsWithWeight)
    prepareWeights()
    print(Clases)
    
    
main()