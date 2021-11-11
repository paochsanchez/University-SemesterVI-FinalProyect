#Aquí iría nuestro proyecto
#SI HUBIERA UNO :(
    
import csv

def readCSVFile():
    with open('test-set.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter='\t')
        print(csv_reader.fieldnames) 
        for row in csv_reader:
            print(row)

readCSVFile()