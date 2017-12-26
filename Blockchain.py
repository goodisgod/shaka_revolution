import datetime #library containing timestamp function
import hashlib #hash generator

"""
TO DO LIST:\
**imbed blockchain verification into transfer code (CHECK)
**overdraft
**option of negative balance
**Merkel Tree development
**connect to network
**pull blockchain if it exists from file at program starts
**change password input so it's not visible on console
**implement a mechanism for shaka creation
**develop a GUI
"""

class Block:
    def __init__(self, index, data, previousHash = ''):
        self.timestamp = datetime.datetime.now()  #[2012-12-15 10:14:51.898000]
        self.index = index
        self.data = data
        self.previousHash = previousHash
        self.hash = self.calculateHash()
        self.transfer()

    def calculateHash(self):
        return hashlib.sha256(str(self.index) + self.previousHash + str(self.timestamp) + str(self.data)).hexdigest()

    def transfer(self):
        if isinstance(self.data, dict):
            origin = False
            reciever = False
            amount = False
            for key in self.data.keys():
                if key == "origin":
                    if origin == True:
                        return False
                    else:
                        origin = True 
                elif key == "reciever":
                    if reciever == True:
                        return False
                    else:
                        reciever = True
                elif key == "amount":
                    if amount == True:
                        return False
                    else:
                        amount = True
                else:
                    return False
            if origin != True or reciever != True or amount != True:
                print "Data is missing from set."
                return False
            else:
                if self.data["origin"].accountBalance >= self.data["amount"]:
                    #execute the transfer
                    self.data["origin"].accountBalance -= self.data["amount"]
                    self.data["reciever"].accountBalance += self.data["amount"]
                #ISSUE: overdraft
                else:
                    print "Insufficient funds to complete transfer."
                    return False

        elif self.index == 0:  #case of the genesis block
            return True
        else:
            print "Data cannot be read."
            return False

        return True

class Blockchain:
    def __init__(self):
        self.chain = [self.createGenesisBlock()]    #list that holds blocks

        blockchainFile = open("blockchain.txt", 'w')
        blockchainFile.write("Index \t Timestamp \t Origin \t Reciever \t Amount \t Hash \t Previous Hash")
        blockchainFile.write('\n' + str(self.getLatestBlock().index) + '\t' + str(self.getLatestBlock().timestamp) + '\t' + "0" + '\t' + "0" + '\t' + "0" + '\t' + self.getLatestBlock().hash + '\t' + self.getLatestBlock().previousHash)
        blockchainFile.close()

    def createGenesisBlock(self):
        return Block(0, "Genesis Block", "0")

    def getLatestBlock(self):
        return self.chain[len(self.chain) - 1]

    def addBlock(self, newBlock):
        newBlock.previousHash = self.getLatestBlock().hash
        newBlock.hash = newBlock.calculateHash()
        self.chain.append(newBlock)

        #record new transaction to disk
        #formatted as [index, timestamp, data, hash, previous hash]
        blockchainFile = open("blockchain.txt", "a+")
        blockchainFile.write('\n' + str(newBlock.index) + '\t' + str(newBlock.timestamp) + '\t' + newBlock.data["origin"].username + '\t' + newBlock.data["reciever"].username + '\t' + str(newBlock.data["amount"]) + '\t' + newBlock.hash + '\t' + newBlock.previousHash)
        blockchainFile.close()
        
        #method of reversing last transaction
        if self.isChainValid() == False:
            print "Corrupt Block: reversing latest transaction..."
            currentIndex = self.getLatestBlock().index + 1
            self.addBlock(Block(1, {"origin": self.getLatestBlock().data["origin"], "reciever": self.getLatestBlock().data["reciever"], "amount": -self.getLatestBlock().data["amount"]}))
            #delete the last two blocks in the chain
            del self.chain[-1]
            del self.chain[-2]
            
    def isChainValid(self):
        i= 0
        for link in self.chain:
            if i != 0:
                if link.hash != link.calculateHash():
                    return False
                if link.previousHash != prevLink.hash:
                    return False
            else:
                i = 1
            prevLink = link
        return True

    #method of printing blockchain for troubleshooting
    def stringify(self):
        for link in self.chain:
            print "Block Index: " + str(link.index) + " @ " + str(link.timestamp) + " Data: " + str(link.data) + " #" + link.hash
        return "end"

class user:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.accountBalance = 0    #initialize a user's account balance to zero

    def valueCreation(self, newMoney):
        self.accountBalance += newMoney
        return self.accountBalance

    def info(self):
        return self.username + " has " + str(self.accountBalance) + " shakas at " + str(datetime.datetime.now())

    def login(self):
        print "USERNAME: " + self.username
        N = 0   #number of attempts 
        while N < 3:
            if raw_input("PASSWORD: ") == self.password:
                return True
            N += 1
        return False

def login():
    try:
        u = input("USERNAME: ")
    except:
        return False
    if isinstance(u, user):
        N = 0
        while N < 3:
            if raw_input("PASSWORD: ") == u.password:
                return (True, "Accessing " + u.username + "'s account...", u)
            N += 1
        return False
    return False
    
    
       
    
        
ShakaGold = Blockchain()    #create a new blockchain

Adam = user("Adam", "password")
Eve = user("Eve", "bravenewworld")

#How do we create value? How do we monetize the sharing economy and assign a value to human assets?
Adam.valueCreation(10)

ShakaGold.addBlock(Block(1, {"origin": Adam, "reciever": Eve, "amount": 7}))
ShakaGold.addBlock(Block(2, {"origin": Eve, "reciever": Adam, "amount": 4}))

#ATM
currentUser = login()
while isinstance(currentUser, tuple):
    print ''
    query = raw_input("Access [info], make a [transfer], see [history], or change [password]: ")

    #display account information
    if query == "info":
        print currentUser[2].info()

    #transfer money
    elif query == "transfer":
        try:
            recipient = input("Specify recipient: ")
        except:
            print "No user with this name exists."
            continue
        
        amount = input("Amount to Transfer; $")
        currentIndex = ShakaGold.getLatestBlock().index + 1
        ShakaGold.addBlock(Block(currentIndex, {"origin": currentUser[2], "reciever": recipient, "amount": amount}))
        if ShakaGold.isChainValid() == True:
            print "$%s has been transferred to %s's account successfully." % (amount, recipient.username)
        else:
            print "Blockchain is corrupt!"
            #ADDRESS corrupt blockchain
    
    #change account password
    elif query == "password":
        if raw_input("Enter old password: ") == currentUser[2].password:
            newPassword = raw_input("Enter new password: ")
            if raw_input("Retype password: ") != newPassword:
                print "Password does not match."
            else:
                currentUser[2].password = newPassword
                print "Password changed!"
        else:
            print "Password is incorrect."
    #look up history for troubleshooting
    elif query == "history":
        blockchainFile = open("blockchain.txt", 'r')
        history = blockchainFile.read()
        print history
        blockchainFile.close()
    else:
        print "Response does not match any option."
    print ''
    currentUser = login()
                
        
        
    

    
    


