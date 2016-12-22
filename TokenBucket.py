import time

class TokenBucket:
    """limits requests"""
    def __init__(self,tokens,coolDown):
        self.numTokens = float(tokens)              # max number of tokens
        self.tokens = float(tokens)                 # number of tokens available
        self.coolDown = float(coolDown)
        self.timeStamp = time.time()

    def removeTokens(self,tokens):                  # removes a given amount of tokens
        if (tokens <= self.tokens):
            self.tokens = self.tokens - tokens
            return True
        else:
            return False

    def refreshTokens(self):                            # refreshes tokens if an hour has passed
        currentTime = time.time()
        if(currentTime - self.timeStamp > self.coolDown):
            self.tokens = self.numTokens
            self.timeStamp = time.time()
            return True
        else:
            timeleft = (time.time() - self.timeStamp)
            print(timeleft)
            return False

    def areTokensLeft(self,numTokens):
        if (numTokens>self.tokens):
            return False
        return True