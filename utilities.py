import inspect

class ERROR:
	
	CMD_SUCCESS              =  0   #Command is success
	CONNECTION_FAIL          = -1	#Bittrex api JSON cannot connect to server
	CMD_UNSUCCESS            = -2	#Bittrex api JSON return "success"=False
	CMD_INVALID              = -3	#Bittrex api not supported. Ex: wrong market name.
	TIME_OUT                 = -4	#A cmd cannot be completed within a specific time.
	PARAMETERS_INVALID       = -5	#Inputs for api are invalid. Ex: "INSUFFICIENT_FUNDS"
	
def err_line_track():
	"""Returns the current line number in our program."""
	return inspect.currentframe().f_back.f_lineno

def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        return 0
    return sum(data)/n # in Python 2 use sum(data)/float(n)

def ssdev(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss
	
def pstdev(data):
    """Calculates the population standard deviation."""
    n = len(data)
    if n < 2:
        return 0
    ss = ssdev(data)
    pvar = ss/n # the population variance
    return pvar**0.5

def stddev(data):
    """Calculates the sample standard deviation."""
    n = len(data)
    if n < 2:
        return 0
    ss = ssdev(data)
    pvar = ss/(n-1) # the sample variance
    return pvar**0.5