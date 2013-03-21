'''
Stamps
'''

class Stamp(object):
    
    @staticmethod
    def getDungeon():
        pass
    
    @staticmethod
    def getHouse():
        pass
        

class StampGenerator(object):
    
    @staticmethod
    def generateDungeon():
        pass
        
    def generateHouse():
        pass
    
    def generatePane():
        pass

if __name__ == "__main__":
    '''
    Generate Some Stamps
    '''
    
    for i in range(10):
        StampGenerator.generateDungeon()
        StampGenerator.generateHouse()
        StampGenerator.generatePane()